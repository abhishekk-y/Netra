import unittest
from sensor.normalizer.event_normalizer import EventNormalizer

class TestCommunityID(unittest.TestCase):
    def test_community_id_calculation(self):
        # Flow direction does not affect the identifier.
        id1 = EventNormalizer.calculate_community_id("192.168.1.1", "10.0.0.1", 12345, 80, "tcp")
        id2 = EventNormalizer.calculate_community_id("10.0.0.1", "192.168.1.1", 80, 12345, "tcp")
        self.assertEqual(id1, id2)
        
    def test_different_protocols(self):
        id1 = EventNormalizer.calculate_community_id("192.168.1.1", "10.0.0.1", 12345, 80, "tcp")
        id2 = EventNormalizer.calculate_community_id("192.168.1.1", "10.0.0.1", 12345, 80, "udp")
        self.assertNotEqual(id1, id2)

    def test_network_byte_order_known_digest(self):
        # Seed + packed IPs + protocol/padding + packed ports, per v1 spec.
        import hashlib, base64
        wire = bytes.fromhex("00000a0000017f000001060004d20050")
        expected = "1:" + base64.b64encode(hashlib.sha1(wire).digest()).decode()
        self.assertEqual(EventNormalizer.calculate_community_id("10.0.0.1", "127.0.0.1", 1234, 80, "TCP"), expected)

    def test_ipv6_and_unsupported_protocol(self):
        one = EventNormalizer.calculate_community_id("2001:db8::1", "2001:db8::2", 50000, 443, "tcp")
        two = EventNormalizer.calculate_community_id("2001:db8::2", "2001:db8::1", 443, 50000, "tcp")
        self.assertEqual(one, two)
        self.assertTrue(one.startswith("1:"))
        self.assertEqual(EventNormalizer.calculate_community_id("10.0.0.1", "10.0.0.2", 0, 0, "icmp"), "")

if __name__ == '__main__':
    unittest.main()
