"""
app.py
Streamlit web application for the Realty Income Financial Assistant.

Tabs:
  1. 💬 Chat        — Vertex AI ADK chatbot with Bedrock fallback
  2. 📊 Financials  — SEC EDGAR data with charts
  3. 🏠 Housing     — Random Forest regression predictor
  4. 🏦 Bank        — Logistic Regression subscription predictor
"""

import sys
import os
import json
import uuid
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import boto3
import joblib

# ── Path setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "chatbot"))
sys.path.insert(0, os.path.join(BASE_DIR, "ml"))

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ── SageMaker client ───────────────────────────────────────────────────────────
REGION                   = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
REGRESSION_ENDPOINT      = "housing-regression-endpoint"
CLASSIFICATION_ENDPOINT  = "bank-classification-endpoint"
REGRESSION_FEATURES      = [
    "MedInc", "HouseAge", "AveOccup", "Latitude", "Longitude",
    "Population", "rooms_per_person", "bedrooms_ratio", "income_per_room"
]

sagemaker_runtime = boto3.client(
    "sagemaker-runtime",
    region_name=REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def sagemaker_predict_regression(features: dict) -> dict:
    """
    Call the SageMaker regression endpoint.
    Sends raw features as CSV; the endpoint scales and predicts internally.
    Returns the same dict shape as inference_regression.predict().
    """
    payload = ",".join(str(features[f]) for f in REGRESSION_FEATURES)
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=REGRESSION_ENDPOINT,
        ContentType="text/csv",
        Body=payload,
    )
    raw = response["Body"].read().decode().strip().strip("[]")
    prediction = float(raw)
    return {
        "predicted_value":     round(prediction, 4),
        "predicted_value_usd": round(prediction * 100_000, 2),
        "source": "SageMaker",
    }


def sagemaker_predict_classification(features: dict) -> dict:
    """
    Call the SageMaker classification endpoint.
    Encodes categoricals locally (same encoders used during training),
    then sends the numeric array to the endpoint.
    Returns the same dict shape as inference_classification.predict().
    """
    encoders_path    = os.path.join(BASE_DIR, "ml", "artifacts", "lr_bank_marketing_encoders.pkl")
    feature_col_path = os.path.join(BASE_DIR, "ml", "artifacts", "lr_bank_marketing_features.pkl")
    label_encoders   = joblib.load(encoders_path)
    feature_cols     = joblib.load(feature_col_path)

    # Encode categorical fields using saved LabelEncoders
    encoded = {}
    for col, val in features.items():
        if col in label_encoders:
            encoded[col] = int(label_encoders[col].transform([val])[0])
        else:
            encoded[col] = val

    payload = ",".join(str(encoded[f]) for f in feature_cols)
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=CLASSIFICATION_ENDPOINT,
        ContentType="text/csv",
        Body=payload,
    )
    raw = response["Body"].read().decode().strip()

    # Response is a serialized numpy array — parse prediction and probability
    # Format varies by SageMaker sklearn version; handle both array and scalar
    values = [v.strip().strip("[]") for v in raw.replace("\n", ",").split(",") if v.strip().strip("[]")]
    prediction = int(float(values[0]))
    # Probabilities follow if the endpoint serializes predict_proba output
    prob_yes = float(values[1]) if len(values) > 1 else (0.9 if prediction == 1 else 0.1)
    prob_no  = float(values[2]) if len(values) > 2 else (1 - prob_yes)

    return {
        "prediction":       prediction,
        "prediction_label": "yes" if prediction == 1 else "no",
        "probability_yes":  round(prob_yes, 4),
        "probability_no":   round(prob_no, 4),
        "source": "SageMaker",
    }

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Realty Income Financial Assistant",
    page_icon="🏢",
    layout="wide",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide Streamlit's header bar — it's what causes the whitespace above tabs */
header[data-testid="stHeader"] { height: 0; min-height: 0; }

/* Pull content up to top now that header is gone */
.block-container { padding-top: 1rem !important; }

