from agents import Agent

from sales_agent.config import AgentConfig
from sales_agent.tools.email import send_html_email

SUBJECT_WRITER_INSTRUCTIONS = """
You are an expert at writing email subject lines.
Given the body of a cold sales email, write a compelling subject line that:
- Is concise (under 60 characters)
- Creates curiosity or urgency
- Is relevant to the email content
- Avoids spam trigger words

Respond with ONLY the subject line, no quotes or explanation.
"""

HTML_CONVERTER_INSTRUCTIONS = """
You are an email HTML formatting specialist.
Convert the given text email body to clean, professional HTML.

Guidelines:
- Use simple, email-safe HTML (tables for layout if needed)
- Keep styling inline (no external CSS)
- Use a clean, readable font stack
- Add appropriate spacing and structure
- Preserve all content and meaning
- Make links clickable
- Keep it mobile-friendly

Respond with ONLY the HTML, no explanation or markdown code blocks.
"""

EMAIL_MANAGER_INSTRUCTIONS = """
You are an email formatter and sender. Your job is to take an email body and:

1. First, use the subject_writer tool to generate a compelling subject line
2. Then, use the html_converter tool to convert the body to professional HTML
3. Finally, use the send_html_email tool to send the email

Always complete all three steps in order. Report the result of the send operation.
"""


def create_subject_writer_agent(config: AgentConfig) -> Agent:
    return Agent(
        name="Subject Writer",
        instructions=SUBJECT_WRITER_INSTRUCTIONS,
        model=config.model,
    )


def create_html_converter_agent(config: AgentConfig) -> Agent:
    return Agent(
        name="HTML Converter",
        instructions=HTML_CONVERTER_INSTRUCTIONS,
        model=config.model,
    )


def create_email_manager_agent(config: AgentConfig) -> Agent:
    subject_agent = create_subject_writer_agent(config)
    html_agent = create_html_converter_agent(config)
    
    subject_tool = subject_agent.as_tool(
        tool_name="subject_writer",
        tool_description="Write a compelling subject line for a cold sales email",
    )
    
    html_tool = html_agent.as_tool(
        tool_name="html_converter",
        tool_description="Convert a text email body to professional HTML",
    )
    
    return Agent(
        name="Email Manager",
        instructions=EMAIL_MANAGER_INSTRUCTIONS,
        tools=[subject_tool, html_tool, send_html_email],
        model=config.model,
        handoff_description="Format an email as HTML and send it",
    )