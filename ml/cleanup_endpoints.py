"""
ml/cleanup_endpoints.py
Deletes the failed SageMaker endpoints, endpoint configs, and models
so they can be cleanly redeployed.

Usage:
    python cleanup_endpoints.py
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

sm = boto3.client(
    "sagemaker",
    region_name=REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

ENDPOINTS     = ["bank-classification-endpoint", "housing-regression-endpoint"]
CONFIGS       = ["bank-classification-endpoint-config", "housing-regression-endpoint-config"]
MODELS        = ["bank-classification-model", "housing-regression-model"]


def safe_delete(fn, label, name):
    try:
        fn(name)
        print(f"  ✅ Deleted {label}: {name}")
    except sm.exceptions.ClientError as e:
        code = e.response["Error"]["Code"]
        if "NotFound" in code or "does not exist" in str(e):
            print(f"  ⚠️  {label} not found (already deleted): {name}")
        else:
            print(f"  ❌ Error deleting {label} {name}: {e}")


print("\n=== Deleting SageMaker Endpoints ===")
for name in ENDPOINTS:
    safe_delete(lambda n: sm.delete_endpoint(EndpointName=n), "Endpoint", name)

print("\n=== Deleting Endpoint Configs ===")
for name in CONFIGS:
    safe_delete(lambda n: sm.delete_endpoint_config(EndpointConfigName=n), "Config", name)

print("\n=== Deleting Models ===")
for name in MODELS:
    safe_delete(lambda n: sm.delete_model(ModelName=n), "Model", name)

print("\n✅ Cleanup complete. Now update S3_BUCKET in deploy_sagemaker.py and run it.")
