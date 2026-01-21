from typing import List

from agents import Agent

from sales_agent.config import AgentConfig
from sales_agent.agents.sales import create_all_sales_agents
from sales_agent.agents.email import create_email_manager_agent


SALES_MANAGER_INSTRUCTIONS = """
You are a Sales Manager at {company_name}. Your goal is to create and send the best possible cold sales email.

## Your Process

1. **Generate Drafts**: Use ALL THREE sales agent tools to generate different email drafts.
   - sales_agent_professional: For formal, business-focused emails
   - sales_agent_engaging: For witty, personality-driven emails  
   - sales_agent_concise: For brief, direct emails
   
   Do NOT proceed until you have all three drafts.

2. **Evaluate and Select**: Review all drafts and choose the SINGLE BEST email.
   Consider:
   - Clarity and professionalism
   - Likelihood to get a response
   - Appropriate tone for the recipient
   - Compelling value proposition
   
   You may regenerate drafts if none are satisfactory.

3. **Hand Off for Sending**: Pass ONLY the winning email to the 'Email Manager' agent.
   The Email Manager will handle formatting and sending.

## Critical Rules

- You MUST use the sales agent tools - do not write emails yourself
- You MUST hand off EXACTLY ONE email to the Email Manager
- You MUST wait for all three drafts before selecting
- Explain briefly why you chose the winning email
"""


def create_sales_manager_agent(config: AgentConfig) -> Agent:
    sales_agents = create_all_sales_agents(config)
      
    tool_configs = [
        ("sales_agent_professional", "Write a professional, formal cold sales email"),
        ("sales_agent_engaging", "Write a witty, engaging cold sales email"),
        ("sales_agent_concise", "Write a brief, to-the-point cold sales email"),
    ]
    
    sales_tools = [
        agent.as_tool(
            tool_name=name,
            tool_description=description,
        )
        for agent, (name, description) in zip(sales_agents, tool_configs)
    ]
    

    email_manager = create_email_manager_agent(config)
 
    instructions = SALES_MANAGER_INSTRUCTIONS.format(
        company_name=config.company_name
    )
    
    return Agent(
        name="Sales Manager",
        instructions=instructions,
        tools=sales_tools,
        handoffs=[email_manager],
        model=config.model,
    )
