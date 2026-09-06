import tempfile
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from ml.datasets.quality import DatasetQualityAnalyzer
from ml.inference.engine import InferenceEngine
from ml.inference.pipeline import InferencePipeline
from ml.models.anomaly import AnomalyDetector
from ml.training.evaluate import Evaluator


class TestMLPipeline(unittest.TestCase):
    def test_unavailable_model_is_not_zero_risk(self):
        result = InferencePipeline(InferenceEngine()).process_single_event({})
        self.assertEqual(result["model_status"], "unavailable")
        self.assertIsNone(result["anomaly_score"])
        self.assertIsNone(result["confidence"])

    def test_independent_load_and_training_feature_order(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/"anomaly.pkl")
            model = AnomalyDetector()
            model.fit(np.array([[100,2], [120,3], [150,4], [180,4], [200,5]]), ["total_bytes", "total_packets"])
            model.save(path)
            engine = InferenceEngine({"classifier": str(Path(folder)/"missing.pkl"), "anomaly": path})
            result = engine.infer_flow({"total_packets": 3, "total_bytes": 120, "unused": 99})
            expected = model.score_samples(np.array([[120,3]]))[0]
            self.assertAlmostEqual(result["anomaly_score"], expected)
            self.assertEqual(result["model_status"], "partial")
            self.assertIn("classifier", result["errors"])

    def test_missing_features_reported(self):
        engine = InferenceEngine()
        model = AnomalyDetector()
        model.feature_names = ["absent_feature"]
        engine.models["anomaly"] = model
        result = engine.infer_flow({"other": 1})
        self.assertEqual(result["model_status"], "unavailable")
        self.assertIn("absent_feature", result["errors"]["anomaly"])

    def test_temporal_split_keeps_equal_timestamps_together(self):
        data = pd.DataFrame({"timestamp": [1,2,3,3,3,4], "label": [0,0,1,1,1,0]})
        train, test = DatasetQualityAnalyzer().temporal_split(data, "timestamp", .4)
        self.assertLess(train.timestamp.max(), test.timestamp.min())
        with self.assertRaises(ValueError):
            DatasetQualityAnalyzer().temporal_split(pd.DataFrame({"timestamp":[1,1]}), "timestamp")

    def test_evaluation_uses_supplied_predictions(self):
        metrics = Evaluator().evaluate_classifier([0,1], [0,1], [[.8,.2],[.1,.9]])
        self.assertEqual(metrics["f1"], 1)
        self.assertAlmostEqual(metrics["brier_score"], .05)
        with self.assertRaises(ValueError):
            Evaluator().evaluate_classifier([0], [0], [[.8,.8]])
