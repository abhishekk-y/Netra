"""Regression checks for measured capture parsing, provenance and model honesty."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
import uuid

from sensor.ingest import read_pcap, read_packet_summaries, packet_summaries, preserve_evidence, read_logs
from sensor.cli import submit


@contextmanager
def workspace_temp():
    # Ordinary inherited permissions also work in the Windows desktop sandbox.
    parent = Path(__file__).resolve().parent
    directory = parent / (".sensor-test-" + uuid.uuid4().hex)
    directory.mkdir()
    try:
        yield directory
    finally:
        if directory.resolve().parent != parent or not directory.name.startswith(".sensor-test-"):
            raise RuntimeError("Unexpected test cleanup path")
        shutil.rmtree(directory)


class TestSensorPipeline(unittest.TestCase):
    def test_packet_details_are_real_bytes_including_arp_and_truncation(self):
        from scapy.all import Ether, IP, TCP, Raw, ARP, wrpcap
        with workspace_temp() as folder:
            ethernet = Ether(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
            packets = [ethernet/IP(src="10.0.0.1", dst="10.0.0.2")/TCP(sport=50000, dport=443)/Raw(b"HELLO"),
                       ethernet/ARP(psrc="10.0.0.1", pdst="10.0.0.2"),
                       ethernet/IP(src="10.0.0.1", dst="10.0.0.2")/TCP()/Raw(b"X"*3000)]
            for i, packet in enumerate(packets):
                packet.time = 1000 + i
            path = folder/"sample.pcap"
            wrpcap(str(path), packets)
            rows = list(read_packet_summaries(path))
            self.assertEqual([row["index"] for row in rows], [1, 2, 3])
            self.assertEqual(rows[0]["rawHex"], bytes(packets[0]).hex())
            self.assertTrue(rows[0]["ascii"].endswith("HELLO"))
            self.assertEqual(rows[1]["protocol"], "ARP")
            self.assertEqual(rows[1]["srcIp"], "10.0.0.1")
            self.assertEqual(len(rows[2]["rawHex"]), 4096)
            self.assertTrue(rows[2]["truncated"])
            self.assertTrue(rows[0]["communityId"].startswith("1:"))
            self.assertTrue(any(layer["name"] == "IP" for layer in rows[0]["layers"]))
            self.assertTrue(all(isinstance(v,str) and len(v) <= 256 for row in rows for layer in row["layers"] for v in layer["fields"].values()))
            json.dumps(rows, allow_nan=False)
            self.assertEqual(packet_summaries(path, 1, 1)[0]["index"], 2)

    def test_pcapng_aggregates_measured_counts(self):
        from scapy.all import Ether, IP, UDP
        from scapy.utils import PcapNgWriter
        with workspace_temp() as folder:
            first = Ether(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")/IP(src="10.0.0.1", dst="10.0.0.2")/UDP(sport=53000,dport=53)
            second = first.copy()
            first.time, second.time = 1000, 1002
            path = folder/"sample.pcapng"
            with PcapNgWriter(str(path)) as stream:
                stream.write(first)
                stream.write(second)
            flows = list(read_pcap(path))
            self.assertEqual(len(flows), 1)
            self.assertEqual(flows[0]["packets"], 2)
            self.assertEqual(flows[0]["bytes"], len(first)*2)
            self.assertEqual(flows[0]["duration"], 2)
            self.assertEqual(flows[0]["rawSource"], "pcap")

    def test_manifest_does_not_trust_modified_reference(self):
        with workspace_temp() as folder:
            path = folder/"sample.pcap"
            path.write_bytes(b"evidence fixture")
            store = folder/"evidence"
            manifest = preserve_evidence(path, store)
            self.assertEqual(preserve_evidence(path, store), manifest)
            manifest_file = store/(manifest["sha256"]+".json")
            manifest["storedName"] = "../../other-file"
            manifest_file.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "manifest"):
                preserve_evidence(path, store)

    def test_zeek_preserves_timestamp_and_session(self):
        with workspace_temp() as folder:
            path = folder/"conn.log"
            path.write_text(json.dumps({"ts":1000, "uid":"C123", "id.orig_h":"10.0.0.1", "id.resp_h":"10.0.0.2", "id.orig_p":50000, "id.resp_p":443, "proto":"tcp", "orig_pkts":2,"resp_pkts":1,"orig_bytes":80,"resp_bytes":40,"duration":1.5})+"\n")
            flow = list(read_logs(path,"zeek"))[0]
            self.assertEqual(flow["sessionUid"], "C123")
            self.assertEqual(flow["bytes"], 120)
            self.assertEqual(flow["packets"], 3)
            self.assertEqual(flow["timestamp"], "1970-01-01T00:16:40+00:00")

    def test_cli_uses_canonical_api_path(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'{"accepted":1}'
        with patch("sensor.cli.urlopen", return_value=Response()) as opened:
            self.assertEqual(submit("http://localhost:8000/", [{"source":"pcap-import"}]), {"accepted":1})
            request = opened.call_args.args[0]
            self.assertEqual(request.full_url, "http://localhost:8000/api/v1/ingest/flows")
            self.assertEqual(json.loads(request.data), {"flows":[{"source":"pcap-import"}]})

    def test_no_artifact_has_no_fabricated_risk(self):
        from ml.inference.engine import InferenceEngine
        from ml.inference.pipeline import InferencePipeline
        result = InferencePipeline(InferenceEngine()).process_single_event({})
        self.assertEqual(result["model_status"], "unavailable")
        self.assertIsNone(result["confidence"])
        self.assertIsNone(result["anomaly_score"])

    def test_artifact_feature_order_and_independent_load_failure(self):
        import numpy as np
        from ml.models.anomaly import AnomalyDetector
        from ml.inference.engine import InferenceEngine
        with workspace_temp() as folder:
            model = AnomalyDetector()
            model.fit(np.array([[100,2], [120,3], [150,4], [180,4], [200,5]]), ["total_bytes", "total_packets"])
            path = folder/"anomaly.pkl"
            model.save(path)
            engine = InferenceEngine({"classifier": str(folder/"missing.pkl"), "anomaly": str(path)})
            result = engine.infer_flow({"total_packets": 3, "total_bytes": 120, "unused": 99})
            self.assertAlmostEqual(result["anomaly_score"], model.score_samples(np.array([[120,3]]))[0])
            self.assertEqual(result["model_status"], "partial")
            self.assertIn("classifier", result["errors"])

    def test_synthetic_training_requires_explicit_opt_in_and_does_not_overwrite(self):
        from ml.training.train_ensemble import train, extract_features
        with self.assertRaisesRegex(ValueError, "exactly one"):
            train()
        with workspace_temp() as folder:
            artifact = folder/"existing.pkl"
            artifact.write_bytes(b"existing user model")
            with self.assertRaises(FileExistsError):
                train(synthetic=True, output=artifact)
            self.assertEqual(artifact.read_bytes(), b"existing user model")
        features = extract_features({"duration":0,"packets":0,"bytes":0})
        self.assertEqual(features[0], 0)
        self.assertEqual(features[7], 0)
        self.assertEqual(features[9], 0)


if __name__ == "__main__":
    unittest.main()
