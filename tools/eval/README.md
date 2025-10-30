# Evaluation Toolkit

Use `run_benchmark.py` to evaluate a folder of media assets against the configured detector.

```bash
python run_benchmark.py --input ./dataset --output metrics.json
```

Expected directory layout:

```
dataset/
├── real/
│   ├── example1.jpg
│   └── ...
└── synthetic/
    ├── fake1.png
    └── ...
```

The script aggregates predictions, computes ROC AUC, precision/recall at configurable thresholds, and persists metrics for tracking.
