from crewai import Crew
from app.agents.crew.risk_analyzer import risk_analyzer_agent
from app.agents.crew.supply_mapper import supply_chain_mapper_agent
from app.agents.crew.tasks import supply_mapping_task
from app.agents.crew.tasks import risk_analysis_task

#3rd party impact scorer agent and task
from app.agents.crew.impact_task import impact_scoring_task
from app.agents.crew.impact_scorer import impact_scorer_agent

# risk_crew = Crew(
#     agents=[risk_analysis_task.agent],
#     tasks=[risk_analysis_task],
#     verbose=True
# )

# result = risk_crew.kickoff(
#     inputs={
#         "events": [
#             "Severe floods in Southern Thailand",
#             "Suspension of rubber production"
#         ]
#     }
# )

# print(result)

supply_chain_crew = Crew(
    agents=[
        risk_analyzer_agent,
        supply_chain_mapper_agent,
        impact_scorer_agent
    ],
    tasks=[
        risk_analysis_task,
        supply_mapping_task,
        impact_scoring_task
    ],
    verbose=True
)

result = supply_chain_crew.kickoff(
    inputs={
        "entities": [
            {"name": "Severe floods", "type": "Event"},
            {"name": "Thailand", "type": "Location"},
            {"name": "RThai Rubber Co", "type": "Supplier"},
            {"name": "Latex", "type": "Product"}
        ]
    }
)

print(result)


