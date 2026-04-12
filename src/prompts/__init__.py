"""Utility for loading prompts from files."""
import os
from pathlib import Path


def load_prompt(task_category: str, task_name: str) -> str:
    """
    Load a prompt from file.
    
    Args:
        task_category: Category of the task (e.g., 'system-management', 'edge-detection')
        task_name: Name of the task (e.g., 'deployment_monitoring', 'edge_detection')
    
    Returns:
        The prompt content as a string
    
    Raises:
        FileNotFoundError: If the prompt file cannot be found
    """
    prompt_path = Path(__file__).parent / task_category / f"{task_name}.txt"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, 'r') as f:
        return f.read()


def load_all_prompts(task_category: str) -> dict:
    """
    Load all prompts from a category.
    
    Args:
        task_category: Category of the tasks (e.g., 'system-management', 'edge-detection')
    
    Returns:
        Dictionary mapping task names to prompt content
    """
    category_path = Path(__file__).parent / task_category
    
    if not category_path.exists():
        raise FileNotFoundError(f"Prompt category not found: {category_path}")
    
    prompts = {}
    for prompt_file in category_path.glob("*.txt"):
        task_name = prompt_file.stem
        with open(prompt_file, 'r') as f:
            prompts[task_name] = f.read()
    
    return prompts
