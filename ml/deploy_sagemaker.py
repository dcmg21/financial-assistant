"""
ml/deploy_sagemaker.py
Packages model artifacts and deploys both models to SageMaker hosted endpoints.

Usage:
    python deploy_sagemaker.py

Requirements:
    - AWS credentials configured (aws configure OR .env file with keys below)
    - An S3 bucket already created
    - SageMaker execution role ARN (from AWS console)
"""

import boto3
import tarfile
import os
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG — fill these in ─────────────────────────────────────────────────────
S3_BUCKET    = "financial-assistant-models"
REGION       = "us-east-1"                    # match your SageMaker region
ROLE_ARN     = "arn:aws:iam::864795784776:role/SageMakerExecutionRole"

# SageMaker uses this container for sklearn models
SKLEARN_IMAGE = f"683313688378.dkr.ecr.{REGION}.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

s3     = boto3.client("s3",         region_name=REGION)
sm     = boto3.client("sagemaker",  region_name=REGION)


def package_model(tar_name: str, artifact_files: list, inference_script: str) -> str:
    """
    Bundle model artifacts + inference script into a .tar.gz for SageMaker.
    Returns the local path to the tar file.
    """
    tar_path = os.path.join(BASE_DIR, tar_name)
    with tarfile.open(tar_path, "w:gz") as tar:
        for fpath in artifact_files:
            tar.add(fpath, arcname=os.path.basename(fpath))
        tar.add(inference_script, arcname=os.path.basename(inference_script))
    print(f"  Packaged: {tar_name}")
    return tar_path


def upload_to_s3(local_path: str, s3_key: str) -> str:
    """Upload a file to S3 and return the S3 URI."""
    s3.upload_file(local_path, S3_BUCKET, s3_key)
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
    print(f"  Uploaded to: {s3_uri}")
    return s3_uri


def deploy_model(model_name: str, s3_uri: str, endpoint_name: str):
    """Create a SageMaker model, endpoint config, and deploy endpoint."""

    # 1. Create SageMaker model
    print(f"  Creating SageMaker model: {model_name}")
    sm.create_model(
        ModelName=model_name,
        PrimaryContainer={
            "Image":        SKLEARN_IMAGE,
            "ModelDataUrl": s3_uri,
            "Environment":  {
                # Tell SageMaker which script to use as the serving entry point.
                # The script is already bundled inside the model.tar.gz at its root,
                # so SAGEMAKER_SUBMIT_DIRECTORY is NOT set — when it points to the
                # same S3 URI as the model data it causes a pip-install conflict.
                "SAGEMAKER_PROGRAM": (
                    "inference_regression.py"
                    if "regression" in model_name
                    else "inference_classification.py"
                ),
            }
        },
        ExecutionRoleArn=ROLE_ARN
    )

    # 2. Create endpoint config
    config_name = f"{endpoint_name}-config"
    print(f"  Creating endpoint config: {config_name}")
    sm.create_endpoint_config(
        EndpointConfigName=config_name,
        ProductionVariants=[{
            "VariantName":          "AllTraffic",
            "ModelName":            model_name,
            "InitialInstanceCount": 1,
            "InstanceType":         "ml.t2.medium"
        }]
    )

    # 3. Deploy endpoint
    print(f"  Deploying endpoint: {endpoint_name}  (takes ~5 min...)")
    sm.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=config_name
    )
    print(f"  Done — endpoint '{endpoint_name}' is being created.")


# ── REGRESSION ─────────────────────────────────────────────────────────────────
print("\n=== Deploying Regression Model ===")
reg_artifacts = [
    os.path.join(BASE_DIR, "artifacts", "rf_housing.pkl"),
    os.path.join(BASE_DIR, "artifacts", "rf_housing_scaler.pkl"),
]
reg_tar  = package_model("model_regression.tar.gz", reg_artifacts,
                          os.path.join(BASE_DIR, "inference_regression.py"))
reg_s3   = upload_to_s3(reg_tar, "models/regression/model_regression.tar.gz")
deploy_model("housing-regression-model", reg_s3, "housing-regression-endpoint")


# ── CLASSIFICATION ─────────────────────────────────────────────────────────────
print("\n=== Deploying Classification Model ===")
clf_artifacts = [
    os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing.pkl"),
    os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_scaler.pkl"),
    os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_encoders.pkl"),
    os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_features.pkl"),
]
clf_tar  = package_model("model_classification.tar.gz", clf_artifacts,
                          os.path.join(BASE_DIR, "inference_classification.py"))
clf_s3   = upload_to_s3(clf_tar, "models/classification/model_classification.tar.gz")
deploy_model("bank-classification-model", clf_s3, "bank-classification-endpoint")


print("\n=== All deployments kicked off! ===")
print("Check status in AWS Console → SageMaker → Endpoints")
print("Both endpoints take ~5 minutes to reach InService status.")
