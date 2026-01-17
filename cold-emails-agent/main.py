from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."

instructions ="You are an email formatter and sender. You receive the body of an email to be sent. \
You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
Finally, you use the send_html_email tool to send the email with the subject and HTML body."

sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model="gpt-4o-mini"
)

sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model="gpt-4o-mini"
)

sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model="gpt-4o-mini"
)


subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

html_instructions = "You can convert a text email body to an HTML email body. \
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
html_tool = html_converter.as_tool(tool_name="html_converter",tool_description="Convert a text email body to an HTML email body")

@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send out an email with the given subject and HTML body to all sales prospects """
    print("\n" + "="*60)
    print("FUNKCJA send_html_email WYWOŁANA")
    print("="*60)
    print(f"Subject: {subject}")
    print(f"HTML Body length: {len(html_body)} characters")
    print(f"From: adrian17159@gmail.com")
    print(f"To: adrian17159@o2.pl")
    
    try:
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            error_msg = "SENDGRID_API_KEY nie jest ustawiony!"
            print(f"ERROR: {error_msg}")
            return {"status": "error", "error": error_msg}
        
        print(f"API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '****'}")
        
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        from_email = Email("adrian17159@gmail.com")  # Change to your verified sender
        to_email = To("adrian17159@o2.pl")  # Change to your recipient
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        
        print("Wysyłanie emaila przez SendGrid...")
        response = sg.client.mail.send.post(request_body=mail)
        
        # Sprawdź status odpowiedzi
        status_code = response.status_code
        print(f"\nSendGrid response status code: {status_code}")
        
        # Sprawdź nagłówki odpowiedzi
        if hasattr(response, 'headers'):
            print(f"Response headers: {dict(response.headers)}")
        
        if status_code == 202:
            print("✓ Email zaakceptowany przez SendGrid (status 202)")
            print("UWAGA: Status 202 oznacza, że SendGrid zaakceptował email.")
            print("Jeśli email nie dociera, sprawdź:")
            print("  1. Folder SPAM w skrzynce odbiorcy")
            print("  2. Czy adres nadawcy jest zweryfikowany w SendGrid")
            print("  3. Dashboard SendGrid -> Activity Feed (sprawdź status dostarczenia)")
            print("  4. Czy adres odbiorcy jest poprawny")
            return {"status": "success", "status_code": status_code, "message": "Email zaakceptowany przez SendGrid"}
        else:
            # Próba odczytania treści odpowiedzi w przypadku błędu
            try:
                error_body = response.body.decode('utf-8') if response.body else "No error details"
                print(f"\n✗ BŁĄD wysyłania emaila!")
                print(f"Status: {status_code}")
                print(f"Szczegóły błędu: {error_body}")
            except Exception as decode_error:
                print(f"\n✗ BŁĄD wysyłania emaila!")
                print(f"Status: {status_code}")
                print(f"Nie można odczytać szczegółów błędu: {decode_error}")
            
            return {"status": "error", "status_code": status_code}
            
    except sendgrid.exceptions.SendGridException as e:
        error_msg = f"SendGrid Exception: {str(e)}"
        print(f"\n✗ BŁĄD SendGrid: {error_msg}")
        print(f"Exception type: {type(e).__name__}")
        if hasattr(e, 'body'):
            print(f"Error body: {e.body}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        return {"status": "error", "error": error_msg}
    except Exception as e:
        error_msg = f"Nieoczekiwany błąd: {str(e)}"
        print(f"\n✗ BŁĄD: {error_msg}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return {"status": "error", "error": error_msg}
    finally:
        print("="*60 + "\n")

tools = [subject_tool, html_tool, send_html_email]

emailer_agent = Agent(
    name="Email Manager",
    instructions=instructions,
    tools=tools,
    model="gpt-4o-mini",
    handoff_description="Convert an email to HTML and send it")

sales_manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
You can use the tools multiple times if you're not satisfied with the results from the first try.
 
3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must hand off exactly ONE email to the Email Manager — never more than one.
"""

description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

tools = [tool1, tool2, tool3]
handoffs = [emailer_agent]

sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini")

message = "Send out a cold sales email addressed to Dear CEO from Alice"


async def main():
    with trace("Automated SDR"):
        result = await Runner.run(sales_manager, message)
    
    print(f"\nWynik agenta: {result.final_output}")
    return result

if __name__ == "__main__":
    load_dotenv(override=True)
    asyncio.run(main())