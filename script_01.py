"""
Main script for processing documents and generating educational content.

This script orchestrates the document analysis, content extraction, and quiz generation
process using CrewAI agents and tasks.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, Final
import openlit
from crewai import Crew, Process

from configs.models import QuizConfig
from configs.config_loader import load_agents, load_tasks

# Constants
INPUT_FILE: Final = "./input/doc_02_flow_content.md"
OUTPUT_DIR: Final = "./output"
EXTRACTED_INFO_FILE: Final = f"{OUTPUT_DIR}/extracted_info.json"
COMBINED_OUTPUT_FILE: Final = f"{OUTPUT_DIR}/combined_output.md"
AGENTS_CONFIG: Final = "./configs/agents.yaml"
TASKS_CONFIG: Final = "./configs/tasks.yaml"

def ensure_directories_exist() -> None:
    """Create necessary directories if they don't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_source_document(file_path: str) -> str:
    """Read and return the contents of the source document."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")
        raise

def serialize_crew_output(obj: Any) -> Dict:
    """Serialize CrewAI output objects to JSON-compatible format."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [serialize_crew_output(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize_crew_output(value) for key, value in obj.items()}
    elif hasattr(obj, "__dict__"):
        return serialize_crew_output(obj.__dict__)
    else:
        return str(obj)

def combine_markdown_files() -> None:
    """Combine all generated markdown files into a single document."""
    markdown_files = [
        f"{OUTPUT_DIR}/summary.md",
        f"{OUTPUT_DIR}/study_guide.md",
        f"{OUTPUT_DIR}/quiz_questions.md",
        f"{OUTPUT_DIR}/quiz_answers.md"
    ]
    
    combined_content = []
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if content:
                    combined_content.append(content)
                    combined_content.append("\n\n---\n\n")  # Add separator
        except FileNotFoundError:
            print(f"Warning: Could not find {file_path}")
    
    if combined_content:
        with open(COMBINED_OUTPUT_FILE, 'w', encoding='utf-8') as file:
            file.write("".join(combined_content))

def main() -> None:
    """Main execution function."""
    # Ensure directories exist
    ensure_directories_exist()
    
    # Initialize OpenLit
    openlit.init(otlp_endpoint="http://127.0.0.1:4318", application_name="Disable Memory")
    
    # Read source document
    source_content = read_source_document(INPUT_FILE)
    
    # Initialize quiz configuration
    quiz_config = QuizConfig()
    
    # Load agents and tasks from configuration
    agents = load_agents(AGENTS_CONFIG)
    tasks = load_tasks(
        TASKS_CONFIG,
        agents,
        source_content,
        quiz_config.get_config_text()
    )
    
    # Create and run the crew
    crew_ai = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential
    )
    
    # Execute the crew's tasks
    result = crew_ai.kickoff()
    
    # Save extracted information
    with open(EXTRACTED_INFO_FILE, 'w', encoding='utf-8') as file:
        json.dump(serialize_crew_output(result), file, indent=4)
    
    # Combine all markdown files
    combine_markdown_files()

if __name__ == "__main__":
    main()
