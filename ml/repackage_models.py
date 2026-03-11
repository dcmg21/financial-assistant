"""
ml/repackage_models.py
Repackages both model tar.gz files with inference scripts renamed to inference.py
(SageMaker's default script name — no SAGEMAKER_PROGRAM env var needed).
Then uploads to S3, overwriting the existing files.

Usage:
    python repackage_models.py
"""

import boto3
import tarfile
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

S3_BUCKET = "financial-assistant-models"
REGION    = "us-east-1"
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

s3 = boto3.client(
    "s3",
    region_name=REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def repackage(tar_name, artifact_files, inference_script, s3_key):
    tar_path = os.path.join(BASE_DIR, tar_name)
    print(f"\nPackaging {tar_name}...")
    with tarfile.open(tar_path, "w:gz") as tar:
        for fpath in artifact_files:
            tar.add(fpath, arcname=os.path.basename(fpath))
            print(f"  + {os.path.basename(fpath)}")
        # Bundle the inference script as inference.py — SageMaker's default name
        tar.add(inference_script, arcname="inference.py")
        print(f"  + inference.py  (from {os.path.basename(inference_script)})")

    print(f"  Uploading to s3://{S3_BUCKET}/{s3_key} ...")
    s3.upload_file(tar_path, S3_BUCKET, s3_key)
    print(f"  Done.")


# ── Regression ─────────────────────────────────────────────────────────────────
repackage(
    tar_name="model_regression.tar.gz",
    artifact_files=[
        os.path.join(BASE_DIR, "artifacts", "rf_housing.pkl"),
        os.path.join(BASE_DIR, "artifacts", "rf_housing_scaler.pkl"),
    ],
    inference_script=os.path.join(BASE_DIR, "inference_regression.py"),
    s3_key="models/regression/model_regression.tar.gz",
)

# ── Classification ─────────────────────────────────────────────────────────────
repackage(
    tar_name="model_classification.tar.gz",
    artifact_files=[
        os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing.pkl"),
        os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_scaler.pkl"),
        os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_encoders.pkl"),
        os.path.join(BASE_DIR, "artifacts", "lr_bank_marketing_features.pkl"),
    ],
    inference_script=os.path.join(BASE_DIR, "inference_classification.py"),
    s3_key="models/classification/model_classification.tar.gz",
)

print("\n✅ Both models repackaged and uploaded.")
print("Next steps in AWS Console:")
print("  1. Delete both failed models (SageMaker → Inference → Models)")
print("  2. Recreate both models — NO environment variables needed this time")
print("  3. Delete failed endpoints → recreate using existing endpoint configs")
