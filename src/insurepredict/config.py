"""Central configuration for InsurePredict."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "best_model.joblib"
META_PATH = MODEL_DIR / "model_metadata.json"
DATA_PATH = ROOT / "data" / "insurance.csv"

APP_NAME = "InsurePredict"
CURRENCY = "$"

GENDERS = ["Female", "Male"]
SMOKING = ["Non-smoker", "Smoker"]
REGIONS = ["Northeast", "Northwest", "Southeast", "Southwest"]

# Hard limits: inputs outside these are rejected.
AGE_LIMITS = (18, 100)
BMI_LIMITS = (10.0, 70.0)
CHILDREN_LIMITS = (0, 10)

# Fallback "training range" used only if the metadata file lacks it.
DEFAULT_TRAINING_RANGES = {"age": (18, 64), "bmi": (15.9, 53.2), "children": (0, 5)}

HISTORY_LIMIT = 10
HEALTHY_BMI = 24.9
