"""
chatbot/bedrock_client.py
AWS Bedrock integration for summarization and fallback support.
Uses Amazon Nova Micro via AWS Bedrock — satisfies the multi-cloud requirement.
"""

import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ── Bedrock client ─────────────────────────────────────────────────────────────
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

MODEL_ID = "amazon.nova-micro-v1:0"


def _invoke(prompt: str, max_tokens: int = 500) -> str:
    """Internal helper — calls Amazon Nova Micro and returns the response string."""
    body = json.dumps({
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.3}
    })
    response = bedrock.invoke_model(body=body, modelId=MODEL_ID)
    result = json.loads(response["body"].read())
    return result["output"]["message"]["content"][0]["text"].strip()


def summarize(text: str, context: str = "financial data") -> str:
    """
    Summarize a block of text using Amazon Titan via AWS Bedrock.
    Used to provide concise summaries of financial data or press releases.

    Args:
        text:    The text to summarize
        context: What type of content is being summarized

    Returns:
        A concise summary string
    """
    prompt = f"""Summarize the following {context} in 2-3 clear, concise sentences
for a financial analyst audience. Focus on the most important insights.

{text}

Summary:"""
    return _invoke(prompt, max_tokens=300)


def fallback_answer(question: str, context: str) -> str:
    """
    Fallback response generator using Bedrock when the primary
    Vertex AI agent is unavailable or hits quota limits.

    Args:
        question: The user's original question
        context:  Any relevant data already retrieved

    Returns:
        A natural language answer based on the context
    """
    prompt = f"""You are a financial assistant for Realty Income Corporation (ticker: O).
Answer the following question using only the provided context data.
Be concise and professional.

Question: {question}

Context:
{context}

Answer:"""
    return _invoke(prompt, max_tokens=500)


# ── Local test ─────────────────────────────────────────────────────────────────
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
