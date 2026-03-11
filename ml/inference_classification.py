"""
ml/inference_classification.py
Accepts bank customer feature inputs and returns a subscription prediction
with probability score.
Used locally and as the SageMaker inference handler.
"""

import joblib
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH     = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing.pkl")
SCALER_PATH    = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_scaler.pkl")
ENCODERS_PATH  = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_encoders.pkl")
FEATURES_PATH  = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_features.pkl")


# ── Local model references (None until loaded) ─────────────────────────────────
# In SageMaker, model_fn() handles loading from /opt/ml/model/
# Locally, call predict() only after assigning these manually
model = scaler = label_encoders = feature_cols = None


def predict(features: dict) -> dict:
    """
    Predict whether a customer will subscribe to a term deposit.

    Parameters
    ----------
    features : dict
        Raw (un-encoded) customer features. Categorical values should be
        the original string labels from the dataset.
        Example:
            {
                "age": 35,
                "job": "management",
                "marital": "married",
                "education": "tertiary",
                "default": "no",
                "balance": 1500,
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "day": 15,
                "month": "may",
                "duration": 200,
                "campaign": 2,
                "pdays": -1,
                "previous": 0,
                "poutcome": "unknown"
            }

    Returns
    -------
    dict
        prediction       : int   — 1 = subscribes, 0 = does not subscribe
        prediction_label : str   — "yes" or "no"
        probability_yes  : float — probability of subscribing (0–1)
        probability_no   : float — probability of not subscribing (0–1)
    """
    # Encode categorical fields using saved label encoders
    encoded = {}
    for col, val in features.items():
        if col in label_encoders:
            encoded[col] = label_encoders[col].transform([val])[0]
        else:
            encoded[col] = val

    x = np.array([[encoded[f] for f in feature_cols]])
    x_scaled = scaler.transform(x)

    prediction = int(model.predict(x_scaled)[0])
    proba      = model.predict_proba(x_scaled)[0]

    return {
        "prediction":       prediction,
        "prediction_label": "yes" if prediction == 1 else "no",
        "probability_yes":  round(float(proba[1]), 4),
        "probability_no":   round(float(proba[0]), 4)
    }


# ── SageMaker handler functions ───────────────────────────────────────────────
def model_fn(model_dir):
    """Load model artifacts from SageMaker model directory."""
    return {
        "model":          joblib.load(os.path.join(model_dir, "lr_bank_marketing.pkl")),
        "scaler":         joblib.load(os.path.join(model_dir, "lr_bank_marketing_scaler.pkl")),
        "label_encoders": joblib.load(os.path.join(model_dir, "lr_bank_marketing_encoders.pkl")),
        "feature_cols":   joblib.load(os.path.join(model_dir, "lr_bank_marketing_features.pkl"))
    }


def predict_fn(input_data, model_artifacts):
    """Run prediction using loaded SageMaker artifacts."""
    m  = model_artifacts["model"]
    s  = model_artifacts["scaler"]
    x_scaled = s.transform(input_data)
    return m.predict(x_scaled), m.predict_proba(x_scaled)


# ── Local test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "age":       35,
        "job":       "management",
        "marital":   "married",
        "education": "tertiary",
        "default":   "no",
        "balance":   1500,
        "housing":   "yes",
        "loan":      "no",
        "contact":   "cellular",
        "day":       15,
        "month":     "may",
        "duration":  200,
        "campaign":  2,
        "pdays":    -1,
        "previous":  0,
        "poutcome":  "unknown"
    }

    result = predict(sample)
    print("Input features:")
    for k, v in sample.items():
        print(f"  {k}: {v}")
    print(f"\nPrediction:      {result['prediction_label'].upper()}")
    print(f"Probability Yes: {result['probability_yes']:.2%}")
    print(f"Probability No:  {result['probability_no']:.2%}")
