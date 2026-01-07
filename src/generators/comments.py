"""
Generate comments, custom fields, tags, and attachments.
"""
import uuid
import random
import logging
from datetime import datetime, timedelta

from src.utils.db import Database
from src.utils.patterns import (COMMENT_TEMPLATES, STATUSES, BLOCKERS, OUTCOMES, 
                                QUESTIONS, CUSTOM_FIELDS_BY_TEAM_TYPE, ORGANIZATION_TAGS)
from src.utils.distributions import (select_random_subset, random_int_in_range,
                                    sample_n_from_list)
from src import config

logger = logging.getLogger(__name__)


def generate_comments(db: Database) -> None:
    """
    Generate comments on tasks.
    
    Args:
        db: Database instance
    """
    logger.info("Generating comments...")
    
    cursor = db.connection.cursor()
    
    # Get tasks that should have comments
    cursor.execute("""
        SELECT t.task_id, t.created_at, t.assignee_id, t.created_by, t.project_id
        FROM tasks t
        WHERE t.parent_task_id IS NULL
        ORDER BY RANDOM()
        LIMIT ?
    """, (int(config.NUM_TASKS * config.COMMENT_RATE),))
    
    tasks_with_comments = cursor.fetchall()
    
    comments_data = []
    
    for task_id, task_created_at, assignee_id, created_by, project_id in tasks_with_comments:
        # Get team members for this project
        cursor.execute("""
            SELECT DISTINCT u.user_id
            FROM users u
            JOIN team_memberships tm ON u.user_id = tm.user_id
            JOIN projects p ON tm.team_id = p.team_id
            WHERE p.project_id = ?
        """, (project_id,))
        team_members = [row[0] for row in cursor.fetchall()]
        
        if not team_members:
            continue
        
        num_comments = random_int_in_range(
            config.COMMENTS_PER_TASK[0],
            config.COMMENTS_PER_TASK[1],
            distribution='lower_weighted'
        )
        
        task_created = datetime.fromisoformat(str(task_created_at))
        
        for i in range(num_comments):
            comment_id = f"comment_{uuid.uuid4().hex[:12]}"
            
            # Comment author (bias toward assignee and creator)
            if assignee_id and random.random() < 0.6:
                user_id = assignee_id
            elif random.random() < 0.3:
                user_id = created_by
            else:
                user_id = random.choice(team_members)
            
            # Comment created after task creation
            days_since_creation = max(0, (datetime.now() - task_created).days)
            
            if days_since_creation <= 0:
                # Task created today or in the future - comment within hours
                hours_after = random.uniform(0.5, 12)
                comment_created_at = task_created + timedelta(hours=hours_after)
            else:
                # Task created earlier - comment within days
                days_after = random.randint(0, min(30, days_since_creation))
                hours_after = random.randint(1, 23)
                comment_created_at = task_created + timedelta(days=days_after, hours=hours_after)
            
            # Generate comment text
            comment_text = generate_comment_text()
            
            # 5% of comments are pinned
            is_pinned = random.random() < 0.05
            
            comments_data.append({
                'comment_id': comment_id,
                'task_id': task_id,
                'user_id': user_id,
                'comment_text': comment_text,
                'created_at': comment_created_at,
                'is_pinned': is_pinned
            })
    
    db.insert_many('comments', comments_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(comments_data)} comments")


