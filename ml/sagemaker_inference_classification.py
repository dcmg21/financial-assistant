# ml/sagemaker_inference_classification.py
# This is what actually runs inside the SageMaker container for the bank endpoint.
# Bundled into sourcedir.tar.gz by create_tarballs.py.
# NOTE: app.py encodes categoricals before sending here — this only gets numeric data.
# NOTE: not the same as inference_classification.py — that one is the local fallback.

import joblib
import numpy as np
import os


def model_fn(model_dir):
    model  = joblib.load(os.path.join(model_dir, "lr_bank_marketing.pkl"))
    scaler = joblib.load(os.path.join(model_dir, "lr_bank_marketing_scaler.pkl"))
    # the container runs sklearn 1.2 which expects multi_class on the object,
    # but models trained with sklearn 1.5+ no longer store it — patch it back in
    if not hasattr(model, "multi_class"):
        model.multi_class = "auto"
    return {"model": model, "scaler": scaler}


def predict_fn(input_data, model_artifacts):
    # SageMaker sends a 1D array for a single CSV row — reshape before scaling
    # returns [prediction, prob_yes, prob_no]
    x = input_data.reshape(1, -1) if input_data.ndim == 1 else input_data
    x_scaled = model_artifacts["scaler"].transform(x)
    pred  = int(model_artifacts["model"].predict(x_scaled)[0])
    proba = model_artifacts["model"].predict_proba(x_scaled)[0]
    # return as numpy array so SageMaker's container can serialize it
    return np.array([pred, round(float(proba[1]), 4), round(float(proba[0]), 4)])
