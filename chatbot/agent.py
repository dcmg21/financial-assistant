# chatbot/agent.py
# Sets up the Vertex AI ADK agent using Gemini 2.5 Flash.
# The agent gets six tools (defined in tools.py) and a system prompt that tells
# it how to route questions to the right data source.

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

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

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

APP_NAME        = "financial_assistant"
USER_ID         = "user"
session_service = InMemorySessionService()
runner          = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def _chat_async(user_message: str, session_id: str) -> str:

    # Check if a session already exists for this user; create one if not
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
        # We only care about text parts — skip tool call and tool result events.
        # Keep overwriting response_text so we end up with the final answer.
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text = part.text

    return response_text or "I could not generate a response. Please try again."


def chat(user_message: str, session_id: str = "default") -> str:
    """Public entry point called by app.py. Wraps the async runner so Streamlit can call it synchronously."""
    return asyncio.run(_chat_async(user_message, session_id))


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
        time.sleep(15)  # free tier is 5 RPM, so wait between test calls
