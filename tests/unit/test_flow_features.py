import math
import unittest
from ml.features.flow_features import FlowFeatureExtractor
from ml.features.host_features import HostFeatureExtractor


class TestFlowFeatures(unittest.TestCase):
    def test_rates_and_direction(self):
        features = FlowFeatureExtractor().extract(dict(duration_ms=2000, fwd_packets=3,
            bwd_packets=1, fwd_bytes=300, bwd_bytes=100, protocol="TCP", dst_port=443))
        self.assertEqual(features["packets_per_second"], 2)
        self.assertEqual(features["bytes_per_second"], 200)
        self.assertEqual(features["packet_ratio"], .75)
        self.assertEqual(features["is_tcp"], 1)

    def test_zero_duration_and_nonfinite_are_finite(self):
        features = FlowFeatureExtractor().extract({"duration_ms": 0, "fwd_bytes": float("inf")})
        self.assertTrue(all(math.isfinite(value) for value in features.values()))
        self.assertEqual(features["bytes_per_second"], 0)

    def test_payload_entropy_uses_payload_not_packet_sizes(self):
        features = FlowFeatureExtractor().extract({"fwd_pkt_lens": [10, 20], "payload_bytes": [1, 1]})
        self.assertEqual(features["packet_length_entropy"], 1)
        self.assertEqual(features["payload_byte_entropy"], 0)

    def test_host_excludes_unrelated_traffic_and_missing_ports(self):
        flows = [{"src_ip": "a", "dst_ip": "b", "timestamp": 0, "fwd_bytes": 100, "fwd_packets": 2},
                 {"src_ip": "x", "dst_ip": "y", "timestamp": 1000, "fwd_bytes": 9999}]
        features = HostFeatureExtractor().extract("a", flows)
        self.assertEqual(features["total_bytes_sent"], 100)
        self.assertEqual(features["connections_per_second"], 1)
        self.assertEqual(features["avg_packet_size"], 50)
