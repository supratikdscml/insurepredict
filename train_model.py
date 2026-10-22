"""Train the InsurePredict model and save it to models/.

Mirrors the upgraded notebook: stratified 80/20 split, engineered features inside the
pipeline, Lasso tuned with 5-fold CV on the training set, test set used once, and a
split-conformal 90% interval.

Usage:  python train_model.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from insurance_features import InsuranceFeatureEngineer  # noqa: E402

RANDOM_STATE = 42
COVERAGE = 0.90
NUMERIC = ["age", "bmi", "children", "age_squared", "smoker_x_bmi", "smoker_x_age"]
BINARY = ["obese", "smoker_x_obese"]
CATEGORICAL = ["sex", "smoker", "region"]


def build_pipeline() -> Pipeline:
    pre = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), NUMERIC),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore"))]), CATEGORICAL),
        ("bin", "passthrough", BINARY),
    ])
    return Pipeline([("features", InsuranceFeatureEngineer()), ("preprocessor", pre),
                     ("model", Lasso(max_iter=50000))])


def main(data_path: Path = ROOT / "data" / "insurance.csv") -> None:
    df = pd.read_csv(data_path).drop_duplicates().reset_index(drop=True)
    X, y = df.drop(columns="charges"), df["charges"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=X["smoker"])

    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    search = GridSearchCV(build_pipeline(), {"model__alpha": np.logspace(-3, 2, 11)},
                          cv=cv, scoring="neg_root_mean_squared_error", n_jobs=1)
    search.fit(X_train, y_train)
    model = search.best_estimator_

    # test set is used once, only to report performance
    pred = model.predict(X_test)
    metrics = {"mae": float(mean_absolute_error(y_test, pred)),
               "rmse": float(np.sqrt(mean_squared_error(y_test, pred))),
               "r2": float(r2_score(y_test, pred))}

    # split-conformal half-width from out-of-fold training residuals
    oof = cross_val_predict(clone(model), X_train, y_train, cv=cv)
    resid = np.abs(y_train.to_numpy() - oof)
    n = len(resid)
    halfwidth = float(np.quantile(resid, min(1.0, np.ceil((n + 1) * COVERAGE) / n)))
    covered = float(np.mean(np.abs(y_test.to_numpy() - pred) <= halfwidth))

    metadata = {
        "model_name": "Lasso regression with engineered features",
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,
        "n_train": int(len(X_train)), "n_test": int(len(X_test)),
        "best_alpha": float(search.best_params_["model__alpha"]),
        "cv_rmse": float(-search.best_score_),
        "test_metrics": metrics,
        "interval": {"method": "split-conformal", "coverage": COVERAGE, "halfwidth": halfwidth,
                     "test_coverage": covered},
        "training_ranges": {"age": [int(X.age.min()), int(X.age.max())],
                            "bmi": [float(X.bmi.min()), float(X.bmi.max())],
                            "children": [int(X.children.min()), int(X.children.max())]},
        "reference_charges": {"mean": float(y.mean()), "median": float(y.median()),
                              "smoker_mean": float(y[X.smoker == "yes"].mean()),
                              "nonsmoker_mean": float(y[X.smoker == "no"].mean())},
    }

    out = ROOT / "models"
    out.mkdir(exist_ok=True)
    joblib.dump(model, out / "best_model.joblib")
    (out / "model_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"Saved model to {out}")
    print(f"alpha={metadata['best_alpha']:.3f}  CV RMSE={metadata['cv_rmse']:,.0f}")
    print(f"Test  MAE={metrics['mae']:,.0f}  RMSE={metrics['rmse']:,.0f}  R2={metrics['r2']:.3f}")
    print(f"Conformal 90% half-width={halfwidth:,.0f}  (test coverage {covered:.1%})")


if __name__ == "__main__":
    main()