/* Tab labels */
.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    font-weight: 600;
    padding: 10px 28px;
}

/* Sidebar text size */
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] li { font-size: 16px; }

/* Keep chat text consistent — stop AI markdown headers from rendering huge */
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin: 0.25rem 0 !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li { font-size: 0.95rem; line-height: 1.6; }

/* Normalize inline code inside alert/success boxes — AI responses sometimes wrap
   numbers in backticks which renders as monospace code font inside the green box */
[data-testid="stAlert"] code,
[data-testid="stAlert"] pre {
    font-family: inherit !important;
    font-size: inherit !important;
    background: transparent !important;
    padding: 0 !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.markdown("""
<div style="text-align:center; padding: 16px 0 8px 0;">
    <div style="font-size:30px; font-weight:800; color:#1F497D; letter-spacing:1px;">Realty Income</div>
    <div style="font-size:13px; color:#888; margin-top:4px; font-weight:500;">NYSE: O &nbsp;|&nbsp; Financial Assistant</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown(
    "**Data Sources**\n"
    "- 📄 SEC EDGAR Financials\n"
    "- 🏢 Property Database (Supabase)\n"
    "- 📰 Press Releases\n\n"
    "**ML Models**\n"
    "- 🏠 Housing Price (Random Forest)\n"
    "- 🏦 Bank Subscription (Logistic Reg)\n\n"
    "**Cloud**\n"
    "- ☁️ Google Vertex AI (Gemini)\n"
    "- ☁️ AWS Bedrock (Nova Micro)\n"
)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_chat, tab_fin, tab_housing, tab_bank = st.tabs([
    "💬 Chat", "📊 Financials", "🏠 Housing Predictor", "🏦 Bank Predictor"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.header("💬 Financial Assistant Chat")
    st.caption("Ask questions about Realty Income — financials, properties, news, and more.")

    # Session ID persists per browser session
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Example questions
    with st.expander("💡 Example questions"):
        cols = st.columns(2)
        examples = [
            "What was Realty Income's net income last year?",
            "Show me the revenue trend over the past 5 years",
            "Any recent acquisitions?",
            "Show properties in Chicago",
            "What's the latest company news?",
            "What is Realty Income's most recent dividend announcement?",
        ]
        for i, ex in enumerate(examples):
            col = cols[i % 2]
            if col.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state.pending_question = ex
                st.rerun()

    # Handle example button click
    if "pending_question" in st.session_state:
        prompt = st.session_state.pop("pending_question")
    else:
        prompt = st.chat_input("Ask about financials, properties, or news…")

    if prompt:
        # Show user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                response = ""
                used_fallback = False

                # Try Vertex AI agent first
                try:
                    from agent import chat as agent_chat
                    response = agent_chat(prompt, session_id=st.session_state.session_id)
                    if not response or "could not generate" in response.lower():
                        raise ValueError("Empty or default response from Vertex AI")
                except Exception as primary_err:
                    # Fallback to AWS Bedrock
                    used_fallback = True
                    try:
                        from bedrock_client import fallback_answer
                        # Pull some context from SEC data
                        fin_path = Path(BASE_DIR) / "data_sources" / "realty_income_financials.json"
                        context = ""
                        if fin_path.exists():
                            with open(fin_path) as f:
                                data = json.load(f)
                            # Most recent 2 years as context
                            recent = sorted(data.keys(), reverse=True)[:2]
                            for yr in recent:
                                d = data[yr]
                                context += f"{yr}: Revenue=${d.get('revenue', 0):,.0f}, Net Income=${d.get('net_income', 0):,.0f}\n"
                        response = fallback_answer(prompt, context or "No financial context available.")
                    except Exception as fallback_err:
                        response = f"⚠️ Both AI services are currently unavailable.\n\nVertex AI error: {primary_err}\nBedrock error: {fallback_err}"

                if used_fallback:
                    st.info("ℹ️ Response generated by AWS Bedrock (Vertex AI fallback)", icon="☁️")
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear conversation", key="clear_chat"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FINANCIALS
# ══════════════════════════════════════════════════════════════════════════════
with tab_fin:
    st.header("📊 Realty Income Financial Dashboard")

    fin_path = Path(BASE_DIR) / "data_sources" / "realty_income_financials.json"

    if not fin_path.exists():
        st.warning("Financial data not found. Run `data_sources/sec_edgar.py` to fetch it.")
    else:
        with open(fin_path) as f:
            fin_data = json.load(f)

        # Build DataFrame
        rows = []
        for yr, d in fin_data.items():
            rows.append({
                "Year": int(yr),
                "Revenue ($M)": round(d.get("revenue", 0) / 1_000_000, 1) if d.get("revenue") else None,
                "Net Income ($M)": round(d.get("net_income", 0) / 1_000_000, 1) if d.get("net_income") else None,
            })
        df = pd.DataFrame(rows).sort_values("Year", ascending=False).reset_index(drop=True)

        # KPI cards — most recent year
        latest = df.iloc[0]
        k1, k2, k3 = st.columns(3)
        k1.metric("📅 Most Recent Year", int(latest["Year"]))
        k2.metric("💰 Revenue", f"${latest['Revenue ($M)']:,.0f}M" if latest["Revenue ($M)"] else "N/A")
        k3.metric("📈 Net Income", f"${latest['Net Income ($M)']:,.0f}M" if latest["Net Income ($M)"] else "N/A")

        st.divider()

        # Charts
        df_chart = df.sort_values("Year")
        col1, col2 = st.columns(2)

        with col1:
            fig_rev = go.Figure()
            fig_rev.add_trace(go.Bar(
                x=df_chart["Year"], y=df_chart["Revenue ($M)"],
                name="Revenue", marker_color="#1f77b4"
            ))
            fig_rev.update_layout(title="Annual Revenue ($M)", xaxis_title="Year", yaxis_title="$ Millions",
                                  height=350, margin=dict(l=40, r=20, t=40, b=40))
            st.plotly_chart(fig_rev, use_container_width=True)

        with col2:
            fig_inc = go.Figure()
            fig_inc.add_trace(go.Bar(
                x=df_chart["Year"], y=df_chart["Net Income ($M)"],
                name="Net Income", marker_color="#2ca02c"
            ))
            fig_inc.update_layout(title="Annual Net Income ($M)", xaxis_title="Year", yaxis_title="$ Millions",
                                  height=350, margin=dict(l=40, r=20, t=40, b=40))
            st.plotly_chart(fig_inc, use_container_width=True)

        # Trend line chart
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_chart["Year"], y=df_chart["Revenue ($M)"],
            mode="lines+markers", name="Revenue", line=dict(color="#1f77b4", width=2)
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_chart["Year"], y=df_chart["Net Income ($M)"],
            mode="lines+markers", name="Net Income", line=dict(color="#2ca02c", width=2)
        ))
        fig_trend.update_layout(title="Revenue & Net Income Trend", xaxis_title="Year",
                                yaxis_title="$ Millions", height=350,
                                margin=dict(l=40, r=20, t=40, b=40))
        st.plotly_chart(fig_trend, use_container_width=True)

        # Raw data table
        with st.expander("📋 Raw Data Table"):
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Bedrock AI summary
        st.divider()
        st.subheader("🤖 AI Summary (AWS Bedrock)")
        if st.button("Generate financial summary", key="gen_summary"):
            with st.spinner("Generating summary via AWS Bedrock…"):
                try:
                    from bedrock_client import summarize
                    recent_rows = df.head(5)
                    text_block = "\n".join(
                        f"{int(r['Year'])}: Revenue=${r['Revenue ($M)']:,.0f}M, Net Income=${r['Net Income ($M)']:,.0f}M"
                        for _, r in recent_rows.iterrows()
                        if r["Revenue ($M)"] is not None
                    )
                    summary = summarize(text_block, context="Realty Income annual financial results")
                    st.success(summary)
                except Exception as e:
                    st.error(f"Bedrock error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HOUSING PRICE PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_housing:
    st.header("🏠 Housing Price Predictor")
    st.caption("Random Forest Regression — California Housing Dataset")

    st.info(
        "Enter housing characteristics below. The model predicts the **median house value** "
        "based on features from the California Housing dataset.",
        icon="ℹ️"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        med_inc       = st.number_input("Median Income (10k$)", min_value=0.5, max_value=15.0, value=3.5, step=0.1,
                                        help="Median household income in the block (in $10,000 units)")
        house_age     = st.number_input("House Age (years)", min_value=1, max_value=52, value=20,
                                        help="Median age of houses in the block")
        population    = st.number_input("Population", min_value=10, max_value=35682, value=1200,
                                        help="Population in the block")

    with col2:
        ave_occup     = st.number_input("Avg Occupancy", min_value=1.0, max_value=20.0, value=3.0, step=0.1,
                                        help="Average number of household members")
        latitude      = st.number_input("Latitude", min_value=32.0, max_value=42.0, value=34.05, step=0.01)
        longitude     = st.number_input("Longitude", min_value=-125.0, max_value=-114.0, value=-118.25, step=0.01)

    with col3:
        rooms_per_person  = st.number_input("Rooms per Person", min_value=0.5, max_value=20.0, value=2.5, step=0.1,
                                            help="Total rooms divided by population")
        bedrooms_ratio    = st.number_input("Bedrooms Ratio", min_value=0.01, max_value=1.0, value=0.21, step=0.01,
                                            help="Bedrooms / total rooms")
        income_per_room   = st.number_input("Income per Room", min_value=0.1, max_value=10.0, value=1.1, step=0.1,
                                            help="Median income divided by average rooms")

    if st.button("🔮 Predict House Value", key="predict_housing", use_container_width=True, type="primary"):
        features = {
            "MedInc":           med_inc,
            "HouseAge":         float(house_age),
            "AveOccup":         ave_occup,
            "Latitude":         latitude,
            "Longitude":        longitude,
            "Population":       float(population),
            "rooms_per_person": rooms_per_person,
            "bedrooms_ratio":   bedrooms_ratio,
            "income_per_room":  income_per_room,
        }
        result = None
        sagemaker_err = None
        # Try SageMaker endpoint first
        try:
            result = sagemaker_predict_regression(features)
        except Exception as e:
            sagemaker_err = str(e)

        # Fall back to local model if SageMaker unavailable
        if result is None:
            try:
                from inference_regression import predict as reg_predict
                result = reg_predict(features)
                result["source"] = "Local Model"
            except Exception as e:
                st.error(f"Prediction error: {e}")

        if result:
            st.divider()
            if result["source"] == "SageMaker":
                source_badge = "☁️ AWS SageMaker"
                st.caption(f"Prediction source: {source_badge}")
            else:
                st.caption("Prediction source: 💻 Local Model (SageMaker fallback)")
                if sagemaker_err:
                    with st.expander("ℹ️ Why Local Model? (SageMaker error details)"):
                        st.code(sagemaker_err, language=None)
            r1, r2 = st.columns(2)
            r1.metric("Predicted Value (raw)", f"{result['predicted_value']:.4f}")
            r2.metric("Predicted Median House Value", f"${result['predicted_value_usd']:,.2f}")
            st.success(
                f"✅ This block's predicted median house value is **${result['predicted_value_usd']:,.2f}**",
                icon="🏠"
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BANK SUBSCRIPTION PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_bank:
    st.header("🏦 Bank Term Deposit Predictor")
    st.caption("Logistic Regression — Bank Marketing Dataset")

    st.info(
        "Enter customer profile details to predict whether they will **subscribe to a term deposit**.",
        icon="ℹ️"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        age       = st.number_input("Age", min_value=18, max_value=95, value=35)
        job       = st.selectbox("Job", ["management", "technician", "entrepreneur", "blue-collar",
                                          "unknown", "retired", "admin.", "services", "self-employed",
                                          "unemployed", "housemaid", "student"])
        marital   = st.selectbox("Marital Status", ["married", "single", "divorced"])
        education = st.selectbox("Education", ["tertiary", "secondary", "unknown", "primary"])
        default   = st.selectbox("Has Credit Default?", ["no", "yes"])

    with col2:
        balance   = st.number_input("Account Balance ($)", min_value=-8019, max_value=102127, value=1500)
        housing   = st.selectbox("Has Housing Loan?", ["yes", "no"])
        loan      = st.selectbox("Has Personal Loan?", ["no", "yes"])
        contact   = st.selectbox("Contact Type", ["cellular", "unknown", "telephone"])
        day       = st.number_input("Last Contact Day", min_value=1, max_value=31, value=15)

    with col3:
        month     = st.selectbox("Last Contact Month", ["jan", "feb", "mar", "apr", "may", "jun",
                                                          "jul", "aug", "sep", "oct", "nov", "dec"])
        duration  = st.number_input("Call Duration (seconds)", min_value=0, max_value=4918, value=200)
        campaign  = st.number_input("Contacts This Campaign", min_value=1, max_value=63, value=2)
        pdays     = st.number_input("Days Since Last Contact (-1 = never)", min_value=-1, max_value=871, value=-1)
        previous  = st.number_input("Previous Campaign Contacts", min_value=0, max_value=275, value=0)
        poutcome  = st.selectbox("Previous Outcome", ["unknown", "failure", "other", "success"])

    if st.button("🔮 Predict Subscription", key="predict_bank", use_container_width=True, type="primary"):
        features = {
            "age": age, "job": job, "marital": marital, "education": education,
            "default": default, "balance": balance, "housing": housing, "loan": loan,
            "contact": contact, "day": day, "month": month, "duration": duration,
            "campaign": campaign, "pdays": pdays, "previous": previous, "poutcome": poutcome,
        }
        result = None
        sagemaker_err = None
        # Try SageMaker endpoint first
        try:
            result = sagemaker_predict_classification(features)
        except Exception as e:
            sagemaker_err = str(e)

        # Fall back to local model if SageMaker unavailable
        if result is None:
            try:
                from inference_classification import predict as clf_predict
                result = clf_predict(features)
                result["source"] = "Local Model"
            except Exception as e:
                st.error(f"Prediction error: {e}")

        if result:
            st.divider()
            if result["source"] == "SageMaker":
                source_badge = "☁️ AWS SageMaker"
                st.caption(f"Prediction source: {source_badge}")
            else:
                st.caption("Prediction source: 💻 Local Model (SageMaker fallback)")
                if sagemaker_err:
                    with st.expander("ℹ️ Why Local Model? (SageMaker error details)"):
                        st.code(sagemaker_err, language=None)

            label    = result["prediction_label"].upper()
            prob_yes = result["probability_yes"]
            prob_no  = result["probability_no"]

            r1, r2, r3 = st.columns(3)
            r1.metric("Prediction", label)
            r2.metric("Probability: Subscribe", f"{prob_yes:.1%}")
            r3.metric("Probability: Not Subscribe", f"{prob_no:.1%}")

            if result["prediction"] == 1:
                st.success(f"✅ This customer is **LIKELY TO SUBSCRIBE** to a term deposit ({prob_yes:.1%} confidence)", icon="✅")
            else:
                st.warning(f"❌ This customer is **UNLIKELY TO SUBSCRIBE** to a term deposit ({prob_no:.1%} confidence)", icon="⚠️")

            # Probability bar chart
            fig_prob = go.Figure(go.Bar(
                x=["Subscribe (Yes)", "Not Subscribe (No)"],
                y=[prob_yes, prob_no],
                marker_color=["#2ca02c", "#d62728"],
                text=[f"{prob_yes:.1%}", f"{prob_no:.1%}"],
                textposition="outside"
            ))
            fig_prob.update_layout(
                title="Subscription Probability",
                yaxis=dict(range=[0, 1.15], tickformat=".0%"),
                height=300,
                margin=dict(l=40, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_prob, use_container_width=True)
