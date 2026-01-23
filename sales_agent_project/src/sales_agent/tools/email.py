"""
Email sending tool for the agent system.

WHY separate this into its own module:
- Single Responsibility: This module only handles email sending
- Testability: Can be tested independently with mocked SendGrid client
- Reusability: Could be used by other parts of the system
- Encapsulation: SendGrid-specific logic is contained here
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

from agents import function_tool

from sales_agent.config import EmailConfig
from sales_agent.logging_config import get_logger


logger = get_logger(__name__)


class EmailStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class EmailResult:
    status: EmailStatus
    message: str
    status_code: Optional[int] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dict for tool return value."""
        result = {
            "status": self.status.value,
            "message": self.message,
        }
        if self.status_code is not None:
            result["status_code"] = self.status_code
        if self.error is not None:
            result["error"] = self.error
        return result


class EmailService:
   
    def __init__(self, config: EmailConfig):
        self._config = config
        self._client = sendgrid.SendGridAPIClient(api_key=config.sendgrid_api_key)
    
    def send_html_email(
        self,
        subject: str,
        html_body: str,
        to_email: Optional[str] = None,
    ) -> EmailResult:
        recipient = to_email or self._config.recipient_email
        
        logger.info(
            "Sending email | subject=%r | to=%s | body_length=%d",
            subject,
            recipient,
            len(html_body),
        )
        
        try:
            mail = Mail(
                from_email=Email(self._config.sender_email),
                to_emails=To(recipient),
                subject=subject,
                html_content=Content("text/html", html_body),
            )
            
            response = self._client.client.mail.send.post(
                request_body=mail.get()
            )
            
            return self._handle_response(response)
            
        except sendgrid.exceptions.SendGridException as e:
            return self._handle_sendgrid_error(e)
        except Exception as e:
            return self._handle_unexpected_error(e)
    
    def _handle_response(self, response) -> EmailResult:
        status_code = response.status_code
        
        if status_code == 202:
            logger.info("Email accepted by SendGrid | status_code=%d", status_code)
            return EmailResult(
                status=EmailStatus.SUCCESS,
                message="Email accepted by SendGrid for delivery",
                status_code=status_code,
            )
        
        # Non-202 status codes indicate issues
        error_body = self._extract_error_body(response)
        logger.error(
            "SendGrid returned non-success status | status_code=%d | error=%s",
            status_code,
            error_body,
        )
        return EmailResult(
            status=EmailStatus.ERROR,
            message=f"SendGrid returned status {status_code}",
            status_code=status_code,
            error=error_body,
        )
    
    @staticmethod
    def _extract_error_body(response) -> str:
        try:
            if response.body:
                return response.body.decode("utf-8")
        except Exception:
            pass
        return "No error details available"
    
    def _handle_sendgrid_error(self, error: sendgrid.exceptions.SendGridException) -> EmailResult:
        logger.exception("SendGrid API error occurred")
        return EmailResult(
            status=EmailStatus.ERROR,
            message="SendGrid API error",
            error=str(error),
            status_code=getattr(error, "status_code", None),
        )
    
    def _handle_unexpected_error(self, error: Exception) -> EmailResult:
        logger.exception("Unexpected error while sending email")
        return EmailResult(
            status=EmailStatus.ERROR,
            message="Unexpected error occurred",
            error=str(error),
        )


# Module-level service instance (will be initialized in main.py)
_email_service: Optional[EmailService] = None


def init_email_service(config: EmailConfig) -> None:
    global _email_service
    _email_service = EmailService(config)


@function_tool
def send_html_email(subject: str, html_body: str) -> dict:
    if _email_service is None:
        logger.error("Email service not initialized - call init_email_service first")
        return {
            "status": "error",
            "error": "Email service not initialized",
        }
    
    result = _email_service.send_html_email(subject, html_body)
    return result.to_dict()