# Tool Invocation AI - Career Conversation Chatbot

A Gradio-based chatbot that acts as your professional alter-ego, answering questions about your career, background, skills, and experience. Uses OpenAI's function calling to record user details and unknown questions.

## Features

- 🤖 AI-powered chatbot representing you professionally
- 📧 Records user contact information (email, name, notes)
- ❓ Tracks questions that couldn't be answered
- 📱 Push notifications via Pushover
- 💾 SQLite database for persistent storage
- 🌐 Web interface via Gradio

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in this directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   PUSHOVER_USER=your_pushover_user_key
   PUSHOVER_TOKEN=your_pushover_token
   ```

3. **Prepare your personal information:**
   - Place your CV/Resume PDF in `me/cv.pdf`
   - Create `me/summary.txt` with a summary of your background

4. **Update the name in `app.py`:**
   Change `name = "Adrian Kąkol"` to your name (line 172)

## Running

```bash
python app.py
```

The Gradio interface will launch at `http://127.0.0.1:7860`

## Database

The application uses SQLite to store:
- **user_details**: Email, name, notes, and timestamp of users who want to get in touch
- **unknown_questions**: Questions that the chatbot couldn't answer

Database file: `career_conversation.db` (created automatically)

## Deployment

This app can be deployed to HuggingFace Spaces using:
```bash
gradio deploy
```

## Files Structure

```
tool-invokation-ai/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
└── me/
    ├── cv.pdf         # Your CV/Resume (PDF)
    └── summary.txt    # Summary of your background
```

## Notes

- Never commit `.env` files or `.db` files (they contain sensitive data)
- The database file is created automatically on first run
- Pushover is optional - the app will work without it, but won't send notifications

