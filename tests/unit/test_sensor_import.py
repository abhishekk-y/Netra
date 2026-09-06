import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from sensor.ingest import preserve_evidence, read_logs, read_pcap
from sensor.zeek.log_watcher import ZeekLogWatcher
from demo.traffic_generator import TrafficGenerator


class TestSensorImport(unittest.TestCase):
    def test_pcap_and_pcapng_measured_counts(self):
        from scapy.all import Ether, IP, TCP, ARP, wrpcap
        from scapy.utils import PcapNgWriter
        with tempfile.TemporaryDirectory() as folder:
            first = Ether()/IP(src="10.0.0.1", dst="10.0.0.2")/TCP(sport=43210, dport=443)
            second = first.copy()
            first.time, second.time = 1000.0, 1002.0
            packets = [first, second, Ether()/ARP()]
            pcap, pcapng = Path(folder)/"test.pcap", Path(folder)/"test.pcapng"
            wrpcap(str(pcap), packets)
            with PcapNgWriter(str(pcapng)) as writer:
                for packet in packets:
                    writer.write(packet)
            for path in (pcap, pcapng):
                flows = list(read_pcap(path))
                self.assertEqual(len(flows), 1)
                self.assertEqual(flows[0]["packets"], 2)
                self.assertEqual(flows[0]["bytes"], len(first)*2)
                self.assertEqual(flows[0]["duration"], 2.0)
                self.assertEqual(flows[0]["source"], "pcap-import")

    def test_evidence_idempotent_and_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/"input.pcap"
            source.write_bytes(b"actual sample bytes")
            directory = Path(folder)/"evidence"
            manifest = preserve_evidence(source, directory)
            self.assertEqual(manifest["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(preserve_evidence(source, directory), manifest)
            (directory/manifest["storedName"]).write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError, "corrupt"):
                preserve_evidence(source, directory)

    def test_zeek_tsv_and_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"conn.log"
            path.write_text("#fields\tts\tid.orig_h\tid.resp_h\tid.orig_p\tid.resp_p\tproto\torig_pkts\tresp_pkts\torig_bytes\tresp_bytes\tduration\n1000\t10.0.0.1\t10.0.0.2\t50000\t443\ttcp\t2\t3\t100\t200\t2.5\n")
            flows = list(read_logs(path, "zeek"))
            self.assertEqual(flows[0]["packets"], 5)
            self.assertEqual(flows[0]["bytes"], 300)
            self.assertIn("1970-01-01", flows[0]["timestamp"])
            watcher = ZeekLogWatcher(folder)
            self.assertEqual(watcher._parse_line("conn.log", '{"ts":1000}')["log_type"], "conn")

    def test_suricata_uses_flow_counters_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"eve.json"
            event = {"timestamp":"2026-01-01T00:00:00Z", "src_ip":"10.0.0.1", "dest_ip":"10.0.0.2", "src_port":0, "dest_port":53, "proto":"UDP", "event_type":"flow", "flow":{"pkts_toserver":2,"pkts_toclient":1,"bytes_toserver":100,"bytes_toclient":50,"age":2}}
            path.write_text(json.dumps(event)+"\n"+json.dumps(dict(event,event_type="alert"))+"\n")
            flows = list(read_logs(path, "suricata"))
            self.assertEqual(len(flows), 1)
            self.assertEqual(flows[0]["packets"], 3)
            self.assertEqual(flows[0]["bytes"], 150)

    def test_synthetic_demo_explicit_provenance(self):
        generator = TrafficGenerator()
        for phase in generator.PHASES:
            self.assertTrue(all(flow["source"] == "demo-replay" for flow in generator.generate(phase)))
        self.assertGreaterEqual(len({f["dstPort"] for f in generator.generate("recon")}), 8)
        self.assertGreater(generator.generate("exfiltration")[0]["bytes"], 5*1024*1024)
