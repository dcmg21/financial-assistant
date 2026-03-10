"""
chatbot/agent.py
Vertex AI ADK agent for the Financial Assistant.
Routes natural language questions to the correct data source tool.

Usage:
    python agent.py
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from tools import (
    get_annual_financials,
    get_financial_summary,
    search_press_releases,
    get_recent_news,
    get_properties,
    get_property_financials,
)

load_dotenv()

# ── Set Gemini API key ─────────────────────────────────────────────────────────
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

# ── Build Agent ────────────────────────────────────────────────────────────────
SYSTEM_INSTRUCTION = """
You are a Financial Assistant for Realty Income Corporation (ticker: O),
a real estate investment trust (REIT) that owns and leases commercial properties.

You have access to three data sources and must route every question to the
correct tool:

1. SEC EDGAR financials — for questions about company-wide revenue, net income,
   earnings, financial performance, or annual results.

2. Property database — for questions about specific properties, locations,
   metro areas, square footage, property types, or property-level financials.

3. Press releases — for questions about company news, acquisitions, expansions,
   dividends, partnerships, or recent announcements.

Always:
- Use the most relevant tool for the question asked
- Combine results from multiple tools if the question spans topics
- Provide clear, concise answers in plain English
- Format numbers with commas and dollar signs where appropriate
- If you are unsure which tool to use, ask the user to clarify

Example questions and routing:
- "What was net income last year?" → get_annual_financials
- "Show me properties in Chicago" → get_properties
- "Any recent acquisitions?" → search_press_releases(category="acquisition")
- "What's the latest news?" → get_recent_news
- "Show revenue for Chicago properties" → get_property_financials + get_properties
"""

agent = Agent(
    model="gemini-2.5-flash",
    name="financial_assistant",
    description="Financial assistant for Realty Income Corporation",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_annual_financials,
        get_financial_summary,
        search_press_releases,
        get_recent_news,
        get_properties,
        get_property_financials,
    ],
)

# ── Session + Runner ───────────────────────────────────────────────────────────
APP_NAME        = "financial_assistant"
USER_ID         = "user"
session_service = InMemorySessionService()
runner          = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# ── Async core ─────────────────────────────────────────────────────────────────
async def _chat_async(user_message: str, session_id: str) -> str:
    """Async implementation of chat — handles session creation and event loop."""

    # Create session if it doesn't exist
    try:
        existing = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except Exception:
        existing = None

    if not existing:
        await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    content = Content(role="user", parts=[Part(text=user_message)])

    response_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        # Capture text from model events (skip tool call/result events)
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text = part.text  # keep updating — last text wins

    return response_text or "I could not generate a response. Please try again."


def chat(user_message: str, session_id: str = "default") -> str:
    """
    Send a message to the agent and return its response.
    Called by the Streamlit app.

    Args:
        user_message: The user's natural language question
        session_id:   Session ID to maintain conversation history

    Returns:
        The agent's response as a string
    """
    return asyncio.run(_chat_async(user_message, session_id))


# ── Local test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Financial Assistant — Vertex AI ADK")
    print("=" * 60)

    test_questions = [
        "What was Realty Income's net income last year?",
    ]

    import time
    for q in test_questions:
        print(f"\nUser: {q}")
        response = chat(q, session_id="test")
        print(f"Agent: {response}")
        print("-" * 60)
        time.sleep(15)  # stay within 5 RPM free tier limit
