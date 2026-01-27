import json
from app.core.graph_builder import GraphManager
import json
import re

# Mock implementation since google.adk was removed due to version conflicts
# This is a temporary workaround for Docker deployment

graph_db = GraphManager()

async def run_adk_agent(query: str):
    """
    Mock implementation of ADK agent
    Returns empty result to prevent import errors
    """
    print(f"Mock ADK agent called with query: {query}")
    return {
        "source": "Mock",
        "entities": []
    }
