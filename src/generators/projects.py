"""
Generate projects and sections.
"""
import uuid
import random
import logging
from datetime import datetime, timedelta

from src.utils.db import Database
from src.utils.patterns import generate_project_name, SECTIONS_BY_PROJECT_TYPE
from src.utils.dates import random_date_in_range
from src.utils.distributions import weighted_random_choice
from src import config

logger = logging.getLogger(__name__)


def generate_projects(db: Database) -> list[dict]:
    """
    Generate projects for all teams.
    
    Args:
        db: Database instance
    
    Returns:
        List of project dicts with metadata
    """
    logger.info(f"Generating {config.NUM_PROJECTS} projects...")
    
    # Get all teams
    cursor = db.connection.cursor()
    teams = cursor.execute("SELECT team_id, name, team_type FROM teams").fetchall()
    
    projects_per_team = config.NUM_PROJECTS // len(teams)
    
    projects_data = []
    project_metadata = []
    
    for team_id, team_name, team_type in teams:
        # Get team members for assigning project owners
        members = cursor.execute("""
            SELECT user_id FROM team_memberships WHERE team_id = ?
        """, (team_id,)).fetchall()
        member_ids = [m[0] for m in members]
        
        if not member_ids:
            continue
        
        # Determine project type distribution for this team
        if team_type in config.PROJECT_TYPE_BY_TEAM:
            type_dist = config.PROJECT_TYPE_BY_TEAM[team_type]
        else:
            type_dist = config.PROJECT_TYPE_BY_TEAM['default']
        
        project_types = list(type_dist.keys())
        type_weights = list(type_dist.values())
        
        for _ in range(projects_per_team):
            project_id = f"proj_{uuid.uuid4().hex[:12]}"
            
            # Select project type
            project_type = weighted_random_choice(project_types, type_weights)
            
            # Generate project name
            name = generate_project_name(project_type, team_name)
            
            # Project owner (random team member)
            owner_id = random.choice(member_ids)
            
            # Project status
            status_weights = {
                'active': 0.70,
                'completed': 0.15,
                'archived': 0.10,
                'on_hold': 0.05
            }
            status = weighted_random_choice(
                list(status_weights.keys()),
                list(status_weights.values())
            )
            
            # Created at
            created_at = random_date_in_range(
                config.SIMULATION_START_DATE,
                config.SIMULATION_END_DATE,
                weekday_bias=True
            )
            
            # Due date (for milestone/campaign projects)
            due_date = None
            if project_type in ['milestone', 'campaign']:
                days_ahead = random.randint(30, 120)
                due_date = (created_at + timedelta(days=days_ahead)).date()
            
            # Archived date (if archived)
            archived_at = None
            if status == 'archived':
                days_after = random.randint(60, 150)
                archived_at = created_at + timedelta(days=days_after)
            
            # Color
            color = random.choice(config.ASANA_COLORS)
            
            # Description
            description = f"{project_type.replace('_', ' ').title()} project for {team_name}"
            
            projects_data.append({
                'project_id': project_id,
                'team_id': team_id,
                'name': name,
                'description': description,
                'project_type': project_type,
                'status': status,
                'owner_id': owner_id,
                'due_date': due_date,
                'created_at': created_at,
                'archived_at': archived_at,
                'color': color,
                'is_public': True
            })
            
            # Store metadata for task generation
            project_metadata.append({
                'project_id': project_id,
                'team_id': team_id,
                'team_type': team_type,
                'project_type': project_type,
                'status': status,
                'created_at': created_at,
                'member_ids': member_ids
            })
    
    db.insert_many('projects', projects_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(projects_data)} projects")
    
    return project_metadata


def generate_sections(db: Database, project_metadata: list[dict]) -> None:
    """
    Generate sections for each project based on project type.
    
    Args:
        db: Database instance
        project_metadata: Project metadata from generate_projects
    """
    logger.info("Generating sections...")
    
    sections_data = []
    
    for project in project_metadata:
        project_id = project['project_id']
        project_type = project['project_type']
        created_at = project['created_at']
        
        # Get section names for this project type
        section_names = SECTIONS_BY_PROJECT_TYPE.get(
            project_type,
            SECTIONS_BY_PROJECT_TYPE['ongoing']
        )
        
        for position, section_name in enumerate(section_names):
            section_id = f"section_{uuid.uuid4().hex[:12]}"
            
            sections_data.append({
                'section_id': section_id,
                'project_id': project_id,
                'name': section_name,
                'position': position,
                'created_at': created_at
            })
    
    db.insert_many('sections', sections_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(sections_data)} sections")
