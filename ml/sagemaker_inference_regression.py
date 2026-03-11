# ml/sagemaker_inference_regression.py
# This is what actually runs inside the SageMaker container for the housing endpoint.
# Bundled into sourcedir.tar.gz by create_tarballs.py.
# NOTE: not the same as inference_regression.py — that one is the local fallback.

import joblib
import numpy as np
import os


def model_fn(model_dir):
    return {
        "model":  joblib.load(os.path.join(model_dir, "rf_housing.pkl")),
        "scaler": joblib.load(os.path.join(model_dir, "rf_housing_scaler.pkl")),
    }


def predict_fn(input_data, model_artifacts):
    # SageMaker sends a 1D array for a single CSV row — reshape before scaling
    x = input_data.reshape(1, -1) if input_data.ndim == 1 else input_data
    x_scaled = model_artifacts["scaler"].transform(x)
    return model_artifacts["model"].predict(x_scaled)
