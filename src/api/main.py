"""Museum Attendance API

This FastAPI application provides endpoints for:
- Health check (`/healthz`)
- ETL pipeline trigger (`/etl/run`)
- Retrieving museum attendance features (`/features`)
- Accessing linear regression model metrics (`/model/linear`)

Intended for use in analyzing and modeling museum attendance data.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.etl.pipeline import run_etl
from src.ml.features import load_features
from src.ml.model import fit_linear_regression

app = FastAPI(title="Museum Attendance API", version="0.1.0")


class Health(BaseModel):
    status: str


class ETLResponse(BaseModel):
    status: str
    museums: int
    cities: int
    error: str = None


@app.get("/healthz", response_model=Health)
def healthcheck() -> Health:
    return Health(status="ok")


@app.post("/etl/run", response_model=ETLResponse)
def trigger_etl():
    """Trigger the ETL pipeline to fetch and process museum data."""
    try:
        result = run_etl()
        return ETLResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/features")
def get_features():
    """Get the merged dataset of museums, cities, and populations."""
    try:
        df = load_features()
        
        # Convert DataFrame to list of rows
        rows = df.to_dict('records') if not df.empty else []
        
        return {
            "columns": df.columns.tolist(),
            "rows": rows,
            "count": len(rows)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/model/linear")
def model_linear():
    """Run linear regression on museum visitors vs city population."""
    try:
        df = load_features()
        
        if df.empty:
            return {
                "model": "linear_regression",
                "n_samples": 0,
                "r2": None,
                "mae": None,
                "rmse": None,
                "notes": "No data available. Run ETL first."
            }
        
        # Prepare features for regression
        X = df[['population']].values
        y = df['visitors'].values
        
        # Fit the model
        result = fit_linear_regression(X, y)
        
        return {
            "model": "linear_regression",
            "n_samples": result["n_samples"],
            "r2": result["r2"],
            "mae": result["mae"],
            "rmse": result["rmse"],
            "coefficients": result.get("coef", []),
            "intercept": result.get("intercept", 0),
            "notes": "Linear regression of visitors vs city population"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
