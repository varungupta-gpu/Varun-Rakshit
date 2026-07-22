from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent

for path in (PROJECT_ROOT, MODULE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


# Model directory for phase classification
PHASE_MODELS_DIR = MODULE_DIR / "models"

# Model file paths
PHASE_MODEL_PATH = PHASE_MODELS_DIR / "phase_classifier.pkl"
PHASE_LABEL_ENCODER_PATH = PHASE_MODELS_DIR / "phase_label_encoder.pkl"
PHASE_FEATURE_COLUMNS_PATH = PHASE_MODELS_DIR / "phase_feature_columns.pkl"

# Temporal window for prediction
TEMPORAL_WINDOW = 3
SMOOTHING_WINDOW = 5
