from dataclasses import dataclass, field
from typing import Optional
import os


class ConfigurationError(Exception):
    pass


@dataclass(frozen=True)
class EmailConfig:
    sender_email: str
    recipient_email: str
    sendgrid_api_key: str
    
    def __post_init__(self):
        if not self.sendgrid_api_key:
            raise ConfigurationError(
                "SENDGRID_API_KEY environment variable is required. "
                "Get your API key from https://app.sendgrid.com/settings/api_keys"
            )
        if not self.sender_email:
            raise ConfigurationError("SENDER_EMAIL environment variable is required.")
        if not self.recipient_email:
            raise ConfigurationError("RECIPIENT_EMAIL environment variable is required.")


@dataclass(frozen=True)
class AgentConfig:
    model: str = "gpt-4o-mini"
    company_name: str = "ComplAI"
    company_description: str = (
        "a company that provides a SaaS tool for ensuring SOC2 compliance "
        "and preparing for audits, powered by AI"
    )


@dataclass(frozen=True)
class AppConfig:
    email: EmailConfig
    agent: AgentConfig = field(default_factory=AgentConfig)
    debug: bool = False


def load_config() -> AppConfig:
    return AppConfig(
        email=EmailConfig(
            sender_email=os.environ.get("SENDER_EMAIL", ""),
            recipient_email=os.environ.get("RECIPIENT_EMAIL", ""),
            sendgrid_api_key=os.environ.get("SENDGRID_API_KEY", ""),
        ),
        agent=AgentConfig(
            model=os.environ.get("AGENT_MODEL", "gpt-4o-mini"),
            company_name=os.environ.get("COMPANY_NAME", "ComplAI"),
            company_description=os.environ.get(
                "COMPANY_DESCRIPTION",
                "a company that provides a SaaS tool for ensuring SOC2 compliance "
                "and preparing for audits, powered by AI"
            ),
        ),
        debug=os.environ.get("DEBUG", "").lower() in ("true", "1", "yes"),
    )