"""
Netra — PCAP Manager
Handles PCAP file indexing, packet extraction, and session reconstruction.
"""
from __future__ import annotations

import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Generator


class PCAPIndex:
    """Index entry for a PCAP file."""

    def __init__(self, filepath: str):
        self.index_id = str(uuid.uuid4())
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.size_bytes: int = 0
        self.packet_count: int = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.protocols: set[str] = set()
        self.src_ips: set[str] = set()
        self.dst_ips: set[str] = set()
        self.community_ids: set[str] = set()
        self.indexed_at = datetime.now(timezone.utc)
        self.sha256: str = ""

        if os.path.exists(filepath):
            self.size_bytes = os.path.getsize(filepath)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_id": self.index_id,
            "filepath": self.filepath,
            "filename": self.filename,
            "size_bytes": self.size_bytes,
            "packet_count": self.packet_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "protocols": sorted(self.protocols),
            "unique_src_ips": len(self.src_ips),
            "unique_dst_ips": len(self.dst_ips),
            "community_ids_count": len(self.community_ids),
            "indexed_at": self.indexed_at.isoformat(),
            "sha256": self.sha256,
        }


class PacketRecord:
    """A decoded packet record for display."""

    def __init__(self):
        self.packet_id: str = ""
        self.timestamp: Optional[datetime] = None
        self.frame_number: int = 0
        self.length: int = 0
        self.src_ip: str = ""
        self.dst_ip: str = ""
        self.src_port: int = 0
        self.dst_port: int = 0
        self.protocol: str = ""
        self.info: str = ""
        self.layers: list[dict[str, Any]] = []
        self.hex_dump: str = ""
        self.ascii_dump: str = ""
        self.community_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "frame_number": self.frame_number,
            "length": self.length,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "info": self.info,
            "layers": self.layers,
            "hex_dump": self.hex_dump[:2000],
            "ascii_dump": self.ascii_dump[:1000],
            "community_id": self.community_id,
        }


