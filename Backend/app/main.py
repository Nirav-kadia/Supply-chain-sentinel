from fastapi import FastAPI
from pydantic import BaseModel
from app.core.graph_builder import GraphManager
from fastapi import BackgroundTasks
from app.agents.adk_news_agent import run_adk_agent
from app.api.risk_analysis import router as risk_router

app = FastAPI(title="SupplyChain Sentinel API")
graph_db = GraphManager()

class ExtractedEntityRequest(BaseModel):
    name: str
    type: str
    source: str

@app.get("/")
def health_check():
    print("enteredddd..................")
    return {"status": "running"}

@app.post("/entities")
def create_extracted_entity(entity: ExtractedEntityRequest):
    graph_db.create_extracted_entity(
        entity.name, entity.type, entity.source
    )
    return {"message": "ExtractedEntity created"}

@app.post("/resolve/{entity_type}")
def resolve_entities(entity_type: str):
    graph_db.resolve_entities(entity_type)
    return {"message": "Resolution completed"}

@app.get("/impact/supplier/{supplier_name}")
def get_supplier_impact(supplier_name: str):
    return graph_db.get_downstream_impact(supplier_name)



@app.post("/analyze/supplier/{supplier_name}")
async def analyze_supplier(
    supplier_name: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        run_adk_agent,
        f"Recent news about {supplier_name}"
    )

    return {
        "status": "News ingestion started",
        "supplier": supplier_name
    }


# app = FastAPI(title="SupplyChain Sentinel")
app.include_router(risk_router)
