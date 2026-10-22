"""Model loading and prediction (kept free of any Streamlit code so it is easy to test)."""
from __future__ import annotations

import json
import logging
import sys
import warnings
from dataclasses import dataclass, field

import joblib
import numpy as np
import pandas as pd
import sklearn

from . import config as cfg
from .validation import PolicyHolder

log = logging.getLogger("insurepredict")


class ModelNotAvailableError(RuntimeError):
    """Raised when the trained model cannot be loaded."""


@dataclass
class Artifacts:
    model: object
    metadata: dict
    version_warning: str | None = None


@dataclass(frozen=True)
class Scenario:
    label: str
    estimate: float


@dataclass(frozen=True)
class PredictionResult:
    person: PolicyHolder
    estimate: float
    low: float
    high: float
    interval_coverage: float
    bmi_category: str
    scenarios: tuple[Scenario, ...] = field(default_factory=tuple)


def load_artifacts() -> Artifacts:
    """Load the trained pipeline and its metadata."""
    # The saved pipeline contains a custom transformer (src/insurance_features.py)
    src_dir = str(cfg.ROOT / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    if not cfg.MODEL_PATH.exists() or not cfg.META_PATH.exists():
        raise ModelNotAvailableError(
            "No trained model found. Run `python train_model.py` once to create it (takes a few seconds).")
    try:
        metadata = json.loads(cfg.META_PATH.read_text())
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = joblib.load(cfg.MODEL_PATH)
    except Exception as exc:  # corrupted file, version mismatch, missing module...
        log.exception("Could not load model")
        raise ModelNotAvailableError(
            "The saved model could not be loaded (often a scikit-learn version mismatch). "
            "Run `python train_model.py` to rebuild it for this environment.") from exc

    version_warning = None
    trained_with = metadata.get("sklearn_version")
    if trained_with and trained_with != sklearn.__version__ or any("version" in str(w.message).lower() for w in caught):
        version_warning = (f"Model was trained with scikit-learn {trained_with}, but {sklearn.__version__} is installed. "
                           "Run `python train_model.py` to rebuild it.")
    return Artifacts(model=model, metadata=metadata, version_warning=version_warning)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Healthy"
    if bmi < 30:
        return "Overweight"
    return "Obesity"


def _predict_one(model, record: dict) -> float:
    value = float(model.predict(pd.DataFrame([record]))[0])
    return max(value, 0.0)


def predict(artifacts: Artifacts, person: PolicyHolder) -> PredictionResult:
    """Estimate charges for one person, with a conformal interval and what-if scenarios."""
    meta = artifacts.metadata
    record = person.to_record()
    estimate = _predict_one(artifacts.model, record)

    half = float(meta.get("interval", {}).get("halfwidth", 0.0))
    low, high = max(0.0, estimate - half), estimate + half

    scenarios = [Scenario("Your profile", estimate)]
    if person.smoker == "yes":
        scenarios.append(Scenario("If non-smoker", _predict_one(artifacts.model, {**record, "smoker": "no"})))
    if person.bmi > cfg.HEALTHY_BMI:
        scenarios.append(Scenario(f"If BMI were {cfg.HEALTHY_BMI}", _predict_one(artifacts.model, {**record, "bmi": cfg.HEALTHY_BMI})))
    if person.smoker == "yes" and person.bmi > cfg.HEALTHY_BMI:
        scenarios.append(Scenario("Both changes", _predict_one(artifacts.model, {**record, "smoker": "no", "bmi": cfg.HEALTHY_BMI})))

    log.info("prediction served (smoker=%s, region=%s)", person.smoker, person.region)  # no personal values logged beyond coarse fields
    return PredictionResult(person=person, estimate=estimate, low=low, high=high,
                            interval_coverage=float(meta.get("interval", {}).get("coverage", 0.9)),
                            bmi_category=bmi_category(person.bmi), scenarios=tuple(scenarios))
