"""
Generate tasks (the most critical part of the simulation).
"""
import uuid
import random
import logging
from datetime import datetime, timedelta

from src.utils.db import Database
from src.utils.patterns import generate_task_name, DESCRIPTION_TEMPLATES, CONTEXTS, BACKGROUNDS
from src.utils.dates import (generate_due_date, generate_completion_date, 
                             random_date_in_range, distribute_creation_times)
from src.utils.distributions import (assign_with_workload_balance, 
                                    get_completion_rate, should_complete_task,
                                    random_int_in_range, weighted_random_choice)
from src import config

logger = logging.getLogger(__name__)


def generate_tasks(db: Database, project_metadata: list[dict]) -> None:
    """
    Generate tasks for all projects.
    
    This is the most important function - generates realistic task data.
    
    Args:
        db: Database instance
        project_metadata: Project metadata from generate_projects
    """
    logger.info(f"Generating ~{config.NUM_TASKS} tasks...")
    
    cursor = db.connection.cursor()
    tasks_data = []
    total_tasks = 0
    
    for project in project_metadata:
        project_id = project['project_id']
        team_type = project['team_type']
        project_type = project['project_type']
        project_created_at = project['created_at']
        member_ids = project['member_ids']
        
        # Get sections for this project
        sections = cursor.execute("""
            SELECT section_id FROM sections WHERE project_id = ? ORDER BY position
        """, (project_id,)).fetchall()
        section_ids = [s[0] for s in sections]
        
        if not section_ids or not member_ids:
            continue
        
        # Determine number of tasks for this project
        task_range = config.TASKS_PER_PROJECT.get(project_type, (40, 100))
        num_tasks = random.randint(task_range[0], task_range[1])
        
        # Generate creation times distributed over project lifetime
        project_end = min(config.SIMULATION_END_DATE, 
                        project_created_at + timedelta(days=120))

        # Ensure there's at least 1 day between start and end
        if project_end <= project_created_at:
            project_end = project_created_at + timedelta(days=1)

        creation_times = distribute_creation_times(
            project_created_at, 
            project_end, 
            num_tasks
        )
        
        # Assign tasks to members with realistic distribution
        assignee_ids = assign_with_workload_balance(
            member_ids, 
            num_tasks,
            config.UNASSIGNED_TASK_RATE
        )
        
        # Get completion rate for this project type
        base_completion_rate = get_completion_rate(
            project_type,
            config.COMPLETION_RATE_BY_TYPE
        )
        
        for i in range(num_tasks):
            task_id = f"task_{uuid.uuid4().hex[:12]}"
            
            # Task name (using patterns)
            name = generate_task_name(project_type, team_type)
            
            # Description (20% empty, 50% short, 30% medium/detailed)
            description = generate_task_description()
            
            # Assignee
            assignee_id = assignee_ids[i]
            
            # Creator (random team member)
            created_by = random.choice(member_ids)
            
            # Dates
            created_at = creation_times[i]
            
            # Due date
            due_date_type = weighted_random_choice(
                list(config.DUE_DATE_DISTRIBUTION.keys()),
                list(config.DUE_DATE_DISTRIBUTION.values())
            )
            due_date = generate_due_date(created_at, due_date_type)
            
            # Start date (20% of tasks have start dates)
            start_date = None
            if due_date and random.random() < 0.20:
                days_before_due = random.randint(1, 7)
                start_date = due_date - timedelta(days=days_before_due)
            
            # Completion
            task_age_days = (datetime.now() - created_at).days
            completed = should_complete_task(task_age_days, base_completion_rate)
            
            completed_at = None
            completed_by = None
            if completed:
                completed_at = generate_completion_date(created_at, due_date)
                completed_by = assignee_id if assignee_id else created_by
            
            # Section assignment (realistic distribution)
            if completed:
                # Completed tasks in last section
                section_id = section_ids[-1]
            else:
                # Active tasks distributed across sections
                # More in middle sections (In Progress)
                if len(section_ids) >= 3:
                    section_weights = [0.2] + [0.6 / (len(section_ids) - 2)] * (len(section_ids) - 2) + [0.2]
                else:
                    section_weights = [1.0 / len(section_ids)] * len(section_ids)
                section_id = weighted_random_choice(section_ids, section_weights)
            
            tasks_data.append({
                'task_id': task_id,
                'project_id': project_id,
                'section_id': section_id,
                'parent_task_id': None,  # Top-level tasks only for now
                'name': name,
                'description': description,
                'assignee_id': assignee_id,
                'created_by': created_by,
                'due_date': due_date,
                'start_date': start_date,
                'completed': completed,
                'completed_at': completed_at,
                'completed_by': completed_by,
                'created_at': created_at,
                'modified_at': created_at
            })
            
            total_tasks += 1
            
            # Batch insert every 1000 tasks
            if len(tasks_data) >= 1000:
                db.insert_many('tasks', tasks_data)
                db.commit()
                logger.info(f"  Inserted {total_tasks} tasks...")
                tasks_data = []
    
    # Insert remaining tasks
    if tasks_data:
        db.insert_many('tasks', tasks_data)
        db.commit()
    
    logger.info(f"✓ Generated {total_tasks} tasks")


