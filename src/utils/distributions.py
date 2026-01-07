"""
Distribution and statistical utility functions.
"""
import random
from typing import Any, List, Tuple


def weighted_random_choice(choices: list, weights: list) -> Any:
    """
    Select random item from choices using weights.
    
    Args:
        choices: List of items to choose from
        weights: Corresponding weights (must sum to ~1.0)
    
    Returns:
        Selected item
    """
    return random.choices(choices, weights=weights, k=1)[0]


def random_int_in_range(min_val: int, max_val: int, 
                       distribution: str = 'uniform') -> int:
    """
    Generate random integer with specified distribution.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        distribution: 'uniform' or 'lower_weighted'
    
    Returns:
        Random integer
    """
    if distribution == 'uniform':
        return random.randint(min_val, max_val)
    elif distribution == 'lower_weighted':
        # Weight toward lower values (e.g., most tasks have 1-2 subtasks, not 5)
        values = list(range(min_val, max_val + 1))
        weights = [1 / (i - min_val + 1) for i in values]
        return random.choices(values, weights=weights, k=1)[0]
    else:
        return random.randint(min_val, max_val)


def sample_n_from_list(items: list, n: int, replace: bool = False) -> list:
    """
    Sample n items from list.
    
    Args:
        items: List to sample from
        n: Number of items to sample
        replace: Whether to sample with replacement
    
    Returns:
        List of sampled items
    """
    if n >= len(items) and not replace:
        return items.copy()
    
    if replace:
        return random.choices(items, k=n)
    else:
        return random.sample(items, k=min(n, len(items)))


def pareto_sample(items: list, num_samples: int, alpha: float = 1.5) -> list:
    """
    Sample from list using Pareto (power-law) distribution.
    Items at the beginning of the list are more likely to be selected.
    
    Simulates: some users get lots of tasks, most get moderate amounts.
    
    Args:
        items: List to sample from (order matters - early items favored)
        num_samples: Number of samples to draw
        alpha: Power law exponent (1.5 is realistic)
    
    Returns:
        List of sampled items (with repetition)
    """
    if not items:
        return []
    
    n = len(items)
    # Generate Pareto weights: weight = 1 / (rank ^ alpha)
    weights = [1 / ((i + 1) ** alpha) for i in range(n)]
    
    # Normalize weights
    total = sum(weights)
    weights = [w / total for w in weights]
    
    return random.choices(items, weights=weights, k=num_samples)


def assign_with_workload_balance(assignees: list, 
                                 num_tasks: int,
                                 unassigned_rate: float = 0.15) -> list:
    """
    Assign tasks to users with realistic workload distribution.
    
    Uses Pareto principle: 20% of people do 50% of work.
    
    Args:
        assignees: List of user IDs who can be assigned
        num_tasks: Number of tasks to assign
        unassigned_rate: Fraction of tasks left unassigned
    
    Returns:
        List of assignee IDs (length = num_tasks)
    """
    num_unassigned = int(num_tasks * unassigned_rate)
    num_assigned = num_tasks - num_unassigned
    
    # Use Pareto distribution for assigned tasks
    assignments = pareto_sample(assignees, num_assigned, alpha=1.5)
    
    # Add unassigned tasks (represented as None)
    assignments.extend([None] * num_unassigned)
    
    # Shuffle to distribute randomly through task list
    random.shuffle(assignments)
    
    return assignments


def get_completion_rate(project_type: str, 
                       completion_ranges: dict) -> float:
    """
    Get realistic completion rate for a project type.
    
    Args:
        project_type: Type of project
        completion_ranges: Dict mapping project types to (min, max) tuples
    
    Returns:
        Completion rate between 0 and 1
    """
    if project_type in completion_ranges:
        min_rate, max_rate = completion_ranges[project_type]
        return random.uniform(min_rate, max_rate)
    else:
        return random.uniform(0.4, 0.6)  # Default


def should_complete_task(task_age_days: int, 
                        base_completion_rate: float) -> bool:
    """
    Determine if task should be marked complete based on age and base rate.
    Older tasks more likely to be complete.
    
    Args:
        task_age_days: How many days since task creation
        base_completion_rate: Base probability of completion
    
    Returns:
        True if task should be complete
    """
    # Age factor: older tasks more likely complete
    # 0-7 days: 0.8x rate
    # 7-30 days: 1.0x rate
    # 30+ days: 1.2x rate
    if task_age_days < 7:
        age_factor = 0.8
    elif task_age_days < 30:
        age_factor = 1.0
    else:
        age_factor = 1.2
    
    adjusted_rate = min(base_completion_rate * age_factor, 0.95)
    
    return random.random() < adjusted_rate


def select_random_subset(items: list, 
                        rate: float,
                        min_count: int = 0) -> list:
    """
    Select random subset of items based on rate.
    
    Args:
        items: List of items
        rate: Fraction to select (0.0 to 1.0)
        min_count: Minimum items to select
    
    Returns:
        Subset of items
    """
    count = max(int(len(items) * rate), min_count)
    if count >= len(items):
        return items.copy()
    return random.sample(items, count)