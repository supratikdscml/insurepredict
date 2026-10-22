# InsurePredict

A Streamlit app that estimates annual medical insurance charges from age, gender, BMI, number of children,
smoking status and region. It serves the model from the *Medical Insurance Cost Prediction* project:
Lasso regression with engineered features (smoker x BMI, smoker x age, obesity flag, ...).

## Quick start

```bash
pip install -r requirements.txt
python train_model.py        # builds models/best_model.joblib for YOUR scikit-learn version (seconds)
streamlit run app.py
```

Run the tests with `python -m pytest -q`.

With Docker: `docker build -t insurepredict . && docker run -p 8501:8501 insurepredict`

## Project layout

```
app.py                      Streamlit entry point (layout and wiring only)
train_model.py              Re-creates the model, metadata and conformal interval from data/insurance.csv
src/insurance_features.py   Custom feature transformer used INSIDE the saved pipeline
src/insurepredict/
    config.py               Paths, categories, input limits
    validation.py           Input validation -> typed record, errors, out-of-range warnings
    predictor.py            Model loading, prediction, interval, what-if scenarios (no Streamlit code)
    styles.py               CSS for the InsurePredict look
    ui.py                   HTML components, chart, results, history, model card
models/                     best_model.joblib + model_metadata.json (created by train_model.py)
tests/                      Validation, predictor and headless UI tests
.streamlit/config.toml      Theme and server settings
```

## How it works

* The saved pipeline accepts the six raw columns, so the app never re-implements feature engineering.
* The 90 % interval is split-conformal: a constant band (about +/- $2.5k) from out-of-fold training residuals.
* "What-if" bars re-run the same model with smoking set to non-smoker and/or BMI set to 24.9.
* Inputs are held only in the browser session. Nothing is written to disk or a database; logs record only
  coarse fields (smoker / region), never age, BMI or the estimate.

## Using your own trained model

`train_model.py` reproduces the notebook's selected model (same split, seed and tuning grid). If you re-train in the notebook
and want the app to use that model instead, save `best_model.joblib` into `models/` and update `models/model_metadata.json`
(see the keys written by `train_model.py`; the app needs `interval.halfwidth`, `training_ranges`, `reference_charges` and `test_metrics`).
Pickled models only load with the scikit-learn version that created them, so re-run `train_model.py` after upgrading it.

## Limitations

Educational estimate only; not an insurance quote or medical advice. Trained on ~1,300 historical records (US dollars), so
unusual profiles are less reliable, rare very expensive cases are under-predicted, and the data may reflect historical bias.
