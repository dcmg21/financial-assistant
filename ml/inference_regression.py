# ml/inference_regression.py
# Local fallback for the housing price predictor.
# app.py imports this when SageMaker is unavailable.

import joblib
import numpy as np
import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "artifacts", "rf_housing.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "artifacts", "rf_housing_scaler.pkl")

# Feature order must match training
FEATURES = [
    "MedInc", "HouseAge", "AveOccup", "Latitude", "Longitude",
    "Population", "rooms_per_person", "bedrooms_ratio", "income_per_room"
]


# load at startup so the first prediction isn't slow
try:
    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception:
    model  = None
    scaler = None


def predict(features: dict) -> dict:
    """Takes a dict of housing features and returns predicted value in dollars.
    Feature keys must match the FEATURES list above."""
    x = np.array([[features[f] for f in FEATURES]])
    x_scaled = scaler.transform(x)
    prediction = float(model.predict(x_scaled)[0])

    return {
        "predicted_value": round(prediction, 4),
        "predicted_value_usd": round(prediction * 100_000, 2)
    }


# SageMaker handler stubs — not used in production (see sagemaker_inference_regression.py)
def model_fn(model_dir):
    """Loads pkl files from the SageMaker model dir."""
    m  = joblib.load(os.path.join(model_dir, "rf_housing.pkl"))
    s  = joblib.load(os.path.join(model_dir, "rf_housing_scaler.pkl"))
    return {"model": m, "scaler": s}


def predict_fn(input_data, model_artifacts):
    m = model_artifacts["model"]
    s = model_artifacts["scaler"]
    x_scaled = s.transform(input_data)
    return m.predict(x_scaled)


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
