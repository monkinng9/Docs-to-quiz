import openlit
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional, Type
import os
import json
from datetime import datetime

openlit.init(otlp_endpoint="http://127.0.0.1:4318")

# Create an LLM with a temperature of 0 to ensure deterministic outputs
llm = LLM(model="openrouter/deepseek/deepseek-chat", temperature=0.7)

class QuizConfig(BaseModel):
    multiple_choice_count: Optional[int] = Field(None, description="Number of multiple choice questions")
    true_false_count: Optional[int] = Field(None, description="Number of true/false questions")
    short_answer_count: Optional[int] = Field(None, description="Number of short answer questions")
    scenario_count: Optional[int] = Field(None, description="Number of scenario-based questions")

    def get_config_text(self) -> str:
        config_parts = []
        if self.multiple_choice_count is not None:
            config_parts.append(f"- Multiple Choice Questions: Exactly {self.multiple_choice_count}")
        if self.true_false_count is not None:
            config_parts.append(f"- True/False Questions: Exactly {self.true_false_count}")
        if self.short_answer_count is not None:
            config_parts.append(f"- Short Answer Questions: Exactly {self.short_answer_count}")
        if self.scenario_count is not None:
            config_parts.append(f"- Scenario Questions: Exactly {self.scenario_count}")
        
        if not config_parts:
            return (
                "Determine appropriate number of questions for each type based on the content complexity "
                "and importance of different topics. Aim for a comprehensive assessment that can be "
                "completed in 30-45 minutes."
            )
        
        return "\n".join(config_parts)

class ExtractedInfo(BaseModel):
    main_concepts: List[str]
    supporting_details: Dict[str, List[str]]
    technical_terms: Dict[str, str]
    relationships: List[str]
    facts: List[str]

extract_agent = Agent(
    role="Information Extractor",
    goal="To thoroughly analyze the document and extract key information, main points, and supporting details.",
    backstory=(
        "This agent is a seasoned researcher with an insatiable curiosity and an eye for detail. They've spent years sifting through countless documents, honing their ability to discern crucial information from the noise. They are methodical and persistent, leaving no stone unturned in their quest for knowledge."
    ),
    llm=llm,
    allow_delegation=False,
    respect_context_window=True,
    verbose=True
)

writer_agent = Agent(
    role="Content Writer and Educator",
    goal="To create clear summaries, effective study guides, and engaging quizzes from technical content",
    backstory=(
        "This agent is a skilled educator with expertise in creating learning materials. "
        "They excel at breaking down complex topics into digestible pieces and creating "
        "engaging content that promotes learning and retention. They have extensive experience "
        "in instructional design and assessment creation."
    ),
    llm=llm,
    memory=True,
    allow_delegation=False,
    respect_context_window=True,
    verbose=True
)

# Get the current script's directory
input_file = "./input/doc_02_flow_content.md"

# Initialize the tool with a specific file path, so the agent can only read the content of the specified file
try:
    with open(input_file, 'r', encoding='utf-8') as file:
        string_source = file.read()
except FileNotFoundError:
    print(f"Error: Could not find {input_file}")
    raise

extract_info_task = Task(
    description=(
        "Your task is to extract key information from the following document:\n\n"
        f"{string_source}\n\n"
        "Please extract:\n"
        "1. Key concepts and main ideas\n"
        "2. Supporting details and examples\n"
        "3. Technical terms and definitions\n"
        "4. Important relationships and connections between concepts\n"
        "5. Any numerical data or specific facts\n"
        "Organize the information by sections as they appear in the document."
    ),
    expected_output=(
        "A dictionary containing extracted information with the following structure:\n"
        "{\n"
        "  'main_concepts': [list of key concepts],\n"
        "  'supporting_details': {concept: [related details]},\n"
        "  'technical_terms': {term: definition},\n"
        "  'relationships': [list of concept relationships],\n"
        "  'facts': [list of important facts and data]\n"
        "}"
    ),
    output_pydantic=ExtractedInfo,
    agent=extract_agent
)

write_summary_task = Task(
    description=(
        "Create a comprehensive summary of the document based on the extracted information.\n"
        "The summary should include:\n"
        "1. A high-level overview (2-3 paragraphs)\n"
        "2. Key takeaways (bullet points)\n"
        "3. Detailed section-by-section breakdown\n"
        "Format the summary for clarity and readability.\n"
        "Output should be in markdown format starting with '# Summary' heading."
    ),
    expected_output=(
        "A markdown formatted summary starting with '# Summary' heading, containing overview, "
        "key takeaways, and detailed section breakdowns. Do not include markdown code blocks."
    ),
    agent=writer_agent,
    output_file="./output/summary.md"
)

