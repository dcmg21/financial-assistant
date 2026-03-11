"""
ml/create_tarballs.py
Creates all four tarballs needed for SageMaker deployment, saved into
subfolders that match the S3 structure exactly. Just drag and drop the
folders into S3 — no renaming needed.

Usage:
    python create_tarballs.py

Output:
    ml/s3_upload/
        regression/
            model_regression.tar.gz   <- upload to s3://.../models/regression/
            sourcedir.tar.gz          <- upload to s3://.../models/regression/
        classification/
            model_classification.tar.gz  <- upload to s3://.../models/classification/
            sourcedir.tar.gz             <- upload to s3://.../models/classification/

Then run cloudshell_deploy.py in AWS CloudShell to create the endpoints.
"""

import io
import os
import tarfile

HERE      = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS = os.path.join(HERE, "artifacts")
OUT_REG   = os.path.join(HERE, "s3_upload", "regression")
OUT_CLS   = os.path.join(HERE, "s3_upload", "classification")

os.makedirs(OUT_REG, exist_ok=True)
os.makedirs(OUT_CLS, exist_ok=True)


def make_model_tar(files: dict) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for arcname, path in files.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing artifact: {path}")
            tar.add(path, arcname=arcname)
    return buf.getvalue()


def make_sourcedir_tar(inference_file: str) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for arcname, src_file in [("inference.py", inference_file),
                                   ("setup.py",    os.path.join(HERE, "sagemaker_setup.py"))]:
            if not os.path.exists(src_file):
                raise FileNotFoundError(f"Missing file: {src_file}")
            b    = open(src_file, "rb").read()
            info = tarfile.TarInfo(name=arcname)
            info.size = len(b)
            tar.addfile(info, io.BytesIO(b))
    return buf.getvalue()


def save(data: bytes, path: str):
    with open(path, "wb") as f:
        f.write(data)
    size_kb = len(data) / 1024
    print(f"  ✓ {os.path.relpath(path, HERE)}  ({size_kb:.1f} KB)")


print("Building regression tarballs...")
save(make_model_tar({
    "rf_housing.pkl":        os.path.join(ARTIFACTS, "rf_housing.pkl"),
    "rf_housing_scaler.pkl": os.path.join(ARTIFACTS, "rf_housing_scaler.pkl"),
}), os.path.join(OUT_REG, "model_regression.tar.gz"))

save(make_sourcedir_tar(
    os.path.join(HERE, "sagemaker_inference_regression.py")
), os.path.join(OUT_REG, "sourcedir.tar.gz"))

print("\nBuilding classification tarballs...")
save(make_model_tar({
    "lr_bank_marketing.pkl":          os.path.join(ARTIFACTS, "lr_bank_marketing.pkl"),
    "lr_bank_marketing_scaler.pkl":   os.path.join(ARTIFACTS, "lr_bank_marketing_scaler.pkl"),
    "lr_bank_marketing_encoders.pkl": os.path.join(ARTIFACTS, "lr_bank_marketing_encoders.pkl"),
    "lr_bank_marketing_features.pkl": os.path.join(ARTIFACTS, "lr_bank_marketing_features.pkl"),
}), os.path.join(OUT_CLS, "model_classification.tar.gz"))

save(make_sourcedir_tar(
    os.path.join(HERE, "sagemaker_inference_classification.py")
), os.path.join(OUT_CLS, "sourcedir.tar.gz"))

print("""
Done. Upload the contents of ml/s3_upload/ to S3:

  ml/s3_upload/regression/     →  s3://financial-assistant-models/models/regression/
  ml/s3_upload/classification/ →  s3://financial-assistant-models/models/classification/

Then upload cloudshell_deploy.py to AWS CloudShell and run:
    python3 cloudshell_deploy.py
""")
