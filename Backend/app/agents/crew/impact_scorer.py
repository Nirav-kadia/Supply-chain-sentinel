from crewai import Agent
from crewai.llm import LLM
from dotenv import load_dotenv
import os

load_dotenv()

llm = LLM(
    model="gemini-2.5-flash-lite",
    provider="google",
    api_key=os.getenv("GOOGLE_API_KEY")
)

impact_scorer_agent = Agent(
    role="Impact Assessment Specialist",
    goal="Score the severity of supply chain risks",
    llm=llm,
    backstory="""
    You assess operational, financial, and logistical impact.
    You assign risk severity on a scale from 1 (Low) to 5 (Critical).
    """,
    verbose=True
)
