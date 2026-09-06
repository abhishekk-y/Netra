import unittest
from backend.app.services.topology.device_classifier import DeviceClassifier


class TestDeviceClassifier(unittest.TestCase):
    def test_unknown_has_no_fabricated_evidence(self):
        label, confidence, evidence = DeviceClassifier().classify({})
        self.assertEqual(label, "Unknown")
        self.assertLess(confidence, .2)
        self.assertEqual(evidence, [])

    def test_observed_switch_protocols(self):
        label, confidence, evidence = DeviceClassifier().classify({"device_type": ["Switch"]})
        self.assertEqual(label, "Switch")
        self.assertGreaterEqual(confidence, .8)
        self.assertTrue(any("LLDP" in item for item in evidence))

    def test_server_ports_support_server(self):
        label, confidence, evidence = DeviceClassifier().classify({"open_ports": [443]})
        self.assertEqual(label, "Server")
        self.assertTrue(evidence)
