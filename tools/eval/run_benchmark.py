from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

from PIL import Image
from sklearn.metrics import roc_auc_score

try:
    from backend.app.inference import ModelRunner
except ImportError as exc:
    raise SystemExit("Run this script from the repository root so backend is importable") from exc


def evaluate_folder(root: Path) -> Tuple[List[float], List[int]]:
    real_dir = root / "real"
    fake_dir = root / "synthetic"
    if not real_dir.exists() or not fake_dir.exists():
        raise FileNotFoundError("Dataset folder must contain 'real' and 'synthetic' subfolders")

    runner = ModelRunner()
    scores: List[float] = []
    labels: List[int] = []

    for label_dir, label in ((real_dir, 0), (fake_dir, 1)):
        for path in label_dir.glob("**/*"):
            if not path.is_file():
                continue
            image = Image.open(path).convert("RGB")
            probability = runner.predict_image(image)
            scores.append(probability)
            labels.append(label)
    return scores, labels


def compute_metrics(scores: List[float], labels: List[int]) -> Dict[str, float]:
    auc = roc_auc_score(labels, scores) if len(set(labels)) == 2 else float("nan")
    threshold = 0.5
    predictions = [1 if score >= threshold else 0 for score in scores]
    accuracy = mean(pred == label for pred, label in zip(predictions, labels)) if scores else 0.0
    return {
        "roc_auc": float(auc),
        "accuracy_at_0.5": float(accuracy),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run detector benchmark on labelled dataset")
    parser.add_argument("--input", type=Path, required=True, help="Path to dataset root")
    parser.add_argument("--output", type=Path, required=True, help="Where to write metrics JSON")
    args = parser.parse_args()

    scores, labels = evaluate_folder(args.input)
    metrics = compute_metrics(scores, labels)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        json.dump({"metrics": metrics, "num_samples": len(scores)}, fh, indent=2)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
