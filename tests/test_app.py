"""Headless end-to-end test of the Streamlit UI."""
import pytest
from streamlit.testing.v1 import AppTest

from insurepredict import config as cfg

pytestmark = pytest.mark.skipif(not cfg.MODEL_PATH.exists(), reason="run train_model.py first")
APP = str(cfg.ROOT / "app.py")


def fill(at, age=35, gender="Female", bmi=27.5, children=1, smoking="Non-smoker", region="Southeast"):
    at.number_input[0].set_value(age)
    at.selectbox[0].set_value(gender)
    at.number_input[1].set_value(bmi)
    at.number_input[2].set_value(children)
    at.selectbox[1].set_value(smoking)
    at.selectbox[2].set_value(region)


def test_page_loads_with_empty_form():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert len(at.number_input) == 3 and len(at.selectbox) == 3
    assert at.number_input[0].value is None


def test_empty_submit_shows_error():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.button[0].click().run()
    assert not at.exception and at.error and "Please fill in" in at.error[0].value


def test_successful_prediction_shows_result():
    at = AppTest.from_file(APP, default_timeout=60).run()
    fill(at, smoking="Smoker", bmi=33)
    at.button[0].click().run()
    assert not at.exception and not at.error
    assert at.session_state["result"].estimate > 10000
    assert len(at.session_state["history"]) == 1


def test_out_of_range_age_is_rejected():
    at = AppTest.from_file(APP, default_timeout=60).run()
    fill(at, age=10)
    at.button[0].click().run()
    assert at.error and "Age must be between" in at.error[0].value
