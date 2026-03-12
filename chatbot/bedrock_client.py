# chatbot/bedrock_client.py
# Handles all AWS Bedrock calls. Nova Micro is used in two places:
# the "Generate financial summary" button in the Financials tab, and as a
# fallback chat responder if Vertex AI goes down or hits a quota limit.

import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

MODEL_ID = "amazon.nova-micro-v1:0"


def _invoke(prompt: str, max_tokens: int = 500) -> str:
    """Internal helper — sends a prompt to Nova Micro and returns the text response."""
    body = json.dumps({
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.3}
    })
    response = bedrock.invoke_model(body=body, modelId=MODEL_ID)
    result = json.loads(response["body"].read())
    return result["output"]["message"]["content"][0]["text"].strip()


def summarize(text: str, context: str = "financial data") -> str:
    """Generates a 2-3 sentence summary of a block of financial text. Called by the Financials tab."""
    prompt = f"""Summarize the following {context} in 2-3 clear, concise sentences
for a financial analyst audience. Focus on the most important insights.

{text}

Summary:"""
    return _invoke(prompt, max_tokens=300)


def fallback_answer(question: str, context: str) -> str:
    """Answers a chat question using Bedrock when Vertex AI isn't available. Passes recent SEC data as context."""
    prompt = f"""You are a knowledgeable financial assistant for Realty Income Corporation (ticker: O),
a real estate investment trust (REIT) that owns and leases commercial properties across the U.S. and Europe.

Answer the following question in a clear, professional, and helpful way.
Use the provided context data if relevant, and supplement with your general knowledge about Realty Income.

Question: {question}

Context (recent financial data):
{context}

Answer:"""
    return _invoke(prompt, max_tokens=500)


if __name__ == "__main__":
    sample = """
    Realty Income Corporation Fiscal Year 2025:
    Revenue: $5,749,377,000
    Net Income: $1,058,590,000
    """

    print("=== Bedrock Summarization Test ===")
    summary = summarize(sample, context="annual financial results")
    print(f"Summary: {summary}")

    print("\n=== Bedrock Fallback Test ===")
    answer = fallback_answer(
        question="How did Realty Income perform in 2025?",
        context=sample
    )
    print(f"Answer: {answer}")
