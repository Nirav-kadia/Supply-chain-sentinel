from crewai import Task
from app.agents.crew.risk_analyzer import risk_analyzer_agent
from app.agents.crew.supply_mapper import supply_chain_mapper_agent

risk_analysis_task = Task(
    description="""
    Analyze extracted events and determine
    if they pose a supply chain risk.
    Classify risk as Low, Medium, or High.
    """,
    expected_output="""
    A structured list of risks with severity levels.
    """,
    agent=risk_analyzer_agent
)

supply_mapping_task = Task(
    description="""
    Given extracted entities and identified risks,
    determine which suppliers and products are affected.

    Output relationships in this format:
    - Event → Supplier
    - Supplier → Product
    """,
    expected_output="""
    Structured relationships between Event, Supplier, and Product.
    """,
    agent=supply_chain_mapper_agent
)

