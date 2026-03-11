"""
ml/inference_regression.py
Accepts housing feature inputs and returns a predicted median house value.
Used locally and as the SageMaker inference handler.
"""

import joblib
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "artifacts", "rf_housing.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "artifacts", "rf_housing_scaler.pkl")

# Feature order must match training
FEATURES = [
    "MedInc", "HouseAge", "AveOccup", "Latitude", "Longitude",
    "Population", "rooms_per_person", "bedrooms_ratio", "income_per_room"
]


# ── Local model references (None until loaded) ─────────────────────────────────
# In SageMaker, model_fn() handles loading from /opt/ml/model/
# Locally, call predict() only after assigning model/scaler manually
model  = None
scaler = None


def predict(features: dict) -> dict:
    """
    Predict median house value from input features.

    Parameters
    ----------
    features : dict
        Keys must match FEATURES list above.
        Example:
            {
                "MedInc": 3.5,
                "HouseAge": 20,
                "AveOccup": 3.0,
                "Latitude": 34.0,
                "Longitude": -118.0,
                "Population": 1200,
                "rooms_per_person": 2.5,
                "bedrooms_ratio": 0.2,
                "income_per_room": 1.1
            }

    Returns
    -------
    dict
        predicted_value : float  — predicted median house value (in $100k units)
        predicted_value_usd : float — same value in dollars
    """
    x = np.array([[features[f] for f in FEATURES]])
    x_scaled = scaler.transform(x)
    prediction = float(model.predict(x_scaled)[0])

    return {
        "predicted_value": round(prediction, 4),
        "predicted_value_usd": round(prediction * 100_000, 2)
    }


# ── SageMaker handler functions ───────────────────────────────────────────────
def model_fn(model_dir):
    """Load model artifacts from SageMaker model directory."""
    m  = joblib.load(os.path.join(model_dir, "rf_housing.pkl"))
    s  = joblib.load(os.path.join(model_dir, "rf_housing_scaler.pkl"))
    return {"model": m, "scaler": s}


def predict_fn(input_data, model_artifacts):
    """Run prediction using loaded SageMaker artifacts."""
    m = model_artifacts["model"]
    s = model_artifacts["scaler"]
    x_scaled = s.transform(input_data)
    return m.predict(x_scaled)


# ── Local test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "MedInc":          3.5,
        "HouseAge":        20.0,
        "AveOccup":        3.0,
        "Latitude":        34.05,
        "Longitude":      -118.25,
        "Population":      1200.0,
        "rooms_per_person": 2.5,
        "bedrooms_ratio":   0.21,
        "income_per_room":  1.1
    }

    result = predict(sample)
    print("Input features:")
    for k, v in sample.items():
        print(f"  {k}: {v}")
    print(f"\nPredicted house value: ${result['predicted_value_usd']:,.2f}")
