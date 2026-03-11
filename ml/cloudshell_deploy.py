import boto3, tarfile, io

REGION    = "us-east-1"
ROLE_ARN  = "arn:aws:iam::864795784776:role/SageMakerExecutionRole"
S3_BUCKET = "financial-assistant-models"
IMAGE     = f"683313688378.dkr.ecr.{REGION}.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"

# Bundled into sourcedir so the container upgrades numpy/sklearn/pandas to
# versions matching the pkl files, before any model loading happens.
SETUP_PY = """
from setuptools import setup
setup(
    name="inference",
    version="1.0.0",
    install_requires=["numpy>=2.0", "scikit-learn>=1.4", "pandas>=2.0"],
    py_modules=["inference"],
)
"""

REGRESSION_CODE = """
import joblib, numpy as np, os

def model_fn(model_dir):
    return {
        "model":  joblib.load(os.path.join(model_dir, "rf_housing.pkl")),
        "scaler": joblib.load(os.path.join(model_dir, "rf_housing_scaler.pkl")),
    }

def predict_fn(input_data, model_artifacts):
    x_scaled = model_artifacts["scaler"].transform(input_data)
    return model_artifacts["model"].predict(x_scaled)
"""

CLASSIFICATION_CODE = """
import joblib, numpy as np, os

def model_fn(model_dir):
    return {
        "model":          joblib.load(os.path.join(model_dir, "lr_bank_marketing.pkl")),
        "scaler":         joblib.load(os.path.join(model_dir, "lr_bank_marketing_scaler.pkl")),
        "label_encoders": joblib.load(os.path.join(model_dir, "lr_bank_marketing_encoders.pkl")),
        "feature_cols":   joblib.load(os.path.join(model_dir, "lr_bank_marketing_features.pkl")),
    }

def predict_fn(input_data, model_artifacts):
    m, s, le, fc = (model_artifacts[k] for k in ["model", "scaler", "label_encoders", "feature_cols"])
    encoded = {col: le[col].transform([val])[0] if col in le else val for col, val in input_data.items()}
    x        = np.array([[encoded[f] for f in fc]])
    x_scaled = s.transform(x)
    pred     = int(m.predict(x_scaled)[0])
    proba    = m.predict_proba(x_scaled)[0]
    return {"prediction": pred, "label": "yes" if pred == 1 else "no",
            "prob_yes": round(float(proba[1]), 4), "prob_no": round(float(proba[0]), 4)}
"""

MODELS = [
    {
        "label":    "Housing Regression",
        "model":    "housing-regression-model",
        "config":   "housing-regression-config",
        "endpoint": "housing-regression-endpoint",
        "model_s3": f"s3://{S3_BUCKET}/models/regression/model_regression.tar.gz",
        "src_key":  "models/regression/sourcedir.tar.gz",
        "code":     REGRESSION_CODE,
    },
    {
        "label":    "Bank Classification",
        "model":    "bank-classification-model",
        "config":   "bank-classification-config",
        "endpoint": "bank-classification-endpoint",
        "model_s3": f"s3://{S3_BUCKET}/models/classification/model_classification.tar.gz",
        "src_key":  "models/classification/sourcedir.tar.gz",
        "code":     CLASSIFICATION_CODE,
    },
]

s3 = boto3.client("s3", region_name=REGION)
sm = boto3.client("sagemaker", region_name=REGION)


def make_sourcedir(code):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, content in [("inference.py", code), ("setup.py", SETUP_PY)]:
            b    = content.strip().encode("utf-8")
            info = tarfile.TarInfo(name=name)
            info.size = len(b)
            tar.addfile(info, io.BytesIO(b))
    return buf.getvalue()


def try_delete(fn, **kwargs):
    try: fn(**kwargs)
    except Exception: pass


def deploy(m):
    print(f"\nDeploying: {m['label']}")

    s3.put_object(Bucket=S3_BUCKET, Key=m["src_key"], Body=make_sourcedir(m["code"]))
    src_s3 = f"s3://{S3_BUCKET}/{m['src_key']}"
    print(f"  ✓ sourcedir.tar.gz → {src_s3}")

    try_delete(sm.delete_endpoint,        EndpointName=m["endpoint"])
    try_delete(sm.delete_endpoint_config, EndpointConfigName=m["config"])
    try_delete(sm.delete_model,           ModelName=m["model"])

    sm.create_model(
        ModelName=m["model"],
        PrimaryContainer={
            "Image":        IMAGE,
            "ModelDataUrl": m["model_s3"],
            "Environment":  {
                "SAGEMAKER_PROGRAM":          "inference.py",
                "SAGEMAKER_SUBMIT_DIRECTORY": src_s3,
            },
        },
        ExecutionRoleArn=ROLE_ARN,
    )
    print(f"  ✓ Model:    {m['model']}")

    sm.create_endpoint_config(
        EndpointConfigName=m["config"],
        ProductionVariants=[{
            "VariantName": "AllTraffic", "ModelName": m["model"],
            "InitialInstanceCount": 1,  "InstanceType": "ml.t2.medium",
        }],
    )
    print(f"  ✓ Config:   {m['config']}")

    sm.create_endpoint(EndpointName=m["endpoint"], EndpointConfigName=m["config"])
    print(f"  ✓ Endpoint: {m['endpoint']}  (deploying...)")


for m in MODELS: deploy(m)

print("\nBoth endpoints deploying. Check SageMaker → Inference → Endpoints.")
print("\nEndpoint names:")
for m in MODELS: print(f"  {m['endpoint']}")
