from crewai import Agent
from crewai.llm import LLM
import os

from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gemini-2.5-flash-lite",
    provider="google",
    api_key=os.getenv("GOOGLE_API_KEY")
)

risk_analyzer_agent = Agent(
    role="Supply Chain Risk Analyst",
    goal="Identify supply chain risks from events and disruptions",
    llm=llm,
    backstory="""
    You are an expert in global supply chains.
    You specialize in detecting risks from natural disasters,
    geopolitical events, and operational disruptions.
    """,
    verbose=True
)

