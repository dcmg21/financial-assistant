"""
Run after re-training notebooks in the sagemaker-compat venv.
Packages pkl files into tar.gz and uploads to S3.

  python package_upload.py
"""
import io, tarfile, os, sys

ARTIFACTS = os.path.join(os.path.dirname(__file__), "artifacts")
S3_BUCKET = "financial-assistant-models"
REGION    = "us-east-1"

REGRESSION_FILES = {
    "rf_housing.pkl":        os.path.join(ARTIFACTS, "rf_housing.pkl"),
    "rf_housing_scaler.pkl": os.path.join(ARTIFACTS, "rf_housing_scaler.pkl"),
}
CLASSIFICATION_FILES = {
    "lr_bank_marketing.pkl":          os.path.join(ARTIFACTS, "lr_bank_marketing.pkl"),
    "lr_bank_marketing_scaler.pkl":   os.path.join(ARTIFACTS, "lr_bank_marketing_scaler.pkl"),
    "lr_bank_marketing_encoders.pkl": os.path.join(ARTIFACTS, "lr_bank_marketing_encoders.pkl"),
    "lr_bank_marketing_features.pkl": os.path.join(ARTIFACTS, "lr_bank_marketing_features.pkl"),
}

def make_tar(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for arcname, path in files.items():
            if not os.path.exists(path):
                print(f"  ✗ Missing: {path}")
                sys.exit(1)
            tar.add(path, arcname=arcname)
    return buf.getvalue()

print("Packaging model artifacts...")
reg_tar  = make_tar(REGRESSION_FILES)
cls_tar  = make_tar(CLASSIFICATION_FILES)
print("  ✓ model_regression.tar.gz built")
print("  ✓ model_classification.tar.gz built")

# Try uploading to S3
try:
    import boto3
    s3 = boto3.client("s3", region_name=REGION)
    s3.put_object(Bucket=S3_BUCKET, Key="models/regression/model_regression.tar.gz",     Body=reg_tar)
    s3.put_object(Bucket=S3_BUCKET, Key="models/classification/model_classification.tar.gz", Body=cls_tar)
    print("\n✓ Both tarballs uploaded to S3.")
    print("  Next: run cloudshell_deploy.py in AWS CloudShell to deploy v5 endpoints.")

except Exception as e:
    # Save locally so user can upload manually via S3 console
    ml_dir = os.path.dirname(__file__)
    reg_path = os.path.join(ml_dir, "model_regression.tar.gz")
    cls_path = os.path.join(ml_dir, "model_classification.tar.gz")
    with open(reg_path,  "wb") as f: f.write(reg_tar)
    with open(cls_path, "wb") as f: f.write(cls_tar)
    print(f"\n⚠  S3 upload failed ({e})")
    print("  Saved locally instead:")
    print(f"    {reg_path}")
    print(f"    {cls_path}")
    print("\n  Upload manually via S3 console:")
    print(f"    s3://{S3_BUCKET}/models/regression/model_regression.tar.gz")
    print(f"    s3://{S3_BUCKET}/models/classification/model_classification.tar.gz")
    print("\n  Then run cloudshell_deploy.py in AWS CloudShell.")
