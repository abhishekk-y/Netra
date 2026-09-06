import threading
import time
import logging
from typing import Callable, Optional
from scapy.all import sniff, wrpcap, Packet
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class PCAPCapture:
    def __init__(self, interface: str, bpf_filter: str = "", storage_path: str = "./evidence/pcap"):
        self.interface = interface
        self.bpf_filter = bpf_filter
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.is_running = False
        self.is_paused = False
        self._capture_thread: Optional[threading.Thread] = None
        self.callbacks = []
        
        self.stats = {
            "packets_captured": 0,
            "bytes_captured": 0,
            "dropped": 0
        }
        
        self._current_pcap_file = None
        self._current_pcap_writer = None
        self._max_pcap_size = 100 * 1024 * 1024 # 100MB
        self._current_pcap_size = 0

    def add_callback(self, callback: Callable[[Packet], None]):
        self.callbacks.append(callback)

    def _rotate_pcap_if_needed(self, packet_len: int):
        if self._current_pcap_size + packet_len > self._max_pcap_size or self._current_pcap_file is None:
            filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
            self._current_pcap_file = self.storage_path / filename
            self._current_pcap_size = 0
            logger.info(f"Rotated PCAP to {self._current_pcap_file}")
            
        self._current_pcap_size += packet_len

    def _packet_handler(self, packet: Packet):
        if not self.is_running:
            return True # stop sniff
            
        if self.is_paused:
            return False

        packet_len = len(packet)
        self.stats["packets_captured"] += 1
        self.stats["bytes_captured"] += packet_len
        
        # Write to PCAP
        try:
            self._rotate_pcap_if_needed(packet_len)
            wrpcap(str(self._current_pcap_file), packet, append=True)
        except Exception as e:
            logger.error(f"Error writing to PCAP: {e}")
            self.stats["dropped"] += 1

        # Process callbacks
        for callback in self.callbacks:
            try:
                callback(packet)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def _sniff_loop(self):
        logger.info(f"Starting capture on {self.interface} with filter '{self.bpf_filter}'")
        try:
            sniff(
                iface=self.interface,
                filter=self.bpf_filter,
                prn=self._packet_handler,
                stop_filter=lambda _: not self.is_running,
                store=False
            )
        except Exception as e:
            logger.error(f"Sniff error: {e}")
        finally:
            self.is_running = False
            logger.info("Capture stopped.")

    def start(self):
        if self.is_running:
            logger.warning("Capture already running")
            return
        self.is_running = True
        self.is_paused = False
        self._capture_thread = threading.Thread(target=self._sniff_loop, daemon=True)
        self._capture_thread.start()

    def stop(self):
        self.is_running = False
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
            
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False
