import sqlite3
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class MemorySearchInput(BaseModel):
    query: str = Field(
        description="Search query - topic or keyword to search for in learning history"
    )


class MemorySearchTool(BaseTool):
    name: str = "Search Learning History"
    description: str = (
        "Search through the user's previous learning sessions. "
        "Use this to check what topics the user has already studied, "
        "to avoid repetition and build upon existing knowledge. "
        "Input should be a topic or keyword to search for."
    )
    args_schema: Type[BaseModel] = MemorySearchInput

    def _run(self, query: str) -> str:
        """Search the long-term memory database for previous learning sessions."""
        db_path = "./memory/long_term_memory_storage.db"

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, task_description, metadata, datetime
                FROM long_term_memories
                WHERE LOWER(task_description) LIKE LOWER(?)
                   OR LOWER(metadata) LIKE LOWER(?)
                ORDER BY datetime DESC
                LIMIT 10
            """, (f"%{query}%", f"%{query}%"))

            results = cursor.fetchall()
            conn.close()

            if not results:
                return f"No previous learning sessions found for '{query}'. This appears to be a new topic for the user."

            output = f"Found {len(results)} previous session(s) related to '{query}':\n\n"

            for i, (id, description, metadata, datetime_str) in enumerate(results, 1):
                desc_preview = description[:500] + "..." if len(description) > 500 else description
                output += f"--- Session {i} ---\n"
                output += f"Date: {datetime_str}\n"
                output += f"Content: {desc_preview}\n\n"

            output += "\nIMPORTANT: The user has already studied this topic. Consider:\n"
            output += "- Building on existing knowledge rather than repeating basics\n"
            output += "- Focusing on advanced aspects or different angles\n"
            output += "- Suggesting related but different topics\n"

            return output

        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                return "No learning history found yet. This is the user's first session."
            return f"Error accessing memory: {e}"
        except Exception as e:
            return f"Error searching memory: {e}"
