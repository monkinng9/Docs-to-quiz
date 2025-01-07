"""
Configuration loader for the quiz generation system.

This module handles loading and parsing YAML configurations for agents and tasks,
and creates the appropriate instances for use in the main script.
"""

import os
from typing import Dict, List
import yaml
from crewai import Agent, Task, LLM
from .models import ExtractedInfo

def load_yaml(file_path: str) -> Dict:
    """Load a YAML file and return its contents as a dictionary."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_llm(llm_config: Dict) -> LLM:
    """Create an LLM instance from configuration."""
    return LLM(
        model=llm_config['model'],
        temperature=llm_config.get('temperature', 0.7),
        base_url=llm_config.get('base_url'),
        api_key=llm_config.get('api_key')
    )

def load_agents(config_path: str) -> Dict[str, Agent]:
    """
    Load agent configurations from YAML and create Agent instances.
    
    Args:
        config_path: Path to the agents.yaml configuration file
    
    Returns:
        Dictionary mapping agent names to Agent instances
    """
    config = load_yaml(config_path)
    agents = {}
    llm_configs = config.get('llm_configs', {})
    
    # Create agent instances
    for agent_name, agent_config in config.items():
        if agent_name == 'llm_configs':
            continue
            
        # Get the LLM configuration for this agent
        llm_name = agent_config.pop('llm', None)  # Remove llm from agent_config
        if llm_name and llm_name in llm_configs:
            llm = create_llm(llm_configs[llm_name])
        else:
            # Fallback to default LLM if not specified
            llm = create_llm({
                'model': 'openrouter/google/gemini-pro-1.5',
                'temperature': 0.7
            })
        
        agents[agent_name] = Agent(
            llm=llm,
            **agent_config
        )
    
    return agents

def create_task(
    name: str,
    config: Dict,
    agents: Dict[str, Agent],
    source_content: str,
    quiz_config: str,
    output_paths: Dict[str, str],
    task_registry: Dict[str, Task] = None
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
    
    # Add context tasks if specified
    if 'context' in config and task_registry is not None:
        context_tasks = [task_registry[task_name] for task_name in config['context']]
        task_kwargs['context'] = context_tasks
    
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
) -> List[Task]:
    """
    Load task configurations from YAML and create Task instances.
    
    Args:
        config_path: Path to the tasks.yaml configuration file
        agents: Dictionary of available agents
        source_content: Content of the source document
        quiz_config: Quiz configuration text
    
    Returns:
        List of Task instances in execution order
    """
    config = load_yaml(config_path)
    output_paths = config['output_paths']
    task_configs = config['tasks']
    
    # Dictionary to store created tasks for context references
    task_registry = {}
    tasks = []
    
    # Create tasks in order of definition
    for task_name, task_config in task_configs.items():
        task = create_task(
            name=task_name,
            config=task_config,
            agents=agents,
            source_content=source_content,
            quiz_config=quiz_config,
            output_paths=output_paths,
            task_registry=task_registry
        )
        tasks.append(task)
        task_registry[task_name] = task
    
    return tasks