def generate_comment_text() -> str:
    """Generate realistic comment text."""
    template = random.choice(COMMENT_TEMPLATES)
    
    comment = template
    if '{status}' in comment:
        comment = comment.replace('{status}', random.choice(STATUSES))
    if '{section}' in comment:
        comment = comment.replace('{section}', random.choice(['To Do', 'In Progress', 'Done']))
    if '{blocker}' in comment:
        comment = comment.replace('{blocker}', random.choice(BLOCKERS))
    if '{team}' in comment:
        comment = comment.replace('{team}', random.choice(['Engineering', 'Design', 'Product']))
    if '{outcome}' in comment:
        comment = comment.replace('{outcome}', random.choice(OUTCOMES))
    if '{question}' in comment:
        comment = comment.replace('{question}', random.choice(QUESTIONS))
    if '{issue}' in comment:
        comment = comment.replace('{issue}', 'performance degradation')
    if '{reason}' in comment:
        comment = comment.replace('{reason}', random.choice(['technical complexity', 'blocked by dependencies', 'scope increased']))
    if '{url}' in comment:
        comment = comment.replace('{url}', 'https://github.com/repo/pull/123')
    if '{aspect}' in comment:
        comment = comment.replace('{aspect}', random.choice(['requirements', 'timeline', 'approach']))
    if '{hours}' in comment:
        comment = comment.replace('{hours}', str(random.randint(2, 16)))
    if '{dependency}' in comment:
        comment = comment.replace('{dependency}', 'Task #456')
    if '{person}' in comment:
        comment = comment.replace('{person}', 'team member')
    
    return comment


def generate_custom_fields(db: Database) -> None:
    """
    Generate custom field definitions and values.
    
    Args:
        db: Database instance
    """
    logger.info("Generating custom fields...")
    
    cursor = db.connection.cursor()
    
    # Get all projects with their team types
    cursor.execute("""
        SELECT p.project_id, t.team_type
        FROM projects p
        JOIN teams t ON p.team_id = t.team_id
    """)
    projects = cursor.fetchall()
    
    field_definitions = []
    field_values = []
    
    for project_id, team_type in projects:
        # Get custom fields for this team type
        if team_type in CUSTOM_FIELDS_BY_TEAM_TYPE:
            available_fields = CUSTOM_FIELDS_BY_TEAM_TYPE[team_type]
        else:
            available_fields = CUSTOM_FIELDS_BY_TEAM_TYPE['default']
        
        # Each project gets 1-4 custom fields
        num_fields = random_int_in_range(
            config.CUSTOM_FIELDS_PER_PROJECT[0],
            config.CUSTOM_FIELDS_PER_PROJECT[1]
        )
        
        selected_fields = sample_n_from_list(available_fields, num_fields)
        
        for field_def in selected_fields:
            field_id = f"field_{uuid.uuid4().hex[:12]}"
            
            dropdown_options = None
            if field_def['type'] == 'dropdown':
                dropdown_options = ','.join(field_def['options'])
            
            field_definitions.append({
                'field_id': field_id,
                'project_id': project_id,
                'field_name': field_def['name'],
                'field_type': field_def['type'],
                'dropdown_options': dropdown_options,
                'created_at': datetime.now()
            })
            
            # Get tasks for this project
            cursor.execute("""
                SELECT task_id FROM tasks WHERE project_id = ? AND parent_task_id IS NULL
            """, (project_id,))
            task_ids = [row[0] for row in cursor.fetchall()]
            
            # 50% of tasks get custom field values
            tasks_to_fill = select_random_subset(task_ids, config.CUSTOM_FIELD_FILL_RATE)
            
            for task_id in tasks_to_fill:
                value_id = f"value_{uuid.uuid4().hex[:12]}"
                
                # Generate value based on field type
                if field_def['type'] == 'dropdown':
                    value = random.choice(field_def['options'])
                elif field_def['type'] == 'number':
                    value = str(random.randint(1000, 50000))
                elif field_def['type'] == 'text':
                    value = f"Value {random.randint(1, 100)}"
                elif field_def['type'] == 'checkbox':
                    value = str(random.choice([True, False]))
                else:
                    value = "N/A"
                
                field_values.append({
                    'value_id': value_id,
                    'task_id': task_id,
                    'field_id': field_id,
                    'value': value
                })
    
    db.insert_many('custom_field_definitions', field_definitions)
    db.insert_many('custom_field_values', field_values)
    db.commit()
    
    logger.info(f"[OK] Generated {len(field_definitions)} custom field definitions")
    logger.info(f"[OK] Generated {len(field_values)} custom field values")


