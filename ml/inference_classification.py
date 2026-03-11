# ml/inference_classification.py
# Local fallback for the bank subscription predictor.
# app.py imports this when SageMaker is unavailable.

import joblib
import numpy as np
import os

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH     = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing.pkl")
SCALER_PATH    = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_scaler.pkl")
ENCODERS_PATH  = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_encoders.pkl")
FEATURES_PATH  = os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_features.pkl")


# load at startup so the first prediction isn't slow
try:
    model          = joblib.load(MODEL_PATH)
    scaler         = joblib.load(SCALER_PATH)
    label_encoders = joblib.load(ENCODERS_PATH)
    feature_cols   = joblib.load(FEATURES_PATH)
except Exception:
    model = scaler = label_encoders = feature_cols = None


def predict(features: dict) -> dict:
    """Takes raw customer features (strings for categoricals) and returns
    a yes/no prediction with probabilities."""
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


# SageMaker handler stubs — not used in production (see sagemaker_inference_classification.py)
def model_fn(model_dir):
    return {
        "model":          joblib.load(os.path.join(model_dir, "lr_bank_marketing.pkl")),
        "scaler":         joblib.load(os.path.join(model_dir, "lr_bank_marketing_scaler.pkl")),
        "label_encoders": joblib.load(os.path.join(model_dir, "lr_bank_marketing_encoders.pkl")),
        "feature_cols":   joblib.load(os.path.join(model_dir, "lr_bank_marketing_features.pkl"))
    }


def predict_fn(input_data, model_artifacts):
    m  = model_artifacts["model"]
    s  = model_artifacts["scaler"]
    x_scaled = s.transform(input_data)
    return m.predict(x_scaled), m.predict_proba(x_scaled)


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
