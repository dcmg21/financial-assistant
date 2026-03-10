# Financial Assistant — Project Status
Paste this into any new chat to restore full context.

---

## Assignment
Build a Financial Assistant Web Application for Realty Income Corporation (ticker: O).
Full stack: SEC data + Supabase DB + press releases + ML models + Vertex AI chatbot + Streamlit UI.

---

## Project Location
`C:\Users\Drew\OneDrive\Documents\Personal Coding Projects\RTS_Job\financial-assistant\`

---

## File Structure
```
financial-assistant/
  data_sources/
    sec_edgar.py                  # Pulls Realty Income financials from SEC EDGAR API
    realty_income_financials.json # Cached SEC data 2010-2025
    press_release_client.py       # Search/retrieve press releases
    press_releases.json           # Mock press release data
    bank-full.csv                 # UCI Bank Marketing dataset
  database/
    db_client.py                  # Supabase PostgreSQL client (DONE)
  ml/
    notebooks/
      01_regression.ipynb         # California Housing / Random Forest (DONE, ran successfully)
      02_classification.ipynb     # Bank Marketing / Logistic Regression (DONE, ran successfully)
    artifacts/
      rf_housing.pkl              # Trained regression model
      rf_housing_scaler.pkl       # Regression scaler
      lr_bank_marketing.pkl       # Trained classification model
      lr_bank_marketing_scaler.pkl
      lr_bank_marketing_encoders.pkl
      lr_bank_marketing_features.pkl
      inference_regression.py     # Copied here for tar packaging
      inference_classification.py # Copied here for tar packaging
    inference_regression.py       # Regression inference script
    inference_classification.py   # Classification inference script
    deploy_sagemaker.py           # Reference deployment script (not used — deployed via GUI)
    model_regression.tar.gz       # Packaged for SageMaker
    model_classification.tar.gz   # Packaged for SageMaker
  requirements.txt
  README.md
  PROJECT_STATUS.md               # This file
```

---

## Completed Steps

### 1. Data Sources ✅
- **SEC EDGAR** — `sec_edgar.py` fetches Realty Income revenue + net income from SEC API, cached in JSON
- **Press releases** — `press_releases.json` + `press_release_client.py` for keyword/category/metro search
- **Supabase DB** — PostgreSQL with Properties and Financials tables, 20+ sample records, `db_client.py` done

### 2. ML Models ✅
- **Regression** — Random Forest on California Housing dataset. Notebook: EDA → feature engineering → train/test split → StandardScaler → RF trained → evaluated with RMSE/MAE/R² → artifacts saved
- **Classification** — Logistic Regression on UCI Bank Marketing dataset (bank-full.csv, semicolon-separated). Notebook: load → encode categoricals with LabelEncoder → StandardScaler → stratified 80/20 split → LR trained → evaluated with accuracy/precision/recall/F1/confusion matrix → artifacts saved

### 3. Inference Scripts ✅
- `inference_regression.py` — `predict(features: dict)` returns predicted house value in $100k and USD. Also has `model_fn`/`predict_fn` for SageMaker.
- `inference_classification.py` — `predict(features: dict)` returns prediction label (yes/no) + probability scores. Also has `model_fn`/`predict_fn` for SageMaker.

### 4. SageMaker Deployment ✅
- **AWS Account ID:** 864795784776
- **Region:** us-east-1
- **S3 Bucket:** financial-assistant-models
  - `models/regression/model_regression.tar.gz`
  - `models/classification/model_classification.tar.gz`
- **IAM Role:** SageMakerExecutionRole (has AmazonSageMakerFullAccess + AmazonS3FullAccess)
- **SKLearn container image:** `683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3`
- **Models created:**
  - `housing-regression-model`
  - `bank-classification-model`
- **Endpoint configs:**
  - `housing-regression-config` (ml.t2.medium)
  - `bank-classification-config` (ml.t2.medium)
- **Live endpoints (InService):**
  - `housing-regression-endpoint`
  - `bank-classification-endpoint`

---

## Remaining Steps

| Step | Status |
|------|--------|
| Vertex AI ADK Chatbot | ⏳ Next up |
| Multi-cloud integration (AWS Bedrock or Azure OpenAI) | ⏳ Pending |
| Streamlit web app | ⏳ Pending |
| Screen recorded demo | ⏳ Pending |
| README documentation | ⏳ Pending |

---

## Vertex AI Chatbot — Requirements
- Use GCP Vertex AI + Agent Development Kit (ADK)
- Agent routes natural language questions to the right data source:
  - SEC EDGAR → financial questions (revenue, net income)
  - Supabase DB → property questions (metro area, sq footage, revenue)
  - Press releases → acquisition/expansion news
- Returns natural language answers using a generative model

## Streamlit App — Requirements
- Conversational chat panel → wired to Vertex AI chatbot
- Results section → financial data, property data, press release summaries
- ML section → user inputs features → calls SageMaker endpoints → displays predictions
- Must show regression prediction (house value) and classification prediction (subscription yes/no + probability)

## Screen Demo — Requirements (from assignment)
- End-to-end app walkthrough
- Chatbot conversations
- Property queries
- Press release summaries
- Regression + classification predictions from SageMaker endpoints
- Separate cloud config recording: Vertex AI ADK setup + SageMaker deployment steps

---

## Tech Stack
- Python 3.13, venv at `financial-assistant/venv/`
- Streamlit, Plotly, pandas, scikit-learn, psycopg2, boto3
- Supabase (PostgreSQL)
- AWS: S3, SageMaker
- GCP: Vertex AI ADK (next step)