def generate_tags(db: Database, organization_id: str) -> None:
    """
    Generate tags and task-tag associations.
    
    Args:
        db: Database instance
        organization_id: Organization ID
    """
    logger.info("Generating tags...")
    
    tags_data = []
    
    # Create organization-wide tags
    for tag_name in ORGANIZATION_TAGS[:config.NUM_TAGS]:
        tag_id = f"tag_{uuid.uuid4().hex[:12]}"
        color = random.choice(config.ASANA_COLORS)
        
        tags_data.append({
            'tag_id': tag_id,
            'organization_id': organization_id,
            'name': tag_name,
            'color': color,
            'created_at': datetime.now()
        })
    
    db.insert_many('tags', tags_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(tags_data)} tags")
    
    # Assign tags to tasks
    logger.info("Assigning tags to tasks...")
    
    cursor = db.connection.cursor()
    
    # Get all task IDs
    cursor.execute("SELECT task_id FROM tasks WHERE parent_task_id IS NULL")
    task_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all tag IDs
    cursor.execute("SELECT tag_id FROM tags")
    tag_ids = [row[0] for row in cursor.fetchall()]
    
    # 25% of tasks get tags
    tasks_to_tag = select_random_subset(task_ids, config.TASK_TAG_RATE)
    
    task_tags_data = []
    
    for task_id in tasks_to_tag:
        num_tags = random_int_in_range(
            config.TAGS_PER_TASK[0],
            config.TAGS_PER_TASK[1],
            distribution='lower_weighted'
        )
        
        selected_tags = sample_n_from_list(tag_ids, num_tags, replace=False)
        
        for tag_id in selected_tags:
            task_tags_data.append({
                'task_id': task_id,
                'tag_id': tag_id,
                'created_at': datetime.now()
            })
    
    db.insert_many('task_tags', task_tags_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(task_tags_data)} task-tag associations")


def generate_attachments(db: Database) -> None:
    """
    Generate attachment records.
    
    Args:
        db: Database instance
    """
    logger.info("Generating attachments...")
    
    cursor = db.connection.cursor()
    
    # Get tasks that should have attachments
    cursor.execute("""
        SELECT task_id, created_by, created_at
        FROM tasks
        WHERE parent_task_id IS NULL
        ORDER BY RANDOM()
        LIMIT ?
    """, (int(config.NUM_TASKS * config.ATTACHMENT_RATE),))
    
    tasks_with_attachments = cursor.fetchall()
    
    attachments_data = []
    
    file_types = ['pdf', 'docx', 'xlsx', 'png', 'jpg', 'zip', 'csv']
    file_names = [
        'requirements.pdf', 'design_mockup.png', 'data_export.csv',
        'presentation.pptx', 'screenshot.png', 'documentation.pdf',
        'report.xlsx', 'architecture.png', 'contract.pdf'
    ]
    
    for task_id, uploaded_by, task_created_at in tasks_with_attachments:
        num_attachments = random_int_in_range(
            config.ATTACHMENTS_PER_TASK[0],
            config.ATTACHMENTS_PER_TASK[1],
            distribution='lower_weighted'
        )
        
        task_created = datetime.fromisoformat(str(task_created_at))
        
        for _ in range(num_attachments):
            attachment_id = f"attachment_{uuid.uuid4().hex[:12]}"
            
            file_name = random.choice(file_names)
            file_type = file_name.split('.')[-1]
            file_size_bytes = random.randint(10000, 5000000)  # 10KB to 5MB
            
            # Attachment uploaded shortly after task creation
            days_since_creation = max(0, (datetime.now() - task_created).days)
            
            if days_since_creation <= 0:
                # Task created today or in the future - upload within hours
                hours_after = random.uniform(0.5, 12)
                uploaded_at = task_created + timedelta(hours=hours_after)
            else:
                # Task created earlier - upload within 14 days
                days_after = random.randint(0, min(14, days_since_creation))
                uploaded_at = task_created + timedelta(days=days_after)
            
            attachments_data.append({
                'attachment_id': attachment_id,
                'task_id': task_id,
                'uploaded_by': uploaded_by,
                'file_name': file_name,
                'file_type': file_type,
                'file_size_bytes': file_size_bytes,
                'download_url': f'https://cdn.asana.com/files/{attachment_id}',
                'created_at': uploaded_at
            })
    
    db.insert_many('attachments', attachments_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(attachments_data)} attachments")
