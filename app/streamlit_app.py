import joblib
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Medical Insurance Cost Prediction", page_icon="📊")
st.title("Medical Insurance Cost Prediction")
st.caption("Educational machine-learning demonstration.")
st.warning(
    "This is not medical advice or an actual insurance quote. Historical data may contain bias; "
    "do not use this model for consequential decisions about individuals."
)

root = Path(__file__).resolve().parents[1]
model_path = root / "models" / "best_model.joblib"
if not model_path.exists():
    st.error("Trained model not found. Run the Jupyter notebook first.")
    st.stop()

model = joblib.load(model_path)
with st.form("insurance_form"):
    age = st.slider("Age", 18, 100, 35)
    sex = st.selectbox("Sex", ["female", "male"])
    bmi = st.number_input("BMI", min_value=10.0, max_value=80.0, value=27.5, step=0.1)
    children = st.number_input("Number of children", min_value=0, max_value=10, value=1, step=1)
    smoker = st.selectbox("Smoking status", ["no", "yes"])
    region = st.selectbox("Region", ["northeast", "northwest", "southeast", "southwest"])
    submitted = st.form_submit_button("Estimate charges")

if submitted:
    sample = pd.DataFrame([{
        "age": age, "sex": sex, "bmi": bmi,
        "children": int(children), "smoker": smoker, "region": region
    }])
    prediction = float(model.predict(sample)[0])
    st.metric("Estimated charges", f"{prediction:,.2f}")
    st.caption("Shown in the units/currency used by the source dataset.")
