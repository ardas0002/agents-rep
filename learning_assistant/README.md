# Learning Assistant
(IN DEVELOPMENT!)
AI-powered learning assistant that creates personalized lesson notes and exercises using CrewAI.

## Overview

Learning Assistant is a multi-agent system that automatically generates personalized educational content. The system uses four specialized agents working in sequence - from planning your learning path, through creating content and exercises, to publishing everything to Notion.

## Architecture

```
Learning Assistant Crew (Sequential)
├── Curriculum Planner    (analyzes learning history, plans next lesson)
├── Content Creator       (creates lesson notes with web research)
├── Exercise Generator    (generates practical exercises)
└── Notion Publisher      (publishes to Notion database)
```

## Project Structure

```
learning_assistant/
├── pyproject.toml
├── .env
└── src/
    └── learning_assistant/
        ├── main.py           # Entry point with interactive CLI
        ├── crew.py           # CrewAI agents and tasks definition
        ├── config/
        │   ├── agents.yaml   # Agent configurations
        │   └── tasks.yaml    # Task configurations
        └── tools/
            └── notion_tool.py  # Notion publishing tool
```

## Installation

Clone the repository and navigate to the project directory:

```bash
cd learning_assistant
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

Install the package in development mode:

```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key

# Notion Integration
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id

# ChromaDB (for agent memory)
CHROMA_OPENAI_API_KEY=your_openai_api_key
```

### Required API Keys

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Serper API Key**: Get from [Serper.dev](https://serper.dev/) (for web search)
- **Notion API Key**: Get from [Notion Integrations](https://www.notion.so/my-integrations)

## Usage

Make sure you have activated the virtual environment before running:

```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Using the CLI command

```bash
learning_assistant
```

### Using Python directly

```bash
python -m learning_assistant.main
```

## How It Works

1. **User provides a topic** they want to learn about
2. **Curriculum Planner** analyzes learning history (using memory) and plans the lesson structure
3. **Content Creator** searches the web and creates comprehensive lesson notes
4. **Exercise Generator** creates practical exercises to reinforce learning
5. **Notion Publisher** formats and publishes everything to your Notion database  |
6. **Memory saves** the session for future personalization                        | IN DEVELOPMENT

## Features

- **Persistent Memory** - Agents remember your learning history across sessions
- **Web Research** - Content Creator uses Serper to find up-to-date information
- **Notion Integration** - All notes are automatically published to your Notion workspace
- **Personalized Learning** - Curriculum adapts based on what you've already learned

## Dependencies

- **crewai** - Multi-agent orchestration framework
- **notion-client** - Notion API integration
- **python-dotenv** - Environment variable management

## License

MIT