create_study_guide_task = Task(
    description=(
        "Create a comprehensive study guide that helps readers master the content.\n"
        "Include:\n"
        "1. Learning objectives for each major section\n"
        "2. Key concepts with explanations\n"
        "3. Important terms and definitions\n"
        "4. Example scenarios or applications\n"
        "5. Review notes and tips\n"
        "Format the study guide in markdown format starting with '# Study Guide' heading."
    ),
    expected_output=(
        "A markdown formatted study guide starting with '# Study Guide' heading, with clear sections for objectives, "
        "concepts, terms, examples, notes, and review questions. Do not include markdown code blocks."
    ),
    agent=writer_agent,
    output_file="./output/study_guide.md"
)

# Default quiz configuration - agent will determine appropriate numbers
quiz_config = QuizConfig()

"""
quiz_config = QuizConfig(
    multiple_choice_count=5,    # Exactly 5 multiple choice questions
    true_false_count=3,        # Exactly 3 true/false questions
    short_answer_count=2,      # Exactly 2 short answer questions
    scenario_count=1           # Exactly 1 scenario question
)
"""

create_quiz_task = Task(
    description=(
        "Create an assessment quiz to test understanding of the material.\n"
        "Include a mix of question types following these specifications:\n"
        f"{quiz_config.get_config_text()}\n\n"
        "Question types:\n"
        "1. Multiple choice questions\n"
        "2. True/False statements\n"
        "3. Short answer questions\n"
        "4. Scenario-based questions\n"
        "Focus on:\n"
        "- Covering key concepts from the document\n"
        "- Testing deep understanding, not just recall\n"
        "- Varying difficulty levels\n"
        "Format the quiz in markdown starting with '# Quiz Questions' heading.\n"
        "Do NOT include answer explanations in this task."
    ),
    expected_output=(
        "A markdown formatted quiz starting with '# Quiz Questions' heading, containing:\n"
        "- Clear, concise questions\n"
        "- Placeholders for answers\n"
        "- Sections for multiple choice, true/false, short answer, and scenario questions\n"
        "Questions should be numbered and clearly formatted and do not include markdown code blocks"
    ),
    agent=writer_agent,
    output_file="./output/quiz_questions.md"
)

create_quiz_answers_task = Task(
    description=(
        "Create comprehensive answer keys and explanations for the previously generated quiz.\n"
        "For each question type:\n"
        "1. Provide correct answers\n"
        "2. Write detailed explanations\n"
        "3. Reference specific parts of the source document\n"
        "4. Explain why other options are incorrect (for multiple choice)\n"
        "5. Provide additional context or learning insights\n"
        "Ensure answers are:\n"
        "- Thorough and educational\n"
        "- Directly linked to the source material\n"
        "- Helpful for understanding, not just grading\n"
        "Format the answers in markdown starting with '# Quiz Answers' heading."
    ),
    expected_output=(
        "A markdown formatted answer key starting with '# Quiz Answers' heading, containing:\n"
        "- Correct answers for each question\n"
        "- Detailed explanations\n"
        "- References to source material\n"
        "- Additional learning insights\n"
        "Answers should be clearly linked to the corresponding quiz questions.\n"
        "Do not include markdown code blocks."
    ),
    agent=writer_agent,
    output_file="./output/quiz_answers.md"
)

crew_ai = Crew(
    agents=[extract_agent, writer_agent],
    tasks=[
        extract_info_task,
        write_summary_task,
        create_study_guide_task,
        create_quiz_task,
        create_quiz_answers_task
    ],
    process=Process.sequential,
    memory=False,
    cache=True,
    verbose=True
)

# Execute the crew
result = crew_ai.kickoff()

# Write the extracted information to JSON for reference
def serialize_crew_output(obj):
    if isinstance(obj, dict):
        return {k: serialize_crew_output(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_crew_output(v) for v in obj]
    elif hasattr(obj, '__dict__'):
        return serialize_crew_output(obj.__dict__)
    else:
        return str(obj)

with open('./output/extracted_info.json', 'w', encoding='utf-8') as file:
    json.dump(serialize_crew_output(result), file, indent=4)

# Combine all markdown files into a single document
output_files = [
    './output/summary.md',
    './output/study_guide.md',
    './output/quiz_questions.md',
    './output/quiz_answers.md'
]

with open('./output/complete_document.md', 'w', encoding='utf-8') as outfile:
    outfile.write("# Document Analysis and Learning Materials\n\n")
    outfile.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
    outfile.write("---\n\n")
    
    for file_path in output_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read().strip()
                outfile.write(f"{content}\n\n")
                outfile.write("---\n\n")
        except FileNotFoundError:
            print(f"Warning: Could not find {file_path}")
            continue

# Clean up individual files
for file_path in output_files:
    try:
        os.remove(file_path)
    except FileNotFoundError:
        continue
