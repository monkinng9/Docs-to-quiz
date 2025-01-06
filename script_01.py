import openlit
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel
from typing import List, Dict, Literal, Optional, Type
import os

openlit.init(otlp_endpoint="http://127.0.0.1:4318")

# Create an LLM with a temperature of 0 to ensure deterministic outputs
llm = LLM(model="openrouter/deepseek/deepseek-chat", temperature=0.7)

extract_agent = Agent(
    role="Information Extractor",
	goal="To thoroughly analyze the document and study guide, identifying and extracting key information, main points, and supporting details.",
	backstory=(
		"This agent is a seasoned researcher with an insatiable curiosity and an eye for detail. They've spent years sifting through countless documents, honing their ability to discern crucial information from the noise. They are methodical and persistent, leaving no stone unturned in their quest for knowledge."
	),
    llm=llm,
    allow_delegation=False,
    verbose=True
)

syn_agent = Agent(
    role="Summary Generator and Study Guide Creator",
	goal="To synthesize the extracted information into concise summaries and create comprehensive study guides with key concepts, questions, and learning objectives",
	backstory=(
		"This agent is a gifted educator and communicator with expertise in creating effective learning materials. They excel at crafting clear summaries and engaging study guides that help learners master complex topics. They have years of experience in instructional design and know how to structure information for optimal learning."
	),
    llm=llm,
    allow_delegation=False,
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
    string_source = ""
extract_info_task = Task(
    description=(
        "Your task is to extract key information from the following document:\n\n"
        f"{string_source}\n\n"
        "Please extract key concepts, arguments, evidence, data, and important quotes. "
        "Pay attention to headings and subheadings to guide your extraction. "
        "Organize the information by sections as they appear in the document."
    ),
    expected_output=(
        "A dictionary containing extracted information categorized by sections. "
        "Each key should represent a section title and the value should be a list of extracted data points (text or quotes) related to that section."
    ),
    agent=extract_agent
)

generate_summaries_task = Task(
    description=(
        "Generate concise summaries and a comprehensive study guide based on the processed information.\n"
        "Create three outputs:\n"
        "1. A high-level overview of the main points\n"
        "2. A detailed breakdown of each section, including subsections if present\n"
        "3. A study guide that includes:\n"
        "   - Learning objectives\n"
        "   - Key concepts and definitions\n"
        "   - Review questions\n"
        "   - Practice exercises or discussion points\n"
        "   - Important terms and concepts to remember"
    ),
    expected_output=(
        "A dictionary with keys 'high_level_summary', 'detailed_summaries', and 'study_guide'.\n"
        "The 'high_level_summary' value should be a string containing an overview.\n"
        "The 'detailed_summaries' value should be a dictionary where each key is a section title "
        "and the value is a detailed summary of that section.\n"
        "The 'study_guide' value should be a dictionary containing structured learning materials "
        "including objectives, key concepts, questions, and exercises."
    ),
    agent=syn_agent
)

refine_deliver_task = Task(
    description=(
        "Refine and polish the generated summaries and study guide.\n"
        "Ensure clarity, accuracy, and pedagogical effectiveness in the final output.\n"
        "Format the content for optimal learning experience, maintaining clear structure and organization.\n"
        "Add bullet points, numbered lists, and callouts to enhance readability and learning.\n"
        "Ensure the study guide components are well-integrated with the summaries."
    ),
    expected_output=(
        "The final, polished summaries and study guide ready for delivery, "
        "structured for effective learning and retention."
    ),
    agent=syn_agent
)

crew_ai = Crew(
    agents=[extract_agent, syn_agent],
    tasks=[extract_info_task, generate_summaries_task, refine_deliver_task],
    process=Process.sequential,
    memory=False,
    cache=True,
    verbose=True
)

# Execute the crew
result = crew_ai.kickoff()

# Write the result to a JSON file
import json

def serialize_crew_output(obj):
    if isinstance(obj, dict):
        return {k: serialize_crew_output(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_crew_output(v) for v in obj]
    elif hasattr(obj, '__dict__'):
        return serialize_crew_output(obj.__dict__)
    else:
        return str(obj)

with open('./output/result.json', 'w', encoding='utf-8') as file:
    json.dump(serialize_crew_output(result), file, indent=4)


result.raw

# # Write the result to a markdown file
with open('./output/result.md', 'w', encoding='utf-8') as file:
    file.write(result.raw)
