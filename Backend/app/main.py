from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import BackgroundTasks
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SupplyChain Sentinel API")

# Initialize components with error handling
try:
    from app.core.graph_builder import GraphManager
    from app.agents.adk_news_agent import run_adk_agent
    from app.api.risk_analysis import router as risk_router
    
    graph_db = GraphManager()
    app.include_router(risk_router)
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing components: {e}")
    graph_db = None

class ExtractedEntityRequest(BaseModel):
    name: str
    type: str
    source: str

@app.get("/")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "running", "service": "SupplyChain Sentinel API"}

@app.get("/health")
def detailed_health_check():
    """Detailed health check for debugging"""
    health_status = {
        "status": "running",
        "service": "SupplyChain Sentinel API",
        "components": {
            "graph_db": graph_db is not None,
            "api_router": True
        }
    }
    logger.info(f"Detailed health check: {health_status}")
    return health_status

@app.post("/entities")
def create_extracted_entity(entity: ExtractedEntityRequest):
    if graph_db is None:
        return {"error": "Graph database not initialized"}
    
    graph_db.create_extracted_entity(
        entity.name, entity.type, entity.source
    )
    return {"message": "ExtractedEntity created"}

@app.post("/resolve/{entity_type}")
def resolve_entities(entity_type: str):
    if graph_db is None:
        return {"error": "Graph database not initialized"}
    
    graph_db.resolve_entities(entity_type)
    return {"message": "Resolution completed"}

@app.get("/impact/supplier/{supplier_name}")
def get_supplier_impact(supplier_name: str):
    if graph_db is None:
        return {"error": "Graph database not initialized"}
    
    return graph_db.get_downstream_impact(supplier_name)

@app.post("/analyze/supplier/{supplier_name}")
async def analyze_supplier(
    supplier_name: str,
    background_tasks: BackgroundTasks
):
    try:
        background_tasks.add_task(
            run_adk_agent,
            f"Recent news about {supplier_name}"
        )
        return {
            "status": "News ingestion started",
            "supplier": supplier_name
        }
    except Exception as e:
        logger.error(f"Error in analyze_supplier: {e}")
        return {"error": "Service temporarily unavailable"}
