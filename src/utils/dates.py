"""
Date generation utilities with realistic patterns.
"""
import random
from datetime import datetime, timedelta
from typing import Optional


def random_date_in_range(start_date: datetime, end_date: datetime, 
                         weekday_bias: bool = True) -> datetime:
    """
    Generate random date in range with optional weekday bias.
    
    Args:
        start_date: Start of range
        end_date: End of range
        weekday_bias: If True, 70% of dates will be Mon-Wed (planning days)
    
    Returns:
        Random datetime
    """
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    
    if weekday_bias:
        # 70% chance to regenerate if it's Thu-Fri
        if random_date.weekday() >= 3 and random.random() < 0.7:
            # Try again to get Mon-Wed
            random_days = random.randint(0, delta.days)
            random_date = start_date + timedelta(days=random_days)
    
    # Add random time component (business hours: 8am-6pm)
    hour = random.randint(8, 18)
    minute = random.randint(0, 59)
    random_date = random_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return random_date


def generate_due_date(created_at: datetime, 
                     distribution_type: str,
                     avoid_weekends: bool = True) -> Optional[datetime]:
    """
    Generate realistic due date based on creation date.
    
    Args:
        created_at: When task was created
        distribution_type: 'within_week', 'within_month', 'one_to_three_months', 'no_due_date'
        avoid_weekends: If True, avoid setting due dates on Sat/Sun
    
    Returns:
        Due date or None
    """
    if distribution_type == 'no_due_date':
        return None
    
    # Generate base due date
    if distribution_type == 'within_week':
        days_ahead = random.randint(1, 7)
    elif distribution_type == 'within_month':
        days_ahead = random.randint(7, 30)
    elif distribution_type == 'one_to_three_months':
        days_ahead = random.randint(30, 90)
    else:
        days_ahead = random.randint(1, 30)
    
    due_date = created_at + timedelta(days=days_ahead)
    
    # Avoid weekends (85% of the time)
    if avoid_weekends and due_date.weekday() >= 5 and random.random() < 0.85:
        # Move to next Monday
        days_to_monday = 7 - due_date.weekday()
        due_date = due_date + timedelta(days=days_to_monday)
    
    return due_date.date()


def generate_completion_date(created_at: datetime,
                            due_date: Optional[datetime] = None,
                            now: datetime = None) -> datetime:
    """
    Generate realistic completion date using log-normal-like distribution.
    Most tasks complete quickly, some take longer.

    Args:
        created_at: When task was created
        due_date: When task is due (optional)
        now: Current time (for bounds checking)

    Returns:
        Completion datetime
    """
    if now is None:
        now = datetime.now()

    # Mean completion time: ~5 days with a long tail
    rand = random.random()
    if rand < 0.50:
        days_to_complete = random.uniform(0.5, 5)
    elif rand < 0.80:
        days_to_complete = random.uniform(5, 10)
    elif rand < 0.95:
        days_to_complete = random.uniform(10, 20)
    else:
        days_to_complete = random.uniform(20, 40)

    completed_at = created_at + timedelta(days=days_to_complete)

    # Ensure completed_at is not in the future
    if completed_at > now:
        # Task created recently but marked complete
        # Make sure it's between created_at and now
        time_since_creation = (now - created_at).total_seconds() / 3600  # hours
        if time_since_creation < 1:
            # If created less than 1 hour ago, complete it within that time
            completed_at = created_at + timedelta(hours=random.uniform(0.1, time_since_creation))
        else:
            # Complete it somewhere between creation and now
            hours_after_creation = random.uniform(1, min(48, time_since_creation))
            completed_at = created_at + timedelta(hours=hours_after_creation)

    # Add random time (business hours)
    hour = random.randint(9, 18)
    minute = random.randint(0, 59)
    completed_at = completed_at.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    # Final safety check to ensure completed_at >= created_at
    if completed_at < created_at:
        completed_at = created_at + timedelta(hours=1)

    return completed_at

def is_business_day(date: datetime) -> bool:
    """Check if date is a weekday (Mon-Fri)."""
    return date.weekday() < 5


def distribute_creation_times(start_date: datetime, 
                              end_date: datetime,
                              count: int) -> list[datetime]:
    """
    Distribute creation times across date range with realistic patterns.
    
    More tasks created:
    - Earlier in the week (Mon-Wed)
    - During business hours
    - With some randomness
    
    Args:
        start_date: Start of project/simulation
        end_date: End of project/simulation
        count: Number of timestamps to generate
    
    Returns:
        List of creation timestamps
    """
    timestamps = []
    
    for _ in range(count):
        timestamp = random_date_in_range(start_date, end_date, weekday_bias=True)
        timestamps.append(timestamp)
    
    return sorted(timestamps)


def get_sprint_boundaries(start_date: datetime, num_sprints: int = 12) -> list[datetime]:
    """
    Generate sprint boundary dates (every 2 weeks).
    Useful for clustering engineering task due dates.
    
    Args:
        start_date: When sprints begin
        num_sprints: Number of sprints to generate
    
    Returns:
        List of sprint start dates
    """
    boundaries = []
    current = start_date
    
    for i in range(num_sprints):
        boundaries.append(current)
        current = current + timedelta(days=14)  # 2-week sprints
    
    return boundaries


def cluster_date_near_target(target_date: datetime, 
                            variance_days: int = 3) -> datetime:
    """
    Generate date clustered around a target (e.g., sprint end).
    
    Args:
        target_date: Target date to cluster around
        variance_days: +/- days of variance
    
    Returns:
        Date near target
    """
    offset = random.randint(-variance_days, variance_days)
    return target_date + timedelta(days=offset)