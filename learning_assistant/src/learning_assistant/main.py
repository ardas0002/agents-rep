import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from learning_assistant.crew import LearningAssistantCrew

load_dotenv()
os.makedirs('output', exist_ok=True)


def run():
    today = datetime.now()

    inputs = {
        'topic': 'Python asyncio and asynchronous programming',
        'skill_level': 'intermediate',
        'time_available': '1 hour',
        'today_date': today.strftime('%B %d, %Y'),
        'current_year': str(today.year)
    }

    print("\n" + "=" * 60)
    print("LEARNING ASSISTANT - Starting session")
    print("=" * 60)
    print(f"Topic: {inputs['topic']}")
    print(f"Level: {inputs['skill_level']}")
    print(f"Time: {inputs['time_available']}")
    print(f"Date: {inputs['today_date']}")
    print("=" * 60 + "\n")

    try:
        result = LearningAssistantCrew().crew().kickoff(inputs=inputs)

        print("\n" + "=" * 60)
        print("SESSION COMPLETED!")
        print("=" * 60)
        print("\nSummary:")
        print(result.raw)
        print("\nBackup saved to: output/last_session.md\n")

    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nPossible issues:")
        print("  - Missing API keys in .env file")
        print("  - Rate limit exceeded (wait a minute and try again)")
        print("  - Network connection issues")
        sys.exit(1)


def interactive():
    print("\nLEARNING ASSISTANT - Interactive Mode\n")

    topic = input("What do you want to learn about? > ").strip()
    if not topic:
        print("No topic provided. Exiting.")
        return

    level = input("Your skill level (beginner/intermediate/advanced) [intermediate]: ").strip()
    if not level:
        level = "intermediate"

    time = input("Available time (e.g., '1 hour', '30 minutes') [1 hour]: ").strip()
    if not time:
        time = "1 hour"

    today = datetime.now()
    inputs = {
        'topic': topic,
        'skill_level': level,
        'time_available': time,
        'today_date': today.strftime('%B %d, %Y'),
        'current_year': str(today.year)
    }

    print("\n" + "=" * 60)
    print("Starting learning session...")
    print("=" * 60 + "\n")

    result = LearningAssistantCrew().crew().kickoff(inputs=inputs)
    print("\nDone!\n")
    print(result.raw)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--interactive', '-i']:
        interactive()
    else:
        run()
