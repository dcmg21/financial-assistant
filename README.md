# Financial Assistant — Realty Income Corporation (NYSE: O)

A full-stack, multi-cloud financial assistant built with Streamlit. It pulls real SEC EDGAR data, connects to a PostgreSQL property database, runs two live ML models on AWS SageMaker, and uses Google Vertex AI (Gemini) to answer natural language questions — all in one app.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Web App (app.py)              │
│  ┌──────────┐  ┌────────────┐  ┌────────┐  ┌────────┐  │
│  │   Chat   │  │ Financials │  │Housing │  │  Bank  │  │
│  │  Panel   │  │ Dashboard  │  │  Pred  │  │  Pred  │  │
│  └────┬─────┘  └─────┬──────┘  └───┬────┘  └───┬────┘  │
└───────┼──────────────┼─────────────┼────────────┼───────┘
        │              │             │            │
        ▼              ▼             ▼            ▼
  Google Vertex    SEC EDGAR    AWS SageMaker  AWS SageMaker
   AI (Gemini)      API        Regression    Classification
   ADK Agent       (XBRL)      Endpoint       Endpoint
        │
        ├── Tool: get_annual_financials   → SEC EDGAR JSON cache
        ├── Tool: get_financial_summary   → SEC EDGAR JSON cache
        ├── Tool: search_press_releases   → press_releases.json
        ├── Tool: get_recent_news         → press_releases.json
        ├── Tool: get_properties          → Supabase PostgreSQL
        └── Tool: get_property_financials → Supabase PostgreSQL
                                                   │
                                          AWS Bedrock (fallback)
                                          Amazon Nova Micro
```

---

## How each tab works

**Chat** — You type a question in plain English. The Vertex AI ADK agent (Gemini 2.5 Flash) figures out which tool to call, fetches the data, and writes a natural language response. If Gemini is unavailable for any reason, it automatically falls back to AWS Bedrock (Nova Micro) using recent SEC data as context.

**Financials** — Pulls Realty Income's actual 10-K filings from the SEC EDGAR XBRL API, caches them locally, and displays KPI cards, bar charts, and a trend line. The "Generate financial summary" button sends the data to AWS Bedrock and gets back a 2-3 sentence summary.

**Housing Predictor** — You fill in a few housing characteristics, hit Predict, and the app sends the data to the `housing-regression-endpoint` on SageMaker. If the endpoint is down, it falls back to the local `.pkl` file and shows a badge so you can tell which one ran.

**Bank Predictor** — Same pattern, but for the bank subscription classification model on `bank-classification-endpoint`. Returns a yes/no prediction with probability scores and a bar chart.

---

## Chatbot query routing

The Vertex AI agent has six tools and routes questions automatically:

| Question | Tool |
|---|---|
| "What was net income last year?" | `get_annual_financials(year=None)` |
| "Show revenue over 5 years" | `get_financial_summary()` |
| "Any recent acquisitions?" | `search_press_releases(category="acquisition")` |
| "What's the latest news?" | `get_recent_news()` |
| "Show properties in Chicago" | `get_properties(metro_area="Chicago")` |
| "Revenue for Chicago properties?" | `get_property_financials()` |

If a question spans multiple topics, the agent calls multiple tools and combines the results into one answer.

---

## Local setup

### What you need first
- Python 3.13
- An AWS account with Bedrock and SageMaker access
- A Google Cloud account with Vertex AI API enabled
- A Supabase project (free tier works fine)

### Running it locally

```bash
# Clone the repo
git clone <your-repo-url>
cd financial-assistant

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your credentials (see the section below)
# Then run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Environment variables

Create a `.env` file in the project root with the following. Never commit this file — it's already in `.gitignore`.

```
# Supabase PostgreSQL
POSTGRES_HOST=aws-0-us-east-1.pooler.supabase.com
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres.<your-project-ref>
POSTGRES_PASSWORD=<your-password>

# AWS
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_DEFAULT_REGION=us-east-1

# Google / Gemini
GOOGLE_API_KEY=<your-gemini-api-key>
GOOGLE_CLOUD_PROJECT=<your-gcp-project-id>
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=gcp_credentials.json
```

> **Note on Supabase:** Use the Session Pooler connection values (not the direct connection). The direct connection is IPv6-only and won't work on most cloud hosting platforms. Find the pooler host and username in your Supabase dashboard under **Connect → Session pooler**.

### Database setup

Open the Supabase SQL Editor and run `database/schema.sql`. This creates the `properties` and `financials` tables and seeds them with 25 sample properties across Chicago, Dallas, Atlanta, New York, Los Angeles, and other metro areas.

---

## Machine learning models

### Regression — Housing price prediction

