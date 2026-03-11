# Financial Assistant Web Application
**Realty Income Corporation (NYSE: O)**

A full-stack AI-powered financial assistant that combines SEC EDGAR data, a PostgreSQL property database, press releases, machine learning predictions, and a generative AI chatbot into a single Streamlit web application.

---

## Architecture Overview

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

## Data Flow

1. **Chat** — User asks a natural language question. The Vertex AI ADK agent (Gemini 2.5 Flash) determines which tool to call, fetches from SEC EDGAR, Supabase, or press releases, and returns a natural language answer. If Gemini is unavailable, AWS Bedrock (Nova Micro) answers using recent SEC data as context.

2. **Financials** — The SEC EDGAR XBRL API is queried on first run and cached locally as `realty_income_financials.json`. The dashboard reads from this cache and displays KPI cards, bar charts, and a trend line. The AI Summary button calls AWS Bedrock to generate a 2-3 sentence narrative.

3. **ML Predictions** — User fills in a feature form. The app calls the live AWS SageMaker endpoint and displays the prediction with a source badge showing "AWS SageMaker" or "Local Model" (fallback if the endpoint is unavailable).

---

## Chatbot Query Routing

The Vertex AI ADK agent uses six tools to route queries:

| User Question | Tool Called |
|---|---|
| "What was net income last year?" | `get_annual_financials(year=None)` |
| "Show revenue over 5 years" | `get_financial_summary()` |
| "Any recent acquisitions?" | `search_press_releases(category="acquisition")` |
| "What's the latest news?" | `get_recent_news()` |
| "Show properties in Chicago" | `get_properties(metro_area="Chicago")` |
| "Revenue for Chicago properties?" | `get_property_financials()` |

The agent's system instruction defines routing rules explicitly. If a question spans multiple topics, the agent calls multiple tools and combines the results.

---

## Setup Instructions

### Prerequisites
- Python 3.13
- AWS account with Bedrock and SageMaker access
- Google Cloud account with Vertex AI API enabled
- Supabase account with the schema from `database/schema.sql`

### Local Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd financial-assistant

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your credentials (see section below)

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Environment Variables (.env)

```
# Supabase PostgreSQL
POSTGRES_HOST=db.<your-project>.supabase.co
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
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

### Database Setup

Run `database/schema.sql` in the Supabase SQL Editor to create the `properties` and `financials` tables and insert 20 sample property records across Chicago, Dallas, Atlanta, New York, Los Angeles, and other metro areas.

---

## Machine Learning Models

### Regression — Housing Price Prediction

**Dataset:** California Housing (scikit-learn built-in, 20,640 samples)
**Model:** Random Forest Regressor (n_estimators=100)
**Notebook:** `ml/notebooks/01_regression.ipynb`

Training steps:
1. Load dataset, perform EDA (shape, describe, correlation heatmap)
2. Engineer 3 derived features: `rooms_per_person`, `bedrooms_ratio`, `income_per_room`
3. Apply StandardScaler to all 9 features
4. 80/20 train/test split (random_state=42)
5. Train Random Forest Regressor
6. Evaluate: RMSE, MAE, R²
7. Save artifacts to `ml/artifacts/`

**Inference script:** `ml/inference_regression.py`
- `predict(features: dict)` returns `predicted_value` and `predicted_value_usd`
- Contains `model_fn` / `predict_fn` handlers for SageMaker

**SageMaker Deployment:**
- Packaged: `ml/model_regression.tar.gz`
- S3 path: `s3://financial-assistant-models/models/regression/`
- Container: `683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3`
- Endpoint: `housing-regression-endpoint` (ml.t2.medium)

---

### Classification — Bank Term Deposit Prediction

**Dataset:** UCI Bank Marketing (`data_sources/bank-full.csv`, 45,211 rows)
**Model:** Logistic Regression (max_iter=1000)
**Notebook:** `ml/notebooks/02_classification.ipynb`

Training steps:
1. Load semicolon-delimited CSV, inspect class distribution
2. Apply LabelEncoder to all 9 categorical columns, save encoders
3. Apply StandardScaler to all numeric features
4. Stratified 80/20 train/test split
5. Train Logistic Regression classifier
6. Evaluate: Accuracy, Precision, Recall, F1, Confusion Matrix
7. Save all artifacts to `ml/artifacts/`

**Inference script:** `ml/inference_classification.py`
- `predict(features: dict)` returns `prediction_label` (yes/no), `probability_yes`, `probability_no`
- Contains `model_fn` / `predict_fn` handlers for SageMaker

**SageMaker Deployment:**
- Packaged: `ml/model_classification.tar.gz`
- S3 path: `s3://financial-assistant-models/models/classification/`
- Container: same scikit-learn image as regression
- Endpoint: `bank-classification-endpoint` (ml.t2.medium)

---

## Cloud Services

| Service | Purpose |
|---|---|
| Google Vertex AI (Gemini 2.5 Flash) | Primary chatbot — natural language routing |
| AWS SageMaker | Hosts regression and classification endpoints |
| AWS Bedrock (Amazon Nova Micro) | Summarization and chatbot fallback |
| Supabase (PostgreSQL) | Property and financial records |
| SEC EDGAR XBRL API | Annual financials for Realty Income Corporation |

---

## Project Structure

```
financial-assistant/
├── app.py                             # Main Streamlit application
├── requirements.txt                   # Python dependencies
├── .streamlit/config.toml             # Theme configuration
├── assets/logo.png                    # Company logo
├── chatbot/
│   ├── agent.py                       # Vertex AI ADK agent
│   ├── tools.py                       # 6 data source tool functions
│   ├── bedrock_client.py              # AWS Bedrock client
│   └── __init__.py
├── data_sources/
│   ├── sec_edgar.py                   # SEC EDGAR API client
│   ├── realty_income_financials.json  # Cached financial data
│   ├── press_release_client.py        # Press release search
│   └── press_releases.json            # Mock press release data
├── database/
│   ├── db_client.py                   # Supabase psycopg2 connection
│   └── schema.sql                     # Table definitions + seed data
└── ml/
    ├── notebooks/
    │   ├── 01_regression.ipynb        # Random Forest training
    │   └── 02_classification.ipynb    # Logistic Regression training
    ├── inference_regression.py        # Regression inference script
    ├── inference_classification.py    # Classification inference script
    ├── deploy_sagemaker.py            # SageMaker deployment reference
    └── artifacts/
        ├── rf_housing.pkl
        ├── rf_housing_scaler.pkl
        ├── lr_bank_marketing.pkl
        ├── lr_bank_marketing_scaler.pkl
        ├── lr_bank_marketing_encoders.pkl
        └── lr_bank_marketing_features.pkl
```
