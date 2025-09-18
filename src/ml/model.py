from typing import Dict, Any
import numpy as np
from sklearn.linear_model import LinearRegression


def fit_linear_regression(X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    if X.size == 0 or y.size == 0:
        return {"n_samples": 0, "r2": None, "mae": None, "rmse": None}
    model = LinearRegression()
    model.fit(X, y)
    preds = model.predict(X)
    r2 = model.score(X, y)
    mae = float(np.mean(np.abs(preds - y)))
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
    return {
        "n_samples": int(len(y)),
        "r2": float(r2),
        "mae": mae,
        "rmse": rmse,
        "coef": model.coef_.tolist(),
        "intercept": float(model.intercept_),
    }