- **Dataset:** California Housing (scikit-learn built-in, 20,640 samples)
- **Model:** Random Forest Regressor (n_estimators=100)
- **Notebook:** `ml/notebooks/01_regression.ipynb`

Training steps: load dataset → EDA → engineer 3 derived features (`rooms_per_person`, `bedrooms_ratio`, `income_per_room`) → StandardScaler → 80/20 train/test split → train → evaluate with RMSE, MAE, R² → save artifacts to `ml/artifacts/`.

- **SageMaker endpoint:** `housing-regression-endpoint` (ml.t2.medium)
- **S3 path:** `s3://financial-assistant-models/models/regression/`
- **Container:** `sagemaker-scikit-learn:1.2-1-cpu-py3`

### Classification — Bank term deposit prediction

- **Dataset:** UCI Bank Marketing (`data_sources/bank-full.csv`, 45,211 rows)
- **Model:** Logistic Regression (max_iter=1000)
- **Notebook:** `ml/notebooks/02_classification.ipynb`

Training steps: load semicolon-delimited CSV → inspect class balance → LabelEncode all 9 categorical columns → StandardScaler → stratified 80/20 split → train → evaluate with Accuracy, Precision, Recall, F1, Confusion Matrix → save all artifacts to `ml/artifacts/`.

- **SageMaker endpoint:** `bank-classification-endpoint` (ml.t2.medium)
- **S3 path:** `s3://financial-assistant-models/models/classification/`
- **Container:** same scikit-learn image as regression

### Deploying (or redeploying) the models

```bash
# 1. Package model artifacts and inference code into tarballs
python ml/create_tarballs.py

# 2. Run cleanup in AWS CloudShell (removes old endpoints and S3 files)
python ml/cloudshell_cleanup.py

# 3. Upload tarballs to S3 (run from AWS CloudShell or locally with AWS CLI)
aws s3 cp ml/s3_upload/regression/model_regression.tar.gz s3://financial-assistant-models/models/regression/
aws s3 cp ml/s3_upload/regression/sourcedir.tar.gz s3://financial-assistant-models/models/regression/
aws s3 cp ml/s3_upload/classification/model_classification.tar.gz s3://financial-assistant-models/models/classification/
aws s3 cp ml/s3_upload/classification/sourcedir.tar.gz s3://financial-assistant-models/models/classification/

# 4. Deploy endpoints (run from AWS CloudShell)
python ml/cloudshell_deploy.py
```

---

## Cloud services

| Service | What it does |
|---|---|
| Google Vertex AI (Gemini 2.5 Flash) | Primary chatbot — natural language question routing |
| AWS SageMaker | Hosts the regression and classification endpoints |
| AWS Bedrock (Amazon Nova Micro) | Financial summarization + chatbot fallback |
| Supabase (PostgreSQL) | Property and financial records database |
| SEC EDGAR XBRL API | Real annual financials for Realty Income Corporation |

---

## Project structure

```
financial-assistant/
├── app.py                             # Main Streamlit app
├── requirements.txt
├── .streamlit/config.toml             # Theme settings
├── assets/logo.png
├── chatbot/
│   ├── agent.py                       # Vertex AI ADK agent (Gemini 2.5 Flash)
│   ├── tools.py                       # Six tool functions the agent can call
│   ├── bedrock_client.py              # AWS Bedrock client (summarize + fallback)
│   └── __init__.py
├── data_sources/
│   ├── sec_edgar.py                   # Fetches and caches SEC EDGAR financials
│   ├── realty_income_financials.json  # Cached financial data
│   ├── press_release_client.py        # Search helper for press releases
│   └── press_releases.json            # Press release dataset
├── database/
│   ├── db_client.py                   # psycopg2 connection to Supabase
│   └── schema.sql                     # Table definitions + seed data
└── ml/
    ├── notebooks/
    │   ├── 01_regression.ipynb        # Random Forest training notebook
    │   └── 02_classification.ipynb    # Logistic Regression training notebook
    ├── inference_regression.py        # Local fallback inference (regression)
    ├── inference_classification.py    # Local fallback inference (classification)
    ├── sagemaker_inference_regression.py     # Inference code for SageMaker container
    ├── sagemaker_inference_classification.py # Inference code for SageMaker container
    ├── create_tarballs.py             # Packages models for S3 upload
    ├── cloudshell_deploy.py           # Creates SageMaker endpoints (run in CloudShell)
    ├── cloudshell_cleanup.py          # Tears down all SageMaker resources
    └── artifacts/
        ├── rf_housing.pkl
        ├── rf_housing_scaler.pkl
        ├── lr_bank_marketing.pkl
        ├── lr_bank_marketing_scaler.pkl
        ├── lr_bank_marketing_encoders.pkl
        └── lr_bank_marketing_features.pkl
```
