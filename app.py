"""InsurePredict - Streamlit front end for the insurance cost model."""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

import sklearn
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from insurepredict import config as cfg  # noqa: E402
from insurepredict import ui  # noqa: E402
from insurepredict.predictor import ModelNotAvailableError, load_artifacts, predict  # noqa: E402
from insurepredict.validation import validate_inputs  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("insurepredict")

st.set_page_config(page_title=f"{cfg.APP_NAME} | Insurance Price Prediction", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="collapsed")


def _model_needs_rebuild() -> bool:
    """Return True if the model is missing or was built with a different sklearn version."""
    if not cfg.MODEL_PATH.exists() or not cfg.META_PATH.exists():
        return True
    try:
        meta = json.loads(cfg.META_PATH.read_text())
        return meta.get("sklearn_version") != sklearn.__version__
    except Exception:
        return True


def _auto_train() -> None:
    """Re-train the model in-process when the environment doesn't match the saved artefact."""
    log.info("Auto-training model for sklearn %s …", sklearn.__version__)
    train_script = ROOT / "train_model.py"
    result = subprocess.run(
        [sys.executable, str(train_script)],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    if result.returncode != 0:
        log.error("Auto-train failed:\n%s", result.stderr)
        raise ModelNotAvailableError(
            "Could not auto-train the model on startup. "
            f"Details: {result.stderr[-500:] if result.stderr else 'unknown error'}"
        )
    log.info("Auto-train complete:\n%s", result.stdout)


@st.cache_resource(show_spinner="Setting up model — this takes about 10 seconds on first launch…")
def get_artifacts():
    if _model_needs_rebuild():
        _auto_train()
    return load_artifacts()


def main() -> None:
    ui.inject_css()
    ui.render_topbar()

    try:
        artifacts = get_artifacts()
    except ModelNotAvailableError as exc:
        st.error(str(exc))
        st.stop()

    ranges = {k: tuple(v) for k, v in artifacts.metadata.get("training_ranges", {}).items()}
    left, right = st.columns([1.12, 1], gap="large")

    # ---------------- right column: the form ----------------
    with right:
        with st.form("premium_form", clear_on_submit=False):
            ui.render_form_header()
            age = st.number_input("Age *", value=None, min_value=0, max_value=120, step=1, placeholder="Enter your age")
            gender = st.selectbox("Gender *", cfg.GENDERS, index=None, placeholder="Select gender")
            bmi = st.number_input("BMI (Body Mass Index) *", value=None, min_value=0.0, max_value=100.0, step=0.1,
                                  format="%.1f", placeholder="Enter your BMI",
                                  help="BMI = weight in kg divided by height in metres squared. 18.5-24.9 is considered healthy.")
            children = st.number_input("Number of Children *", value=None, min_value=0, max_value=50, step=1,
                                       placeholder="Number of children")
            smoking = st.selectbox("Smoking Status *", cfg.SMOKING, index=None, placeholder="Select smoking status")
            region = st.selectbox("Region *", cfg.REGIONS, index=None, placeholder="Select region")
            submitted = st.form_submit_button("Calculate Premium")

        if submitted:
            check = validate_inputs({"age": age, "gender": gender, "bmi": bmi, "children": children,
                                     "smoking": smoking, "region": region}, ranges)
            if not check.ok:
                st.session_state["result"] = None
                for message in check.errors:
                    st.error(message)
            else:
                for message in check.warnings:
                    st.warning(message)
                try:
                    result = predict(artifacts, check.person)
                except Exception:  # never show a stack trace to the end user
                    logging.getLogger("insurepredict").exception("Prediction failed")
                    st.error("Something went wrong while calculating the estimate. Please try again.")
                else:
                    st.session_state["result"] = result
                    ui.record_history(result)

    # ---------------- left column: hero or results ----------------
    with left:
        result = st.session_state.get("result")
        if result is None:
            ui.render_hero()
        else:
            ui.render_results(result, artifacts.metadata)
            if st.button("← Back to overview"):
                st.session_state["result"] = None
                st.rerun()
            ui.render_history()

    ui.render_model_card(artifacts.metadata, artifacts.version_warning)
    ui.render_footer()


main()