class PCAPManager:
    """Manages PCAP file indexing, search, and packet extraction."""

    def __init__(self, pcap_dir: str = "evidence/pcap"):
        self.pcap_dir = Path(pcap_dir)
        self._indexes: dict[str, PCAPIndex] = {}
        self._file_index: dict[str, str] = {}

    def index_file(self, filepath: str) -> PCAPIndex:
        idx = PCAPIndex(filepath)
        try:
            from scapy.all import PcapReader
            reader = PcapReader(filepath)
            count = 0
            protocols: set[str] = set()
            src_ips: set[str] = set()
            dst_ips: set[str] = set()
            first_time = None
            last_time = None

            for pkt in reader:
                count += 1
                if count > 100000:
                    break
                if hasattr(pkt, 'time'):
                    pkt_time = datetime.fromtimestamp(float(pkt.time), tz=timezone.utc)
                    if first_time is None:
                        first_time = pkt_time
                    last_time = pkt_time
                if pkt.haslayer('IP'):
                    ip = pkt['IP']
                    src_ips.add(ip.src)
                    dst_ips.add(ip.dst)
                    if pkt.haslayer('TCP'):
                        protocols.add('TCP')
                    elif pkt.haslayer('UDP'):
                        protocols.add('UDP')
                    elif pkt.haslayer('ICMP'):
                        protocols.add('ICMP')
                elif pkt.haslayer('ARP'):
                    protocols.add('ARP')
                elif pkt.haslayer('IPv6'):
                    protocols.add('IPv6')

            reader.close()
            idx.packet_count = count
            idx.protocols = protocols
            idx.src_ips = src_ips
            idx.dst_ips = dst_ips
            idx.start_time = first_time
            idx.end_time = last_time
        except ImportError:
            idx.packet_count = -1
        except Exception as e:
            idx.packet_count = -1

        self._indexes[idx.index_id] = idx
        self._file_index[filepath] = idx.index_id
        return idx

    def scan_directory(self) -> list[PCAPIndex]:
        results = []
        for ext in ("*.pcap", "*.pcapng"):
            for f in self.pcap_dir.rglob(ext):
                filepath = str(f)
                if filepath not in self._file_index:
                    idx = self.index_file(filepath)
                    results.append(idx)
        return results

    def search_packets(
        self,
        filepath: Optional[str] = None,
        src_ip: Optional[str] = None,
        dst_ip: Optional[str] = None,
        protocol: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        if not filepath:
            return []
        try:
            from scapy.all import PcapReader
        except ImportError:
            return [{"error": "scapy not installed"}]

        results: list[dict] = []
        try:
            reader = PcapReader(filepath)
            frame = 0
            for pkt in reader:
                frame += 1
                if len(results) >= limit:
                    break
                if not pkt.haslayer('IP'):
                    continue
                ip = pkt['IP']
                if src_ip and ip.src != src_ip:
                    continue
                if dst_ip and ip.dst != dst_ip:
                    continue
                proto = "OTHER"
                src_port = 0
                dst_port = 0
                info = ""
                if pkt.haslayer('TCP'):
                    proto = "TCP"
                    tcp = pkt['TCP']
                    src_port = tcp.sport
                    dst_port = tcp.dport
                    flags = str(tcp.flags)
                    info = f"TCP {src_port} -> {dst_port} [{flags}]"
                elif pkt.haslayer('UDP'):
                    proto = "UDP"
                    udp = pkt['UDP']
                    src_port = udp.sport
                    dst_port = udp.dport
                    info = f"UDP {src_port} -> {dst_port}"
                elif pkt.haslayer('ICMP'):
                    proto = "ICMP"
                    info = f"ICMP {pkt['ICMP'].type}/{pkt['ICMP'].code}"

                if protocol and proto.upper() != protocol.upper():
                    continue

                record = {
                    "frame_number": frame,
                    "timestamp": datetime.fromtimestamp(float(pkt.time), tz=timezone.utc).isoformat(),
                    "length": len(pkt),
                    "src_ip": ip.src,
                    "dst_ip": ip.dst,
                    "src_port": src_port,
                    "dst_port": dst_port,
                    "protocol": proto,
                    "info": info,
                }
                results.append(record)
            reader.close()
        except Exception:
            pass
        return results

    def decode_packet(self, filepath: str, frame_number: int) -> dict[str, Any]:
        try:
            from scapy.all import PcapReader
        except ImportError:
            return {"error": "scapy not installed"}

        try:
            reader = PcapReader(filepath)
            frame = 0
            for pkt in reader:
                frame += 1
                if frame == frame_number:
                    reader.close()
                    layers = []
                    layer = pkt
                    while layer:
                        layer_info = {
                            "name": layer.__class__.__name__,
                            "fields": {},
                        }
                        for field in layer.fields_desc:
                            try:
                                val = getattr(layer, field.name, None)
                                layer_info["fields"][field.name] = str(val) if val is not None else ""
                            except Exception:
                                pass
                        layers.append(layer_info)
                        layer = layer.payload if hasattr(layer, 'payload') and layer.payload else None
                        if layer and layer.__class__.__name__ == "NoPayload":
                            break

                    raw_bytes = bytes(pkt)
                    hex_dump = raw_bytes.hex()
                    ascii_dump = "".join(chr(b) if 32 <= b < 127 else "." for b in raw_bytes)

                    return {
                        "frame_number": frame_number,
                        "length": len(pkt),
                        "layers": layers,
                        "hex_dump": hex_dump,
                        "ascii_dump": ascii_dump,
                    }
            reader.close()
        except Exception as e:
            return {"error": str(e)}
        return {"error": "Frame not found"}

    def get_indexes(self) -> list[dict]:
        return [idx.to_dict() for idx in self._indexes.values()]

    def get_stats(self) -> dict[str, Any]:
        return {
            "indexed_files": len(self._indexes),
            "total_packets_indexed": sum(i.packet_count for i in self._indexes.values() if i.packet_count > 0),
        }
