"""Input validation: turns raw form values into a clean, typed record."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from . import config as cfg


@dataclass(frozen=True)
class PolicyHolder:
    age: int
    sex: str        # "female" / "male"
    bmi: float
    children: int
    smoker: str     # "yes" / "no"
    region: str     # "northeast" ...

    def to_record(self) -> dict:
        return {"age": self.age, "sex": self.sex, "bmi": self.bmi,
                "children": self.children, "smoker": self.smoker, "region": self.region}


@dataclass(frozen=True)
class ValidationResult:
    person: PolicyHolder | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.person is not None and not self.errors


def _is_missing(v: Any) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def validate_inputs(raw: Mapping[str, Any], training_ranges: Mapping[str, tuple] | None = None) -> ValidationResult:
    """Validate raw form values. Returns errors (blocking) and warnings (non-blocking)."""
    ranges = {**cfg.DEFAULT_TRAINING_RANGES, **(training_ranges or {})}
    errors: list[str] = []
    warnings: list[str] = []

    # ---- required fields -------------------------------------------------
    labels = {"age": "Age", "gender": "Gender", "bmi": "BMI", "children": "Number of children",
              "smoking": "Smoking status", "region": "Region"}
    missing = [labels[k] for k in labels if _is_missing(raw.get(k))]
    if missing:
        errors.append("Please fill in: " + ", ".join(missing) + ".")

    # ---- numeric checks --------------------------------------------------
    age = bmi = children = None
    if not _is_missing(raw.get("age")):
        try:
            age_f = float(raw["age"])
            if age_f != int(age_f):
                errors.append("Age must be a whole number.")
            elif not cfg.AGE_LIMITS[0] <= age_f <= cfg.AGE_LIMITS[1]:
                errors.append(f"Age must be between {cfg.AGE_LIMITS[0]} and {cfg.AGE_LIMITS[1]}.")
            else:
                age = int(age_f)
        except (TypeError, ValueError):
            errors.append("Age must be a number.")

    if not _is_missing(raw.get("bmi")):
        try:
            bmi_f = float(raw["bmi"])
            if not cfg.BMI_LIMITS[0] <= bmi_f <= cfg.BMI_LIMITS[1]:
                errors.append(f"BMI must be between {cfg.BMI_LIMITS[0]:.0f} and {cfg.BMI_LIMITS[1]:.0f}.")
            else:
                bmi = round(bmi_f, 1)
        except (TypeError, ValueError):
            errors.append("BMI must be a number.")

    if not _is_missing(raw.get("children")):
        try:
            ch_f = float(raw["children"])
            if ch_f != int(ch_f):
                errors.append("Number of children must be a whole number.")
            elif not cfg.CHILDREN_LIMITS[0] <= ch_f <= cfg.CHILDREN_LIMITS[1]:
                errors.append(f"Number of children must be between {cfg.CHILDREN_LIMITS[0]} and {cfg.CHILDREN_LIMITS[1]}.")
            else:
                children = int(ch_f)
        except (TypeError, ValueError):
            errors.append("Number of children must be a number.")

    # ---- categorical checks ----------------------------------------------
    sex = smoker = region = None
    if not _is_missing(raw.get("gender")):
        if raw["gender"] in cfg.GENDERS:
            sex = raw["gender"].lower()
        else:
            errors.append("Please choose a valid gender.")
    if not _is_missing(raw.get("smoking")):
        if raw["smoking"] in cfg.SMOKING:
            smoker = "yes" if raw["smoking"] == "Smoker" else "no"
        else:
            errors.append("Please choose a valid smoking status.")
    if not _is_missing(raw.get("region")):
        if raw["region"] in cfg.REGIONS:
            region = raw["region"].lower()
        else:
            errors.append("Please choose a valid region.")

    if errors or None in (age, bmi, children, sex, smoker, region):
        return ValidationResult(None, tuple(errors), ())

    # ---- extrapolation warnings (non-blocking) ---------------------------
    lo, hi = ranges["age"]
    if not lo <= age <= hi:
        warnings.append(f"Age {age} is outside the range the model was trained on ({lo}-{hi}); treat the estimate with extra caution.")
    lo, hi = ranges["bmi"]
    if not lo <= bmi <= hi:
        warnings.append(f"BMI {bmi} is outside the range the model was trained on ({lo:.1f}-{hi:.1f}); treat the estimate with extra caution.")
    lo, hi = ranges["children"]
    if not lo <= children <= hi:
        warnings.append(f"{children} children is outside the range the model was trained on ({lo}-{hi}); treat the estimate with extra caution.")

    return ValidationResult(PolicyHolder(age, sex, bmi, children, smoker, region), (), tuple(warnings))
