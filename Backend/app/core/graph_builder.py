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

    def resolve_entities(self, entity_label="Supplier", threshold=85):
        fetch_query = """
        MATCH (e:ExtractedEntity {type: $label, processed: false})
        MATCH (d:Supplier)
        RETURN e.name AS extracted, d.name AS domain
        """

        with self.driver.session() as session:
            results = session.run(fetch_query, label=entity_label)

            for record in results:
                similarity = fuzz.WRatio(record["extracted"], record["domain"])

                if similarity >= threshold:
                    link_query = """
                    MATCH (e:ExtractedEntity {name: $e_name}),
                        (d:Supplier {name: $d_name})
                    MERGE (e)-[:REFERS_TO]->(d)
                    SET e.processed = true
                    """
                    session.run(
                        link_query,
                        e_name=record["extracted"],
                        d_name=record["domain"]
                    )

    def get_downstream_impact(self, supplier_name):
        query = """
        MATCH (s:Supplier {name: $name})
            -[:SUPPLIES]->(p:Part)
            -[:PART_OF*]->(prod:Product)
        RETURN prod.name AS product, collect(p.name) AS parts
        """
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query, name=supplier_name)]


#for testing purposes

gm = GraphManager()
gm.create_extracted_entity(
    name="Thai Rubber Example Co., Ltd.",
    entity_type="Supplier",
    source="Reuters"
)

gm.resolve_entities("Supplier")