def generate_task_description() -> str:
    """Generate realistic task description."""
    desc_type = weighted_random_choice(
        ['empty', 'short', 'medium', 'detailed'],
        [0.20, 0.50, 0.25, 0.05]
    )
    
    if desc_type == 'empty':
        return ''
    
    templates = DESCRIPTION_TEMPLATES[desc_type]
    
    if desc_type == 'short':
        template = random.choice(templates)
        # Fill in placeholders
        description = template
        if '{date}' in description:
            description = description.replace('{date}', 'end of week')
        if '{hours}' in description:
            description = description.replace('{hours}', str(random.randint(2, 8)))
        if '{blocker}' in description:
            description = description.replace('{blocker}', random.choice(['other task', 'approval', 'external dependency']))
        if '{customer}' in description:
            description = description.replace('{customer}', 'Enterprise Client')
        return description
    
    elif desc_type in ['medium', 'detailed']:
        template = random.choice(templates)
        description = template
        
        # Fill in placeholders with generic content
        description = description.replace('{context}', random.choice(CONTEXTS))
        description = description.replace('{background}', random.choice(BACKGROUNDS))
        description = description.replace('{item1}', 'Review requirements')
        description = description.replace('{item2}', 'Implement changes')
        description = description.replace('{notes}', 'See attached document for details.')
        description = description.replace('{description}', 'This task involves updating the system.')
        description = description.replace('{req1}', 'Must be completed by EOW')
        description = description.replace('{req2}', 'Should follow existing patterns')
        description = description.replace('{req3}', 'Needs code review approval')
        description = description.replace('{step1}', 'Gather requirements')
        description = description.replace('{step2}', 'Implement solution')
        description = description.replace('{step3}', 'Test and deploy')
        description = description.replace('{overview}', 'High-level task overview.')
        description = description.replace('{criteria1}', 'All tests pass')
        description = description.replace('{criteria2}', 'Code reviewed')
        description = description.replace('{criteria3}', 'Documentation updated')
        description = description.replace('{resource1}', 'Design doc: [link]')
        description = description.replace('{resource2}', 'API spec: [link]')
        description = description.replace('{problem}', 'Current system has limitations.')
        description = description.replace('{solution}', 'Proposed new approach.')
        description = description.replace('{metric1}', 'Performance improvement')
        description = description.replace('{metric2}', 'User satisfaction')
        description = description.replace('{timeline}', '2-3 weeks')
        
        # Replace any remaining template variables
        for key in ['{quarter}', '{num}', '{percent}', '{project_name}', 
                   '{deadline}', '{metric}', '{standard}']:
            if key in description:
                description = description.replace(key, 'TBD')
        
        return description
    
    return ''


def generate_subtasks(db: Database) -> None:
    """
    Generate subtasks for a portion of tasks.
    
    Args:
        db: Database instance
    """
    logger.info("Generating subtasks...")
    
    # Get all tasks that could have subtasks
    cursor = db.connection.cursor()
    cursor.execute("""
        SELECT task_id, project_id, assignee_id, created_by, created_at, completed
        FROM tasks 
        WHERE parent_task_id IS NULL
        ORDER BY RANDOM()
        LIMIT ?
    """, (int(config.NUM_TASKS * config.SUBTASK_RATE),))
    
    parent_tasks = cursor.fetchall()
    
    subtasks_data = []
    
    for parent_task_id, project_id, assignee_id, created_by, created_at, parent_completed in parent_tasks:
        num_subtasks = random_int_in_range(
            config.SUBTASKS_PER_TASK[0],
            config.SUBTASKS_PER_TASK[1],
            distribution='lower_weighted'
        )
        
        for i in range(num_subtasks):
            subtask_id = f"task_{uuid.uuid4().hex[:12]}"
            
            # Subtask name (simpler than parent)
            name = f"Subtask {i+1}: {random.choice(['Research', 'Implementation', 'Testing', 'Documentation', 'Review'])}"
            
            # Subtasks created shortly after parent
            subtask_created_at = datetime.fromisoformat(str(created_at)) + timedelta(hours=random.randint(1, 48))
            
            # Subtasks inherit assignee or are assigned to other team members
            subtask_assignee = assignee_id if random.random() < 0.7 else None
            
            # Subtasks have higher completion rate
            completed = parent_completed or random.random() < 0.75
            completed_at = None
            completed_by = None
            
            if completed:
                completed_at = generate_completion_date(subtask_created_at,  None)
                completed_by = subtask_assignee if subtask_assignee else created_by
            
            subtasks_data.append({
                'task_id': subtask_id,
                'project_id': project_id,
                'section_id': None,  # Subtasks don't have sections
                'parent_task_id': parent_task_id,
                'name': name,
                'description': '',
                'assignee_id': subtask_assignee,
                'created_by': created_by,
                'due_date': None,
                'start_date': None,
                'completed': completed,
                'completed_at': completed_at,
                'completed_by': completed_by,
                'created_at': subtask_created_at,
                'modified_at': subtask_created_at
            })
    
    db.insert_many('tasks', subtasks_data)
    db.commit()
    
    logger.info(f"✓ Generated {len(subtasks_data)} subtasks")