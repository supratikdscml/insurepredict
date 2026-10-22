import math

import pytest

from insurepredict import config as cfg
from insurepredict.predictor import bmi_category, load_artifacts, predict
from insurepredict.validation import validate_inputs

pytestmark = pytest.mark.skipif(not cfg.MODEL_PATH.exists(), reason="run train_model.py first")


@pytest.fixture(scope="module")
def artifacts():
    return load_artifacts()


def person(**kw):
    raw = {"age": 35, "gender": "Female", "bmi": 27.5, "children": 1, "smoking": "Non-smoker", "region": "Southeast", **kw}
    return validate_inputs(raw).person


def test_prediction_is_positive_finite_and_inside_interval(artifacts):
    r = predict(artifacts, person())
    assert math.isfinite(r.estimate) and r.estimate > 0
    assert 0 <= r.low <= r.estimate <= r.high


def test_smoker_costs_more_than_non_smoker(artifacts):
    assert predict(artifacts, person(smoking="Smoker")).estimate > predict(artifacts, person()).estimate * 2


def test_what_if_scenarios(artifacts):
    labels = [s.label for s in predict(artifacts, person(smoking="Smoker", bmi=34)).scenarios]
    assert labels[0] == "Your profile" and "If non-smoker" in labels and "Both changes" in labels
    assert len(predict(artifacts, person(bmi=22)).scenarios) == 1      # nothing to compare for a healthy non-smoker


@pytest.mark.parametrize("bmi,cat", [(17, "Underweight"), (22, "Healthy"), (27, "Overweight"), (31, "Obesity")])
def test_bmi_category(bmi, cat):
    assert bmi_category(bmi) == cat
