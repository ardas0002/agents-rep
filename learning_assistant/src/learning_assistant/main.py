import os
import re
import sys
from datetime import datetime
from dotenv import load_dotenv

from learning_assistant.crew import LearningAssistantCrew
from learning_assistant.tools.concept_tracker_tool import save_concepts, get_all_concepts_for_topic

load_dotenv()
os.makedirs('output', exist_ok=True)


def extract_concepts_from_output(output: str) -> list[dict]:
    """
    Extract concepts from the lesson output.
    Looks for '## Concepts Learned' section, exercise titles, or headings.
    """
    concepts = []
    seen_names = set()

    def add_concept(name: str, desc: str = ""):
        """Add concept if not duplicate."""
        name_lower = name.lower().strip()
        if name_lower and name_lower not in seen_names:
            seen_names.add(name_lower)
            concepts.append({"name": name.strip(), "description": desc.strip()})

    # 1. Try to find explicit "## Concepts Learned" section
    patterns = [
        r"#{1,3}\s*Concepts?\s*Learned\s*\n([\s\S]*?)(?=\n#{1,3}|\Z)",
        r"#{1,3}\s*Key\s*Concepts?\s*\n([\s\S]*?)(?=\n#{1,3}|\Z)",
        r"\*\*Concepts?\s*Learned:?\*\*\s*\n([\s\S]*?)(?=\n#{1,3}|\n\*\*|\Z)",
    ]

    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            section_content = match.group(1)
            lines = section_content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith(('-', '*', '•', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                    # Remove bullet or number
                    line = re.sub(r'^[-*•\d.)\]]+\s*', '', line).strip()
                    if ':' in line and not line.startswith('http'):
                        name, desc = line.split(':', 1)
                        add_concept(name.strip('*'), desc)
                    elif line:
                        add_concept(line.strip('*'))
            if concepts:
                return concepts

    # 2. Extract from exercise titles (### 1. Concept Name (DIFFICULTY))
    exercise_pattern = r'###\s*\d+\.\s*(.+?)\s*\((?:EASY|MEDIUM|HARD|BONUS|OPTIONAL|MEDIUM-HARD)[^)]*\)'
    exercises = re.findall(exercise_pattern, output, re.IGNORECASE)
    for ex in exercises:
        # Clean up the concept name
        name = ex.strip()
        # Remove common prefixes
        name = re.sub(r'^(Exercise|Practice|Challenge|Task)[\s:]+', '', name, flags=re.IGNORECASE)
        if name:
            add_concept(name)

    if concepts:
        return concepts

    # 3. Fall back to extracting from ## or ### headings
    headings = re.findall(r'^#{2,3}\s+(.+?)$', output, re.MULTILINE)
    skip_words = [
        'introduction', 'summary', 'conclusion', 'hands-on', 'exercises',
        'quick reference', 'best practice', 'common pitfall', 'overview',
        'concepts learned', 'key concepts', 'prerequisites', 'objectives',
        'what you', 'why', 'getting started', 'setup', 'next steps'
    ]

    for h in headings:
        h_clean = h.strip()
        h_lower = h_clean.lower()

        # Skip meta-sections
        if any(skip in h_lower for skip in skip_words):
            continue

        # Remove difficulty markers
        h_clean = re.sub(r'\s*\((?:EASY|MEDIUM|HARD|BONUS|OPTIONAL|MEDIUM-HARD)[^)]*\)', '', h_clean, flags=re.IGNORECASE)
        # Remove numbering
        h_clean = re.sub(r'^\d+\.\s*', '', h_clean)

        if h_clean and len(h_clean) > 2:
            add_concept(h_clean)

    return concepts


def show_learned_concepts(topic: str):
    """Display what concepts the user has already learned for this topic."""
    concepts = get_all_concepts_for_topic(topic)
    if concepts:
        print(f"\nYou have already learned {len(concepts)} concept(s) in {topic}:")
        for c in concepts:
            print(f"  - {c['name']}")
        print()


def approve_concepts(topic: str, concepts: list[dict]) -> list[dict]:
    """
    Show extracted concepts to user and let them approve/edit.
    Returns the approved list of concepts.
    """
    if not concepts:
        print("\nNo concepts were automatically extracted from the lesson.")
        manual = input("Enter concepts manually (comma-separated) or press Enter to skip: ").strip()
        if manual:
            return [{"name": c.strip(), "description": ""} for c in manual.split(',') if c.strip()]
        return []

    print("\n" + "=" * 60)
    print("CONCEPTS LEARNED IN THIS SESSION")
    print("=" * 60)
    print(f"\nTopic: {topic}")
    print("\nThe following concepts were covered:")
    for i, c in enumerate(concepts, 1):
        desc = f" - {c['description']}" if c['description'] else ""
        print(f"  {i}. {c['name']}{desc}")

    print("\nOptions:")
    print("  [Enter] - Approve and save all concepts")
    print("  [e]     - Edit the list")
    print("  [s]     - Skip saving")

    choice = input("\nYour choice: ").strip().lower()

    if choice == 's':
        print("Skipped saving concepts.")
        return []
    elif choice == 'e':
        print("\nEnter the concepts you want to save (comma-separated):")
        manual = input("> ").strip()
        if manual:
            return [{"name": c.strip(), "description": ""} for c in manual.split(',') if c.strip()]
        return []
    else:
        return concepts


def run():
    today = datetime.now()

    inputs = {
        'topic': 'Python asyncio and asynchronous programming',
        'time_available': '1 hour',
        'today_date': today.strftime('%B %d, %Y'),
        'current_year': str(today.year)
    }

    print("\n" + "=" * 60)
    print("LEARNING ASSISTANT - Starting session")
    print("=" * 60)
    print(f"Topic: {inputs['topic']}")
    print(f"Time: {inputs['time_available']}")
    print(f"Date: {inputs['today_date']}")
    print("=" * 60)

    show_learned_concepts(inputs['topic'])

    try:
        result = LearningAssistantCrew().crew().kickoff(inputs=inputs)

        print("\n" + "=" * 60)
        print("SESSION COMPLETED!")
        print("=" * 60)
        print("\nLesson Summary:")
        print(result.raw)

        # Extract and approve concepts
        concepts = extract_concepts_from_output(result.raw)
        approved = approve_concepts(inputs['topic'], concepts)

        if approved:
            if save_concepts(inputs['topic'], approved):
                print(f"\nSaved {len(approved)} concept(s) to your learning history!")
            else:
                print("\nFailed to save concepts.")

        print("\nBackup saved to: output/last_session.md\n")

    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nPossible issues:")
        print("  - Missing API keys in .env file")
        print("  - Rate limit exceeded (wait a minute and try again)")
        print("  - Network connection issues")
        sys.exit(1)


def interactive():
    print("\n" + "=" * 60)
    print("LEARNING ASSISTANT - Interactive Mode")
    print("=" * 60)

    topic = input("\nWhat do you want to learn about? > ").strip()
    if not topic:
        print("No topic provided. Exiting.")
        return

    # Show existing knowledge
    show_learned_concepts(topic)

    time_input = input("Available time (e.g., '1 hour', '30 minutes') [1 hour]: ").strip()
    if not time_input:
        time_input = "1 hour"

    today = datetime.now()
    inputs = {
        'topic': topic,
        'time_available': time_input,
        'today_date': today.strftime('%B %d, %Y'),
        'current_year': str(today.year)
    }

    print("\n" + "=" * 60)
    print("Starting learning session...")
    print(f"Topic: {topic}")
    print(f"Time: {time_input}")
    print("=" * 60 + "\n")

    try:
        result = LearningAssistantCrew().crew().kickoff(inputs=inputs)

        print("\n" + "=" * 60)
        print("SESSION COMPLETED!")
        print("=" * 60)
        print("\nLesson Content:")
        print(result.raw)

        # Extract and approve concepts
        concepts = extract_concepts_from_output(result.raw)
        approved = approve_concepts(topic, concepts)

        if approved:
            if save_concepts(topic, approved):
                print(f"\nSaved {len(approved)} concept(s) to your learning history!")
                print("Next time you study this topic, the assistant will build on what you've learned.")
            else:
                print("\nFailed to save concepts.")

    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nPossible issues:")
        print("  - Missing API keys in .env file")
        print("  - Rate limit exceeded (wait a minute and try again)")
        print("  - Network connection issues")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--interactive', '-i']:
        interactive()
    else:
        run()
