"""Compute classifier metrics from supplied predictions; never emit sample scores."""
import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import precision_recall_fscore_support


class Evaluator:
    def evaluate_classifier(self, y_true, y_pred, y_prob):
        y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
        y_prob = np.asarray(y_prob, dtype=float)
        if y_prob.ndim != 2 or not len(y_true) or len(y_true) != len(y_prob) or len(y_pred) != len(y_true):
            raise ValueError("Expected matching nonempty labels and an N x classes probability matrix")
        if not np.issubdtype(y_true.dtype, np.integer) or np.any(y_true < 0) or np.any(y_true >= y_prob.shape[1]):
            raise ValueError("y_true must contain zero-based class indices matching probability columns")
        if not np.isfinite(y_prob).all() or np.any(y_prob < 0) or np.any(y_prob > 1) or not np.allclose(y_prob.sum(axis=1), 1):
            raise ValueError("Probabilities must be finite, in [0,1], and sum to one per row")
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
        # Multiclass Brier score sums squared error over classes, then averages samples.
        brier = np.mean(np.sum((y_prob - np.eye(y_prob.shape[1])[y_true]) ** 2, axis=1))
        return {"precision": float(precision), "recall": float(recall), "f1": float(f1),
                "brier_score": float(brier), "samples": len(y_true)}


def main():
    parser = argparse.ArgumentParser(description="Evaluate an NPZ containing y_true, y_pred, y_prob")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", default="eval_report.json")
    args = parser.parse_args()
    with np.load(args.predictions, allow_pickle=False) as data:
        report = Evaluator().evaluate_classifier(data["y_true"], data["y_pred"], data["y_prob"])
    report["predictions_file"] = str(Path(args.predictions))
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
