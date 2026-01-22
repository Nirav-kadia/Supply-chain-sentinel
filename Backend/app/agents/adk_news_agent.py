from google.adk.agents import Agent
from google.adk.tools import google_search
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

import json
from app.core.graph_builder import GraphManager
import json
import re


# -------------------------
# CONFIG
# -------------------------

BLOCKED_DOMAINS = [
    "reddit.com",
    "twitter.com",
    "facebook.com",
    "gossip.com"
]

graph_db = GraphManager()


# -------------------------
# DOMAIN FILTER (SAFE)
# -------------------------

def domain_filter_callback(tool, args, tool_context):
    print("Applying domain filter callback...------------------------------")
    if tool.name == "google_search":
        query = args.get("query", "")

        for domain in BLOCKED_DOMAINS:
            if f"site:{domain}" in query:
                return {"error": f"Blocked domain: {domain}"}

        if "when:7d" not in query:
            args["query"] = f"{query} when:7d"

    return None


# -------------------------
# AGENT (NO FUNCTION CALLING)
# -------------------------

news_agent = Agent(
    name="supply_chain_news_monitor",
    model="gemini-2.5-flash",
    instruction="""
You are a Supply Chain Intelligence Researcher.

TASK:
1. Search for recent supply chain disruptions.
2. Extract ONLY factual entities.

ENTITY TYPES:
- Supplier
- Manufacturer
- Location
- Event

OUTPUT FORMAT (STRICT JSON ONLY):

{
  "source": "Reuters | Bloomberg | Other",
  "entities": [
    {
      "name": "Entity Name",
      "type": "Supplier"
    }
  ]
}

Rules:
- DO NOT explain
- DO NOT analyze
- DO NOT add extra text
- RETURN JSON ONLY
""",
    tools=[google_search],
    before_tool_callback=[domain_filter_callback]
)

def clean_llm_json(text: str) -> dict:
    """
    Removes ```json ... ``` or ``` ... ``` wrappers and parses JSON safely
    """
    # Remove triple backticks and optional 'json'
    cleaned = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed")
        print(cleaned)
        raise e

# -------------------------
# RUNNER
# -------------------------

async def run_adk_agent(query: str):
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name="supply_chain_app",
        user_id="news_agent_user",
        session_id="session_001"
    )

    runner = Runner(
        agent=news_agent,
        app_name="supply_chain_app",
        session_service=session_service
    )

    async for event in runner.run_async(
        user_id="news_agent_user",
        session_id="session_001",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )
    ):
        if event.is_final_response():
            print("Final response received...------------------------------")
            print(event.content)
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                data = clean_llm_json(text)
                _store_entities(data)
                # _store_entities(text)
                return data



# -------------------------
# MANUAL GRAPH WRITE (SAFE)
# -------------------------

def _store_entities(llm_output: str):
    print("Storing extracted entities...------------------------------")
    try:
        data = llm_output
    except json.JSONDecodeError:
        print("❌ Invalid JSON from LLM")
        return

    source = data.get("source", "Unknown")
    entities = data.get("entities", [])

    for entity in entities:
        graph_db.create_extracted_entity(
            name=entity.get("name"),
            entity_type=entity.get("type"),
            source=source
        )

    print(f"✅ Stored {len(entities)} entities from {source}")
