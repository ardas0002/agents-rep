import asyncio
import logging
import sys
from typing import Optional

from dotenv import load_dotenv
from agents import Runner, trace

from sales_agent.config import load_config, ConfigurationError, AppConfig
from sales_agent.logging_config import setup_logging, get_logger
from sales_agent.tools.email import init_email_service
from sales_agent.agents.manager import create_sales_manager_agent


logger = get_logger(__name__)


async def run_sales_workflow(
    config: AppConfig,
    message: str,
    trace_name: str = "Automated SDR",
) -> Optional[str]:
    """
    Execute the sales email workflow.
    
    This is the core business logic, separated from initialization
    and error handling for clarity and testability.
    
    Args:
        config: Application configuration
        message: The instruction for the sales manager
        trace_name: Name for the trace (for debugging/monitoring)
        
    Returns:
        The final output from the agent, or None if failed
        
    Example:
        result = await run_sales_workflow(
            config,
            "Send a cold email to the CEO of TechCorp from Alice"
        )
    """
    init_email_service(config.email)
    
    sales_manager = create_sales_manager_agent(config.agent)
    
    logger.info("Starting sales workflow | message=%r", message)
    
    with trace(trace_name):
        result = await Runner.run(sales_manager, message)
    
    logger.info("Workflow completed | output_length=%d", len(result.final_output or ""))
    
    return result.final_output


async def main(message: Optional[str] = None) -> int:

    load_dotenv(override=True)
    
    log_level = logging.DEBUG if "--debug" in sys.argv else logging.INFO
    setup_logging(level=log_level)
    
    try:
        config = load_config()
        logger.info(
            "Configuration loaded | model=%s | company=%s",
            config.agent.model,
            config.agent.company_name,
        )
    except ConfigurationError as e:
        logger.error("Configuration error: %s", e)
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        print("\nPlease check your .env file or environment variables.", file=sys.stderr)
        return 1
    

    if message is None:
        message = "Send out a cold sales email addressed to Dear CEO from Alice"
    
    try:
        # Run the workflow
        result = await run_sales_workflow(config, message)
        
        # Print the result
        print("\n" + "=" * 60)
        print("WORKFLOW RESULT")
        print("=" * 60)
        print(result)
        print("=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        logger.exception("Workflow failed with unexpected error")
        print(f"\n❌ Workflow Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)