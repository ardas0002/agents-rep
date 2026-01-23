# Sales Agent

AI-powered cold email generation and sending system using OpenAI Agents SDK.

## Overview

Sales Agent is a multi-agent system that automatically generates and sends cold emails. The system uses three specialized agents to create different email styles, then the Sales Manager selects the best version and hands it off to be sent via SendGrid.

## Architecture

```
Sales Manager
├── Professional Sales Agent  (formal, business-focused emails)
├── Engaging Sales Agent      (creative, witty emails)
├── Concise Sales Agent       (brief, to-the-point emails)
└── Email Manager             (formatting and SendGrid delivery)
```

## Project Structure

```
sales_agent_project/
├── pyproject.toml
├── .env
└── src/
    └── sales_agent/
        ├── main.py           # Entry point
        ├── config.py         # Configuration management
        ├── logging_config.py # Logging setup
        ├── agents/
        │   ├── manager.py    # Sales Manager agent
        │   ├── sales.py      # Sales agents (3 personalities)
        │   └── email.py      # Email Manager agent
        └── tools/
            └── email.py      # SendGrid email tool
```

## Installation

1. Clone the repository and navigate to the project directory:

```bash
cd sales_agent_project
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install the package in development mode:

```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=your_verified_sender@example.com
RECIPIENT_EMAIL=recipient@example.com

# Optional
AGENT_MODEL=gpt-4o-mini
COMPANY_NAME=YourCompany
COMPANY_DESCRIPTION=a company that provides...
DEBUG=false
```

### Required API Keys

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **SendGrid API Key**: Get from [SendGrid Settings](https://app.sendgrid.com/settings/api_keys)

## Usage

Make sure you have activated the virtual environment before running:

```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Using the CLI command

```bash
sales-agent
```

### Using Python directly

```bash
python -m sales_agent.main
```

### With debug logging

```bash
sales-agent --debug
```

## How It Works

1. **Sales Manager** receives a request to send a cold email
2. Calls all three sales agents to generate different email drafts:
   - Professional: formal, business-focused
   - Engaging: witty, personality-driven
   - Concise: brief, direct
3. Evaluates all drafts and selects the best one
4. Hands off the selected email to **Email Manager**
5. Email Manager formats and sends via SendGrid

## Dependencies

- `openai-agents` - OpenAI Agents SDK
- `sendgrid` - Email delivery service
- `python-dotenv` - Environment variable management

## License

MIT
