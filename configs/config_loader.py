"""Configuration loader for YAML-based settings."""

import os
from typing import Any, Dict
import yaml
from crewai import Agent, LLM, Task
from .models import ExtractedInfo

def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_llm(config: Dict[str, Any]) -> LLM:
    """Create an LLM instance from configuration."""
    return LLM(**config)

def create_agent(config: Dict[str, Any], llm: LLM) -> Agent:
    """Create an Agent instance from configuration."""
    return Agent(
        llm=llm,
        **config
    )

def load_agents(config_path: str = "configs/agents.yaml") -> Dict[str, Agent]:
    """Load and create all agents from configuration."""
    config = load_yaml(config_path)
    
    # Create LLM
    llm = create_llm(config['llm'])
    
    # Create agents
    agents = {}
    for agent_name, agent_config in config.items():
        if agent_name != 'llm':
            agents[agent_name] = create_agent(agent_config, llm)
    
    return agents

def create_task(
    name: str,
    config: Dict[str, Any],
    agents: Dict[str, Agent],
    source_content: str,
    quiz_config: str,
    output_paths: Dict[str, str]
) -> Task:
    """Create a Task instance from configuration."""
    # Format the description template with source content and quiz config
    description = config['description_template'].format(
        source_content=source_content,
        quiz_config=quiz_config
    )
    
    # Get the agent
    agent = agents[config['agent']]
    
    # Create task kwargs
    task_kwargs = {
        'description': description,
        'expected_output': config['expected_output'],
        'agent': agent
    }
    
    # Add output file if specified
    if 'output_file' in config:
        output_file = config['output_file']
        # Replace the placeholder with actual path
        for key, value in output_paths.items():
            placeholder = "{output_paths." + key + "}"
            output_file = output_file.replace(placeholder, value)
        task_kwargs['output_file'] = output_file
    
    # Add output_pydantic for extract_info task
    if name == 'extract_info':
        task_kwargs['output_pydantic'] = ExtractedInfo
    
    return Task(**task_kwargs)

def load_tasks(
    config_path: str,
    agents: Dict[str, Agent],
    source_content: str,
    quiz_config: str
) -> list[Task]:
    """Load and create all tasks from configuration."""
    config = load_yaml(config_path)
    output_paths = config['output_paths']
    
    tasks = []
    task_order = ['extract_info', 'write_summary', 'create_study_guide', 'create_quiz', 'create_quiz_answers']
    
    for task_name in task_order:
        if task_name in config['tasks']:
            task = create_task(
                task_name,
                config['tasks'][task_name],
                agents,
                source_content,
                quiz_config,
                output_paths
            )
            tasks.append(task)
    
    return tasks
