import os
from dotenv import load_dotenv

load_dotenv()

def run_supply_chain_analysis(entities: list):
    """
    Mock implementation of supply chain analysis
    Returns a simple response when Google API keys are not available
    """
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not google_api_key:
        print("⚠️ Google API key not available - returning mock analysis")
        return {
            "status": "mock_analysis",
            "message": "CrewAI analysis requires Google API key",
            "entities_received": len(entities),
            "entities": entities
        }
    
    # If API key is available, import and run the actual crew
    try:
        from app.agents.crew.crew_runner import supply_chain_crew
        print("Running supply chain analysis with CrewAI...")
        
        result = supply_chain_crew.kickoff(
            inputs={"entities": entities}
        )
        print(f"CrewAI result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ CrewAI analysis failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "entities_received": len(entities),
            "entities": entities
        }
