import unittest
from sensor.normalizer.event_normalizer import EventNormalizer

class TestNormalizer(unittest.TestCase):
    def setUp(self):
        self.normalizer = EventNormalizer("sensor-123")

    def test_suricata_normalization(self):
        raw_event = {
            "timestamp": "2026-09-07T03:00:00.000000+0530",
            "event_type": "alert",
            "src_ip": "192.168.1.5",
            "dest_ip": "10.0.0.5",
            "src_port": 4444,
            "dest_port": 80,
            "proto": "TCP"
        }
        normalized = self.normalizer.normalize_suricata(raw_event)
        self.assertIsNotNone(normalized)
        self.assertEqual(normalized.source_ip, "192.168.1.5")
        self.assertEqual(normalized.event_type, "suricata_alert")
        
    def test_zeek_normalization(self):
        raw_event = {
            "log_type": "conn",
            "id.orig_h": "192.168.1.5",
            "id.resp_h": "10.0.0.5",
            "id.orig_p": "4444",
            "id.resp_p": "80",
            "proto": "tcp"
        }
        normalized = self.normalizer.normalize_zeek(raw_event)
        self.assertIsNotNone(normalized)
        self.assertEqual(normalized.source_ip, "192.168.1.5")
        self.assertEqual(normalized.event_type, "zeek_conn")

    def test_zeek_timestamp_and_zero_port_preserved(self):
        result = self.normalizer.normalize_zeek({"ts": "1000.25", "proto": "udp", "id.orig_h": "10.0.0.1", "id.resp_h": "10.0.0.2", "id.orig_p": "0", "id.resp_p": "53"})
        self.assertEqual(result.timestamp.timestamp(), 1000.25)
        self.assertEqual(result.source_port, 0)
        self.assertTrue(result.community_id.startswith("1:"))

    def test_invalid_input_rejected(self):
        self.assertIsNone(self.normalizer.normalize_suricata({"src_ip": "not-an-ip"}))
        self.assertIsNone(self.normalizer.normalize_zeek({"id.orig_p": "65536"}))

if __name__ == '__main__':
    unittest.main()
