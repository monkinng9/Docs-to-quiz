import openlit
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel
from typing import List, Dict, Literal, Optional, Type


# openlit.init(otlp_endpoint="http://127.0.0.1:4318")

# Create an LLM with a temperature of 0 to ensure deterministic outputs
llm = LLM(model="openrouter/deepseek/deepseek-chat", temperature=0.7)

extract_agent = Agent(
    role="Information Extractor",
	goal="To thoroughly analyze the document and study guide, identifying and extracting key information, main points, and supporting details.",
	backstory=(
		"This agent is a seasoned researcher with an insatiable curiosity and an eye for detail. They've spent years sifting through countless documents, honing their ability to discern crucial information from the noise. They are methodical and persistent, leaving no stone unturned in their quest for knowledge."
	),
    llm=llm,
    allow_delegation=True,
    verbose=True
)

syn_agent = Agent(
    role="Summary Generator and study guide creator",
	goal=" To synthesize the extracted information into concise and coherent summaries of the document and study guide.",
	backstory=(
		"This agent is a gifted communicator with a passion for clarity and conciseness. They have a knack for taking complex ideas and expressing them in simple, accessible language. They are adept at crafting summaries that are both informative and engaging."
	),
    llm=llm,
    allow_delegation=True,
    verbose=True
)

# Initialize the tool with a specific file path, so the agent can only read the content of the specified file
with open('./input/clean_content.md', 'r', encoding='utf-8') as file:
    string_source = file.read()

extract_info_task = Task(
    description=(
        "<doc>"
        "{string_source}"
        "</doc>"

        "Extract key information from the provided document and study guide."
        "This includes key concepts, arguments, evidence, data, and important quotes."
        "Identify headings and subheadings to guide extraction.")
    ,
    expected_output=(
        "A dictionary containing extracted information categorized by topic or theme."
        "Each key should represent a topic and the value should be a list of extracted data points (text or quotes) related to the topic."
    ),
    agent=extract_agent
)

class OrganizedDataItem(BaseModel):
    text: str
    source: Literal["document", "study_guide"]

class OrganizedInfo(BaseModel):
    root: Dict[str, List[OrganizedDataItem]]

organize_info_task = Task(
    description=(
        "Organize the extracted information."
        "Structure the information logically by category or theme."
        "Ensure accurate attribution to source material (document or study guide)."
    ),
    expected_output=(
        "A structured dictionary with the same keys."
        "Each value should be a list of dictionaries with keys:"
        "    - 'text': The extracted data point."
        "    - 'source': 'document' or 'study_guide' (depending on origin)."
    ),
    agent=extract_agent
)

receive_info_task = Task(
    description=(
        "Receive the structured information from the Information Extractor."
        "Understand the organization and content of the extracted data."
    ),
    expected_output=(
        "Confirmation that the information has been received and processed successfully.")
    ,
    agent=syn_agent
)

generate_summaries_task = Task(
    description=(
        "Generate concise and coherent summaries of the document and study guide."
        "Create summaries at different levels of detail (high-level overview or detailed breakdown)."
    ),
    expected_output=(
        "A dictionary with keys 'high_level_summary' and 'detailed_summary'."
        "Values should be strings containing the respective summaries."
    ),
    agent=syn_agent
)

refine_deliver_task = Task(
    description=(
        "Refine and edit the generated summaries for clarity, accuracy, and conciseness."
        "Deliver the final summaries in the desired format (e.g., text file, API response)."
    ),
    expected_output=(
        "The final, polished summaries in the desired format."
        "(Output format can be customized based on your needs)."
    ),
    agent=syn_agent
)


crew_ai = Crew(
    agents=[extract_agent, syn_agent],
    tasks=[organize_info_task, receive_info_task, generate_summaries_task, refine_deliver_task],
    process=Process.sequential,
    memory=True,
    verbose=True
)

# Execute the crew

inputs = {"string_source": string_source}

result = crew_ai.kickoff(inputs=inputs)

# Write the result to a markdown file
with open('./output/result.md', 'w', encoding='utf-8') as file:
    file.write(result)
