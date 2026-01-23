from typing import List

from agents import Agent

from sales_agent.config import AgentConfig


def _build_base_instructions(config: AgentConfig, personality: str) -> str:
    return (
        f"You are {personality} working for {config.company_name}, "
        f"{config.company_description}. "
    )


class SalesAgentPersonality:

    PROFESSIONAL = (
        "a sales agent",
        "You write professional, serious cold emails."
    )
    ENGAGING = (
        "a humorous, engaging sales agent",
        "You write witty, engaging cold emails that are likely to get a response."
    )
    CONCISE = (
        "a busy sales agent",
        "You write concise, to the point cold emails."
    )


def create_professional_sales_agent(config: AgentConfig) -> Agent:
    role, style = SalesAgentPersonality.PROFESSIONAL
    instructions = _build_base_instructions(config, role) + style
    
    return Agent(
        name="Professional Sales Agent",
        instructions=instructions,
        model=config.model,
    )


def create_engaging_sales_agent(config: AgentConfig) -> Agent:
    role, style = SalesAgentPersonality.ENGAGING
    instructions = _build_base_instructions(config, role) + style
    
    return Agent(
        name="Engaging Sales Agent",
        instructions=instructions,
        model=config.model,
    )


def create_concise_sales_agent(config: AgentConfig) -> Agent:
    role, style = SalesAgentPersonality.CONCISE
    instructions = _build_base_instructions(config, role) + style
    
    return Agent(
        name="Concise Sales Agent",
        instructions=instructions,
        model=config.model,
    )


def create_all_sales_agents(config: AgentConfig) -> List[Agent]:
    return [
        create_professional_sales_agent(config),
        create_engaging_sales_agent(config),
        create_concise_sales_agent(config),
    ]