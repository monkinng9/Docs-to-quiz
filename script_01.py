import openlit
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional, Type
import os
import json
from datetime import datetime

openlit.init(otlp_endpoint="http://127.0.0.1:4318")
# Create an LLM with a temperature of 0 to ensure deterministic outputs
google_api_key = os.getenv("GOOGLE_API_KEY")
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
        "From document:"
        f"{string_source}\n\n"
        "Create an integrated summary that serves as a foundation for the study guide and quiz.\n"
        "Structure the summary to:\n"
        "1. Begin with a concise overview (1-2 paragraphs) that introduces the main concepts\n"
        "2. Present key takeaways as actionable learning objectives\n"
        "3. Provide a detailed breakdown that:\n"
        "   - Explains concepts in a logical progression\n"
        "   - Integrates technical terms within their relevant context\n"
        "   - Demonstrates relationships between concepts using practical examples\n"
        "   - Weaves important facts naturally into the explanations\n"
        "4. Include transition sentences between sections\n"
        "5. Use clear visual hierarchy with appropriate headings and subheadings\n"
        "Format the summary in markdown starting with '# Summary' heading."
    ),
    expected_output=(
        "A markdown formatted summary with clear hierarchy, integrated concepts, and smooth transitions "
        "between sections. The summary should serve as a foundation for the study guide and quiz."
    ),
    agent=writer_agent,
    output_file="./output/summary.md"
)

create_study_guide_task = Task(
    description=(
        "Create an integrated study guide that builds upon and references the summary.\n"
        "Structure the guide to:\n"
        "1. Begin with clear learning objectives that map to the summary's key takeaways\n"
        "2. For each major concept from the summary:\n"
        "   - Provide detailed explanations with cross-references to the summary\n"
        "   - Include practical examples that demonstrate concept applications\n"
        "   - Highlight key terms in context with their relationships\n"
        "   - Add study tips and common pitfalls to avoid\n"
        "3. Include visual elements (ASCII diagrams or structured lists) to illustrate relationships\n"
        "4. End each section with review prompts that prepare for the quiz\n"
        "Format the study guide in markdown starting with '# Study Guide' heading."
    ),
    expected_output=(
        "A markdown formatted study guide that integrates with the summary, uses visual elements, "
        "and prepares readers for the quiz through targeted review prompts."
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
        "Create an assessment quiz that directly ties to the summary and study guide.\n"
        f"{quiz_config.get_config_text()}\n\n"
        "Structure the quiz to:\n"
        "1. Begin with a brief introduction connecting it to the study guide's learning objectives\n"
        "2. Include a mix of questions that:\n"
        "   - Progress from basic recall to complex application\n"
        "   - Reference specific concepts from the summary\n"
        "   - Test relationships and connections identified in the study guide\n"
        "   - Include practical scenarios based on the examples provided\n"
        "3. Group questions by topic and complexity, not just by type\n"
        "4. Use clear formatting and numbering that aids navigation\n"
        "Format the quiz in markdown starting with '# Quiz Questions' heading."
    ),
    expected_output=(
        "A markdown formatted quiz that integrates with the summary and study guide, featuring "
        "progressive complexity and clear organization by topic."
    ),
    agent=writer_agent,
    output_file="./output/quiz_questions.md"
)

create_quiz_answers_task = Task(
    description=(
        "Create comprehensive answer explanations that reinforce learning objectives.\n"
        "Structure the answers to:\n"
        "1. Begin with a brief overview of the topics covered in the quiz\n"
        "2. For each answer:\n"
        "   - Provide the correct response with detailed reasoning\n"
        "   - Cross-reference relevant sections in the summary and study guide\n"
        "   - Explain common misconceptions or incorrect answers\n"
        "   - Include additional examples or scenarios for deeper understanding\n"
        "3. End with key learning points that tie back to the original objectives\n"
        "Format answers in markdown starting with '# Quiz Answers' heading."
    ),
    expected_output=(
        "A markdown formatted answer key that reinforces learning through detailed explanations "
        "and connections to the summary and study guide."
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
