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

supply_chain_mapper_agent = Agent(
    role="Supply Chain Mapping Expert",
    goal="Map disruptions to affected suppliers and products",
    llm=llm,
    backstory="""
    You specialize in supply chain topology.
    You understand how raw materials, suppliers,
    manufacturers, and products are connected.
    """,
    verbose=True
)
