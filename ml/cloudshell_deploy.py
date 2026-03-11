"""
ml/cloudshell_deploy.py
Creates the SageMaker models, endpoint configs, and endpoints.

Pre-requisite: all four tarballs must already be in S3.
Run create_tarballs.py locally and upload them first:

    S3 paths expected:
    s3://financial-assistant-models/models/regression/model_regression.tar.gz
    s3://financial-assistant-models/models/regression/sourcedir.tar.gz
    s3://financial-assistant-models/models/classification/model_classification.tar.gz
    s3://financial-assistant-models/models/classification/sourcedir.tar.gz

Usage (in AWS CloudShell):
  1. Upload cloudshell_deploy.py to CloudShell
  2. Run: python3 cloudshell_deploy.py
"""

import boto3

REGION    = "us-east-1"
ROLE_ARN  = "arn:aws:iam::864795784776:role/SageMakerExecutionRole"
S3_BUCKET = "financial-assistant-models"
IMAGE     = f"683313688378.dkr.ecr.{REGION}.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"

MODELS = [
    {
        "label":    "Housing Regression",
        "model":    "housing-regression-model",
        "config":   "housing-regression-config",
        "endpoint": "housing-regression-endpoint",
        "model_s3": f"s3://{S3_BUCKET}/models/regression/model_regression.tar.gz",
        "src_s3":   f"s3://{S3_BUCKET}/models/regression/sourcedir.tar.gz",
    },
    {
        "label":    "Bank Classification",
        "model":    "bank-classification-model",
        "config":   "bank-classification-config",
        "endpoint": "bank-classification-endpoint",
        "model_s3": f"s3://{S3_BUCKET}/models/classification/model_classification.tar.gz",
        "src_s3":   f"s3://{S3_BUCKET}/models/classification/sourcedir.tar.gz",
    },
]

sm = boto3.client("sagemaker", region_name=REGION)


def try_delete(fn, **kwargs):
    try:
        fn(**kwargs)
    except Exception:
        pass


def deploy(m):
    print(f"\nDeploying: {m['label']}")

    # Delete existing endpoint, config, model (safe to run even if they don't exist)
    try_delete(sm.delete_endpoint,        EndpointName=m["endpoint"])
    try_delete(sm.delete_endpoint_config, EndpointConfigName=m["config"])
    try_delete(sm.delete_model,           ModelName=m["model"])

    # Create Model
    sm.create_model(
        ModelName=m["model"],
        PrimaryContainer={
            "Image":        IMAGE,
            "ModelDataUrl": m["model_s3"],
            "Environment":  {
                "SAGEMAKER_PROGRAM":          "inference.py",
                "SAGEMAKER_SUBMIT_DIRECTORY": m["src_s3"],
            },
        },
        ExecutionRoleArn=ROLE_ARN,
    )
    print(f"  ✓ Model:    {m['model']}")

    # Create Endpoint Config
    sm.create_endpoint_config(
        EndpointConfigName=m["config"],
        ProductionVariants=[{
            "VariantName":          "AllTraffic",
            "ModelName":            m["model"],
            "InitialInstanceCount": 1,
            "InstanceType":         "ml.t2.medium",
        }],
    )
    print(f"  ✓ Config:   {m['config']}")

    # Create Endpoint
    sm.create_endpoint(EndpointName=m["endpoint"], EndpointConfigName=m["config"])
    print(f"  ✓ Endpoint: {m['endpoint']}  (deploying — takes ~8-10 min)")


for m in MODELS:
    deploy(m)

print("\nBoth endpoints deploying.")
print("Check SageMaker → Inference → Endpoints until both show InService.\n")
for m in MODELS:
    print(f"  {m['endpoint']}")
