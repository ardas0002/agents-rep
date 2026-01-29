import sqlite3
import json
from typing import Type, List, Dict, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

DB_PATH = "./memory/long_term_memory_storage.db"


def init_concepts_table():
    """Initialize the learned_concepts table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learned_concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            concept_name TEXT NOT NULL,
            description TEXT,
            prerequisites TEXT,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_concepts(topic: str, concepts: List[Dict]) -> bool:
    """
    Save approved concepts to the database.

    Args:
        topic: Main topic (e.g., "SQL", "Python")
        concepts: List of dicts with keys: name, description, prerequisites (optional)

    Returns:
        True if successful, False otherwise
    """
    init_concepts_table()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for concept in concepts:
            prerequisites = json.dumps(concept.get("prerequisites", []))
            cursor.execute("""
                INSERT INTO learned_concepts (topic, concept_name, description, prerequisites)
                VALUES (?, ?, ?, ?)
            """, (
                topic.lower(),
                concept["name"],
                concept.get("description", ""),
                prerequisites
            ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving concepts: {e}")
        return False


def get_all_concepts_for_topic(topic: str) -> List[Dict]:
    """Get all learned concepts for a topic."""
    init_concepts_table()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT concept_name, description, prerequisites, learned_at
            FROM learned_concepts
            WHERE LOWER(topic) = LOWER(?)
            ORDER BY learned_at ASC
        """, (topic,))

        results = cursor.fetchall()
        conn.close()

        concepts = []
        for name, desc, prereqs, learned_at in results:
            concepts.append({
                "name": name,
                "description": desc,
                "prerequisites": json.loads(prereqs) if prereqs else [],
                "learned_at": learned_at
            })
        return concepts
    except Exception:
        return []


class ConceptSearchInput(BaseModel):
    topic: str = Field(
        description="The main topic to search for learned concepts (e.g., 'SQL', 'Python', 'JavaScript')"
    )


class ConceptSearchTool(BaseTool):
    name: str = "Search Learned Concepts"
    description: str = (
        "Search for concepts the user has already learned for a specific topic. "
        "Use this to understand the user's current knowledge level and what they already know. "
        "This helps you plan lessons that build on existing knowledge without repetition. "
        "Input should be the main topic (e.g., 'SQL', 'Python')."
    )
    args_schema: Type[BaseModel] = ConceptSearchInput

    def _run(self, topic: str) -> str:
        """Search for learned concepts in the given topic."""
        init_concepts_table()

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Search for exact topic match and similar topics
            cursor.execute("""
                SELECT DISTINCT topic, concept_name, description, prerequisites, learned_at
                FROM learned_concepts
                WHERE LOWER(topic) LIKE LOWER(?)
                ORDER BY learned_at ASC
            """, (f"%{topic}%",))

            results = cursor.fetchall()
            conn.close()

            if not results:
                return (
                    f"No learned concepts found for '{topic}'. "
                    f"This appears to be a completely new topic for the user. "
                    f"Start with foundational concepts and basics."
                )

            # Group by topic
            topics_data = {}
            for topic_name, concept, desc, prereqs, learned_at in results:
                if topic_name not in topics_data:
                    topics_data[topic_name] = []
                topics_data[topic_name].append({
                    "concept": concept,
                    "description": desc,
                    "prerequisites": json.loads(prereqs) if prereqs else [],
                    "learned_at": learned_at
                })

            output = f"Found learned concepts related to '{topic}':\n\n"

            for topic_name, concepts in topics_data.items():
                output += f"## Topic: {topic_name.upper()}\n"
                output += f"User has learned {len(concepts)} concept(s):\n\n"

                for i, c in enumerate(concepts, 1):
                    output += f"{i}. **{c['concept']}**\n"
                    if c['description']:
                        output += f"   Description: {c['description']}\n"
                    if c['prerequisites']:
                        output += f"   Prerequisites: {', '.join(c['prerequisites'])}\n"
                    output += f"   Learned: {c['learned_at']}\n\n"

            output += "\n---\n"
            output += "INSTRUCTIONS FOR PLANNING:\n"
            output += "- DO NOT repeat these concepts - the user already knows them\n"
            output += "- Build upon this existing knowledge\n"
            output += "- Suggest the next logical concepts that require these as prerequisites\n"
            output += "- If user knows basics, move to intermediate/advanced topics\n"

            return output

        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                return (
                    f"No learning history found yet for '{topic}'. "
                    f"This is the user's first session. Start with foundational concepts."
                )
            return f"Error accessing concepts database: {e}"
        except Exception as e:
            return f"Error searching concepts: {e}"
