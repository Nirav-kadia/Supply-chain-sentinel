from fastapi import APIRouter
from app.sevices.crew_service import run_supply_chain_analysis
from app.agents.adk_news_agent import run_adk_agent

router = APIRouter(prefix="/analyze", tags=["Risk Analysis"])

@router.post("/risk/{supplier_name}")
async def analyze_supplier_risk(supplier_name: str):
    print("Starting full risk analysis pipeline...********************************111111111111111")
    """
    Full pipeline:
    ADK → CrewAI → Neo4j
    """

    # 1️⃣ Run ADK agent
    adk_result = await run_adk_agent(
        f"Find supply chain disruptions related to {supplier_name}"
    )

    # adk_result should already be structured
    entities = adk_result.get("entities", [])

    # 2️⃣ Run CrewAI
    crew_result = run_supply_chain_analysis(entities)

    return {
        "supplier": supplier_name,
        "analysis": crew_result
    }
