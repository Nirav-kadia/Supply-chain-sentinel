from crewai import Task
from app.agents.crew.impact_scorer import impact_scorer_agent

impact_scoring_task = Task(
    description="""
    Given supply chain mappings and risks,
    assign an impact score from 1 to 5.
    """,
    expected_output="""
    A list of risks with impact score and explanation.
    """,
    agent=impact_scorer_agent
)
