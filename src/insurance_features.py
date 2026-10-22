import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


# Adds domain-driven features. Input: the six raw columns. Output: raw columns + engineered columns.
class InsuranceFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self, obese_threshold=30.0):
        self.obese_threshold = obese_threshold

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        smoker = (X["smoker"].astype(str).str.lower() == "yes").astype(float)
        X["obese"] = (X["bmi"] >= self.obese_threshold).astype(float)
        X["smoker_x_bmi"] = smoker * X["bmi"]
        X["smoker_x_obese"] = smoker * X["obese"]
        X["smoker_x_age"] = smoker * X["age"]
        X["age_squared"] = X["age"] ** 2
        return X
