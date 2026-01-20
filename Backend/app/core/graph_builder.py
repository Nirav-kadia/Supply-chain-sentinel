from neo4j import GraphDatabase
from rapidfuzz import fuzz
import os
from dotenv import load_dotenv

load_dotenv()

class GraphManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(
                os.getenv("NEO4J_USER"),
                os.getenv("NEO4J_PASSWORD")
            )
        )

def create_extracted_entity(self, name, entity_type, source):
    query = """
    CREATE (:ExtractedEntity {
        name: $name,
        type: $type,
        source: $source,
        processed: false
    })
    """
    with self.driver.session() as session:
        session.run(query, name=name, type=entity_type, source=source)
