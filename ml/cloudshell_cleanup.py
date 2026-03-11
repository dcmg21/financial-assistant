import boto3

S3_BUCKET = "financial-assistant-models"
REGION    = "us-east-1"

sm = boto3.client("sagemaker", region_name=REGION)
s3 = boto3.client("s3",        region_name=REGION)

ENDPOINTS = [
    "housing-regression-endpoint",
    "bank-classification-endpoint",
]

CONFIGS = [
    "housing-regression-config",
    "bank-classification-config",
]

MODELS = [
    "housing-regression-model",
    "bank-classification-model",
]

S3_FILES = [
    "models/regression/model_regression.tar.gz",
    "models/regression/sourcedir.tar.gz",
    "models/classification/model_classification.tar.gz",
    "models/classification/sourcedir.tar.gz",
]

# ── delete endpoints ──────────────────────────────────────────────────────────

for name in ENDPOINTS:
    try:
        sm.delete_endpoint(EndpointName=name)
        print(f"deleted endpoint:        {name}")
    except sm.exceptions.ClientError:
        print(f"endpoint not found:      {name}")

# ── delete endpoint configs ───────────────────────────────────────────────────

for name in CONFIGS:
    try:
        sm.delete_endpoint_config(EndpointConfigName=name)
        print(f"deleted endpoint config: {name}")
    except sm.exceptions.ClientError:
        print(f"config not found:        {name}")

# ── delete models ─────────────────────────────────────────────────────────────

for name in MODELS:
    try:
        sm.delete_model(ModelName=name)
        print(f"deleted model:           {name}")
    except sm.exceptions.ClientError:
        print(f"model not found:         {name}")

# ── delete s3 tarballs ────────────────────────────────────────────────────────

for key in S3_FILES:
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
        print(f"deleted s3 object:       s3://{S3_BUCKET}/{key}")
    except Exception as e:
        print(f"s3 delete failed:        {key} — {e}")

print("\ndone.")
