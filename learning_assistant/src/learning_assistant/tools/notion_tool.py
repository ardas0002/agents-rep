import os
from typing import Type, Optional
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    Client = None


class NotionPublisherInput(BaseModel):
    title: str = Field(
        description="Title for the Notion page (usually the topic name)"
    )
    content: str = Field(
        description="Main lesson content in Markdown format"
    )
    exercises: str = Field(
        description="Exercises section in Markdown format"
    )
    difficulty: str = Field(
        default="intermediate",
        description="Difficulty level: beginner, intermediate, or advanced"
    )
    estimated_time: str = Field(
        default="1 hour",
        description="Estimated time to complete the lesson"
    )


class NotionPublisherTool(BaseTool):
    """
    Tool do publikowania lekcji w Notion.

    Ten tool:
    1. Łączy się z Notion API
    2. Tworzy nową stronę w określonej bazie danych
    3. Formatuje treść używając Notion blocks
    4. Zwraca URL utworzonej strony

    KONFIGURACJA (w .env):
    - NOTION_API_KEY: Token integracji Notion
    - NOTION_DATABASE_ID: ID bazy danych gdzie zapisywać lekcje

    JAK UZYSKAĆ:
    1. Idź do https://www.notion.so/my-integrations
    2. Stwórz nową integrację
    3. Skopiuj "Internal Integration Token" → NOTION_API_KEY
    4. Stwórz bazę danych w Notion
    5. Udostępnij ją integracji (... → Connections → Add)
    6. Skopiuj ID z URL bazy → NOTION_DATABASE_ID
    """

    name: str = "Publish to Notion"
    description: str = """
    Publishes lesson content and exercises to a Notion page.
    Use this tool to save the final lesson materials to Notion.

    Required inputs:
    - title: The lesson title
    - content: Main lesson content (Markdown)
    - exercises: Exercises section (Markdown)
    - difficulty: Skill level (beginner/intermediate/advanced)
    - estimated_time: How long to complete
    """
    args_schema: Type[BaseModel] = NotionPublisherInput

    def _run(
        self,
        title: str,
        content: str,
        exercises: str,
        difficulty: str = "intermediate",
        estimated_time: str = "1 hour"
    ) -> str:
        if not NOTION_AVAILABLE:
            return self._fallback_save(title, content, exercises)

        api_key = os.getenv("NOTION_API_KEY")
        database_id = os.getenv("NOTION_DATABASE_ID")

        if not api_key or not database_id:
            return self._fallback_save(title, content, exercises)

        try:
            notion = Client(auth=api_key)

            children_blocks = self._markdown_to_notion_blocks(content, exercises)

            page = notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Name": {
                        "title": [{"text": {"content": title}}]
                    },
                    "Status": {
                        "select": {"name": "To Learn"}
                    },
                    "Difficulty": {
                        "select": {"name": difficulty.capitalize()}
                    },
                    "Time": {
                        "rich_text": [{"text": {"content": estimated_time}}]
                    },
                    "Date": {
                        "date": {"start": datetime.now().strftime("%Y-%m-%d")}
                    }
                },
                children=children_blocks
            )

            page_url = page.get("url", "URL not available")
            return f"""
✅ Successfully published to Notion!

📄 Page: {title}
🔗 URL: {page_url}
📊 Difficulty: {difficulty}
⏱️ Estimated time: {estimated_time}

The lesson has been saved to your Notion database.
"""

        except Exception as e:
            # W przypadku błędu - zapisz lokalnie
            fallback_result = self._fallback_save(title, content, exercises)
            return f"""
⚠️ Notion API error: {str(e)}

{fallback_result}
"""

    def _fallback_save(self, title: str, content: str, exercises: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]

        filename = f"output/{timestamp}_{safe_title}.md"

        full_content = f"""# {title}

*Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}*

---

{content}

---

## Exercises

{exercises}
"""

        try:
            os.makedirs('output', exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_content)

            return f
        except Exception as e:
            return f"❌ Failed to save: {str(e)}"

    def _markdown_to_notion_blocks(self, content: str, exercises: str) -> list:
        blocks = []

        blocks.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "📚 Lesson Content"}}]
            }
        })

        blocks.append({"object": "block", "type": "divider", "divider": {}})

        blocks.extend(self._parse_markdown_section(content))

        blocks.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "✏️ Exercises"}}]
            }
        })

        blocks.append({"object": "block", "type": "divider", "divider": {}})

        blocks.extend(self._parse_markdown_section(exercises))

        return blocks

    def _parse_markdown_section(self, text: str) -> list:
        blocks = []
        lines = text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            if line.startswith('```'):
                language = line[3:].strip() or "plain text"
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                code_content = '\n'.join(code_lines)

                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": code_content}}],
                        "language": language if language in self._get_notion_languages() else "plain text"
                    }
                })

            elif line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })

            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })

            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })

            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })

            elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })

            elif line.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })

            i += 1

        return blocks

    def _get_notion_languages(self) -> set:
        return {
            "abap", "arduino", "bash", "basic", "c", "clojure", "coffeescript",
            "cpp", "csharp", "css", "dart", "diff", "docker", "elixir", "elm",
            "erlang", "flow", "fortran", "fsharp", "gherkin", "glsl", "go",
            "graphql", "groovy", "haskell", "html", "java", "javascript", "json",
            "julia", "kotlin", "latex", "less", "lisp", "livescript", "lua",
            "makefile", "markdown", "markup", "matlab", "mermaid", "nix",
            "objective-c", "ocaml", "pascal", "perl", "php", "plain text",
            "powershell", "prolog", "protobuf", "python", "r", "reason", "ruby",
            "rust", "sass", "scala", "scheme", "scss", "shell", "sql", "swift",
            "typescript", "vb.net", "verilog", "vhdl", "visual basic", "webassembly",
            "xml", "yaml", "java/c/c++/c#"
        }
