# 🛡️ InsurePredict — Medical Insurance Cost Predictor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://insurepredict.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5%2B-orange?logo=scikitlearn)
![License](https://img.shields.io/badge/License-MIT-green)

> **Live demo →** https://insurepredict.streamlit.app

An interactive web application that estimates annual US medical insurance charges from six demographic inputs — using a **Lasso regression model with engineered interaction features** trained on real-world insurance data.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎯 **Instant prediction** | Estimates annual charges from age, gender, BMI, children, smoking status & region |
| 📊 **Confidence interval** | 90 % split-conformal prediction band (~±$2,500) calibrated on held-out training residuals |
| 💡 **What-if scenarios** | Shows how quitting smoking or reaching a healthy BMI would change your estimate |
| 📈 **Session history** | Tracks all queries in the current session for easy comparison |
| 🧾 **Model card** | Embedded model card with live test-set metrics (MAE, RMSE, R²) |
| 🔄 **Auto-rebuild** | Automatically retrains the model on first launch if sklearn version mismatches |

---

## 🖥️ Live App

The app is deployed at **Streamlit Community Cloud**:

**➡️ https://insurepredict.streamlit.app**

No installation needed — open the link, enter your details, and get your estimate instantly.

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11 or later
- `pip`

### Quick start

```bash
# 1. Clone the repo
git clone https://github.com/supratikdscml/insurepredict.git
cd insurepredict

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build the model (takes ~10 seconds)
python train_model.py

# 4. Launch the app
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### With Docker

```bash
docker build -t insurepredict .
docker run -p 8501:8501 insurepredict
```

The Docker image automatically trains the model during build, so no extra steps are needed.

---

## 🗂️ Project Layout

```
insurepredict/
│
├── app.py                          # Streamlit entry point (layout + wiring only)
├── train_model.py                  # Reproduces & saves the trained pipeline
├── requirements.txt                # Runtime dependencies
├── Dockerfile                      # Container image (builds model during build)
│
├── src/
│   ├── insurance_features.py       # Custom sklearn transformer (feature engineering)
│   └── insurepredict/
│       ├── config.py               # Paths, categories, and input limits
│       ├── validation.py           # Input validation → typed record + errors/warnings
│       ├── predictor.py            # Model loading, prediction & what-if scenarios
│       ├── styles.py               # CSS for the InsurePredict theme
│       └── ui.py                   # HTML components, charts, results, history, model card
│
├── models/
│   ├── best_model.joblib           # Trained sklearn pipeline (auto-rebuilt if stale)
│   └── model_metadata.json         # Metrics, conformal interval, training ranges
│
├── data/
│   └── insurance.csv               # Source dataset (~1,338 rows)
│
├── notebooks/
│   └── insurance_cost_prediction_upgraded.ipynb  # Full EDA, modelling & analysis
│
├── tests/                          # pytest test suite (validation, predictor, UI)
└── .streamlit/
    └── config.toml                 # Theme and server settings
```

---

## 🧠 How It Works

### Model
- **Algorithm:** Lasso regression (L1 regularisation)
- **Target:** Annual insurance charges (USD)
- **Split:** Stratified 80/20 train/test (seed = 42)
- **Tuning:** 5-fold GridSearchCV over `alpha ∈ [0.001, 100]` on the training set only

### Feature Engineering (inside the sklearn pipeline)
The raw 6 columns are transformed into richer features before modelling:

| Engineered Feature | Description |
|---|---|
| `smoker_x_bmi` | Smoking × BMI interaction (key cost driver) |
| `smoker_x_age` | Smoking × age interaction |
| `age_squared` | Captures non-linear age effect |
| `obese` | Binary flag: BMI ≥ 30 |
| `smoker_x_obese` | Smoking × obesity interaction |

All numeric features are standardised; categorical features are one-hot encoded — all inside a single `sklearn.Pipeline`, so no feature engineering happens in the app.

### Prediction Interval
The 90 % interval uses **split-conformal prediction**:
1. Out-of-fold residuals are computed on the training set
2. The 90th percentile of absolute residuals becomes the half-width (~$2,500)
3. Every prediction gets `[estimate − half, estimate + half]`

### Privacy
- Nothing is written to disk or a database during prediction
- Logs record only coarse fields (`smoker` / `region`) — never age, BMI, or the estimate

---

## 📊 Model Performance

| Metric | Test Set (held-out, used once) |
|---|---|
| MAE | ~$2,600 |
| RMSE | ~$4,700 |
| R² | ~0.87 |
| 90 % interval coverage | ~91 % |

*Live metrics are shown in the app's embedded Model Card.*

---

## 📓 Notebook

The full analysis lives in [`notebooks/insurance_cost_prediction_upgraded.ipynb`](notebooks/insurance_cost_prediction_upgraded.ipynb):

1. **EDA** — distribution plots, correlation heatmap, outlier analysis  
2. **Hypothesis testing** — t-tests, Mann-Whitney, ANOVA, Kruskal-Wallis  
3. **Multicollinearity** — VIF analysis  
4. **Model comparison** — Linear, Ridge, Lasso, ElasticNet, KNN, Random Forest, Gradient Boosting (raw vs engineered features, original vs log target)  
5. **Hyperparameter tuning + nested CV** — honest generalisation estimate  
6. **Test evaluation** — bootstrap 95 % confidence intervals + residual analysis  
7. **Interpreting predictors** — permutation importance (final model & Ridge), linear effect sizes, partial dependence plots  

---

## ⚠️ Limitations

This is an **educational tool**, not an insurance quote or medical advice.

- Trained on ~1,300 US historical records — unusual profiles are less reliable
- Very expensive cases (>$50k) tend to be under-predicted
- Data may reflect historical demographic bias
- Results vary by US region and time period

---

## 🛠️ Development

### Run tests

```bash
pip install pytest
pytest -q
```

### Re-train the model

```bash
python train_model.py
```

### Add secrets (if needed)

Create `.streamlit/secrets.toml` locally (never commit this file):

```toml
[optional_key]
value = "..."
```

---

## 📄 License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- Dataset: [Medical Cost Personal Datasets](https://www.kaggle.com/datasets/mirichoi0218/insurance) (Kaggle)
- Built with [Streamlit](https://streamlit.io), [scikit-learn](https://scikit-learn.org), and [Altair](https://altair-viz.github.io)
