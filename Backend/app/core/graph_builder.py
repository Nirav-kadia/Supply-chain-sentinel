from neo4j import GraphDatabase
from rapidfuzz import fuzz
import os
from dotenv import load_dotenv

load_dotenv()

class GraphManager:
    def __init__(self):
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            self.driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_user, neo4j_password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print(f"✅ Connected to Neo4j at {neo4j_uri}")
        except Exception as e:
            print(f"⚠️ Neo4j connection failed: {e}")
            print("Running in mock mode - database operations will be logged only")
            self.driver = None

    def create_extracted_entity(self, name, entity_type, source):
        print(f"Creating entity: {name}, type: {entity_type}, source: {source}")
        
        if not self.driver:
            print("⚠️ Neo4j not available - entity creation skipped")
            return
            
        query = """
        CREATE (:ExtractedEntity {
            name: $name,
            type: $type,
            source: $source,
            processed: false
        })
        """
        try:
            with self.driver.session() as session:
                session.run(query, name=name, type=entity_type, source=source)
        except Exception as e:
            print(f"❌ Failed to create entity: {e}")

    def resolve_entities(self, entity_label="Supplier", threshold=85):
        if not self.driver:
            print("⚠️ Neo4j not available - entity resolution skipped")
            return
            
        fetch_query = """
        MATCH (e:ExtractedEntity {type: $label, processed: false})
        MATCH (d:Supplier)
        RETURN e.name AS extracted, d.name AS domain
        """

        try:
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
        except Exception as e:
            print(f"❌ Failed to resolve entities: {e}")

    def get_downstream_impact(self, supplier_name):
        if not self.driver:
            print("⚠️ Neo4j not available - returning empty impact data")
            return []
            
        query = """
        MATCH (s:Supplier {name: $name})
            -[:SUPPLIES]->(p:Part)
            -[:PART_OF*]->(prod:Product)
        RETURN prod.name AS product, collect(p.name) AS parts
        """
        try:
            with self.driver.session() as session:
                return [dict(record) for record in session.run(query, name=supplier_name)]
        except Exception as e:
            print(f"❌ Failed to get downstream impact: {e}")
            return []
        
def create_supply_chain_risk(self, event, supplier, product, severity):
    query = """
    MERGE (r:SupplyChainRisk {event: $event, supplier: $supplier})
    SET r.severity = $severity
    MERGE (e:Event {name: $event})
    MERGE (s:Supplier {name: $supplier})
    MERGE (p:Product {name: $product})
    MERGE (e)-[:CAUSES]->(r)
    MERGE (r)-[:AFFECTS]->(s)
    MERGE (r)-[:IMPACTS]->(p)
    """
    



