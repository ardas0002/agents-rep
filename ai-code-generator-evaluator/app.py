from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
import gradio as gr
import os

# Załaduj zmienne środowiskowe
load_dotenv(override=True)

# Inicjalizacja klientów
openai_client = OpenAI()
anthropic_client = Anthropic()


def generate_with_gpt(prompt: str) -> str:
    """Generuje kod używając GPT-4o-mini"""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert programmer. Generate clean, efficient code based on the user's requirements. Return only the code without explanations."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


def generate_with_claude(prompt: str) -> str:
    """Generuje kod używając Claude Sonnet"""
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": f"You are an expert programmer. Generate clean, efficient code based on the user's requirements. Return only the code without explanations.\n\n{prompt}"}
        ],
        temperature=0.7
    )
    return response.content[0].text


def validate_and_choose(prompt: str, gpt_code: str, claude_code: str) -> dict:
    """Waliduje oba rozwiązania i wybiera lepsze używając GPT-4o"""
    validation_prompt = f"""You are a code reviewer. Compare these two code solutions and choose the better one.

Original requirement:
{prompt}

Solution 1 (GPT):
```
{gpt_code}
```

Solution 2 (Claude):
```
{claude_code}
```

Evaluate based on:
1. Correctness - does it fulfill the requirement?
2. Code quality - readability, efficiency, best practices
3. Completeness - are edge cases handled?

Respond in this exact format:
WINNER: [GPT or CLAUDE]
REASON: [brief explanation why this solution is better]
SELECTED_CODE:
```
[paste the winning code here]
```"""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": validation_prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

def code_agent(prompt: str) -> tuple:
    """Główna funkcja agenta"""
    if not prompt.strip():
        return "Please enter a prompt", "", "", ""
    
    gpt_code = generate_with_gpt(prompt)
    
    claude_code = generate_with_claude(prompt)
    
    validation_result = validate_and_choose(prompt, gpt_code, claude_code)
    
    return gpt_code, claude_code, validation_result, "✅ Complete!"


# Interfejs Gradio
with gr.Blocks(title="AI Code Generator Agent") as demo:
    gr.Markdown("# 🤖 AI Code Generator Agent")
    gr.Markdown("Generate code using GPT and Claude, then automatically select the best solution.")
    
    with gr.Row():
        prompt_input = gr.Textbox(
            label="What code do you want to generate?",
            placeholder="Example: Create a Python function that calculates fibonacci numbers",
            lines=3
        )
    
    generate_btn = gr.Button("🚀 Generate Code", variant="primary")
    
    status_output = gr.Textbox(label="Status", interactive=False)
    
    with gr.Row():
        with gr.Column():
            gpt_output = gr.Code(label="GPT-4o-mini Solution", language="python")
        with gr.Column():
            claude_output = gr.Code(label="Claude Sonnet Solution", language="python")
    
    validation_output = gr.Markdown(label="Validation & Winner")
    
    generate_btn.click(
        fn=code_agent,
        inputs=[prompt_input],
        outputs=[gpt_output, claude_output, validation_output, status_output]
    )
    
    gr.Examples(
        examples=[
            ["Create a Python function that calculates the factorial of a number"],
            ["Write a Python class for a binary search tree with insert and search methods"],
            ["Create a function that validates email addresses using regex"],
        ],
        inputs=prompt_input
    )

if __name__ == "__main__":
    demo.launch()