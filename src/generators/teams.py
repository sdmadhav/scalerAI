"""
Generate teams and team memberships.
"""
import uuid
import random
import logging
from datetime import datetime, timedelta

from src.utils.db import Database
from src.utils.patterns import TEAM_NAMES
from src.utils.distributions import weighted_random_choice, sample_n_from_list
from src import config

logger = logging.getLogger(__name__)


def generate_teams(db: Database, organization_id: str) -> list[str]:
    """
    Generate teams for the organization.
    
    Args:
        db: Database instance
        organization_id: ID of organization
    
    Returns:
        List of generated team IDs
    """
    logger.info(f"Generating {config.NUM_TEAMS} teams...")
    
    teams_data = []
    team_ids = []
    
    # Calculate number of teams per type based on distribution
    team_types = list(config.TEAM_TYPE_DISTRIBUTION.keys())
    team_counts = {
        team_type: max(1, int(config.NUM_TEAMS * ratio))
        for team_type, ratio in config.TEAM_TYPE_DISTRIBUTION.items()
    }
    
    # Adjust to exactly NUM_TEAMS
    total = sum(team_counts.values())
    if total < config.NUM_TEAMS:
        team_counts['engineering'] += config.NUM_TEAMS - total
    
    created_at = config.SIMULATION_START_DATE
    
    for team_type, count in team_counts.items():
        available_names = TEAM_NAMES[team_type].copy()
        
        for i in range(count):
            team_id = f"team_{uuid.uuid4().hex[:12]}"
            team_ids.append(team_id)
            
            # Pick team name
            if available_names:
                name = available_names.pop(0)
            else:
                # Ran out of names, add number suffix
                name = f"{TEAM_NAMES[team_type][0]} {i+1}"
            
            description = f"{team_type.replace('_', ' ').title()} team"
            
            teams_data.append({
                'team_id': team_id,
                'organization_id': organization_id,
                'name': name,
                'description': description,
                'team_type': team_type,
                'created_at': created_at
            })
            
            # Increment creation date slightly
            created_at = created_at + timedelta(days=random.randint(1, 3))
    
    db.insert_many('teams', teams_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(teams_data)} teams")
    return team_ids


def generate_team_memberships(db: Database) -> None:
    """
    Assign users to teams with realistic distribution.
    
    Args:
        db: Database instance
    """
    logger.info("Generating team memberships...")
    
    # Get all users and teams
    cursor = db.connection.cursor()
    users = cursor.execute("SELECT user_id, created_at FROM users").fetchall()
    teams = cursor.execute("SELECT team_id, team_type FROM teams").fetchall()
    
    team_dict = {team[0]: team[1] for team in teams}
    
    memberships_data = []
    
    # Each user joins 1-2 teams (average 1.2)
    for user_id, user_created_at in users:
        num_teams = random.choices([1, 2], weights=[0.8, 0.2])[0]
        
        # Select teams for this user
        user_teams = sample_n_from_list(teams, num_teams, replace=False)
        
        for team_id, team_type in user_teams:
            membership_id = f"membership_{uuid.uuid4().hex[:12]}"
            
            # 10% chance to be team lead
            is_team_lead = random.random() < 0.10
            
            # Join date: between user creation and now
            days_after_creation = random.randint(0, 30)
            joined_at = datetime.fromisoformat(user_created_at) + timedelta(days=days_after_creation)
            
            memberships_data.append({
                'membership_id': membership_id,
                'team_id': team_id,
                'user_id': user_id,
                'joined_at': joined_at,
                'is_team_lead': is_team_lead
            })
    
    db.insert_many('team_memberships', memberships_data)
    db.commit()
    
    logger.info(f"[OK] Generated {len(memberships_data)} team memberships")
    
    # Log team size distribution
    cursor.execute("""
        SELECT t.name, t.team_type, COUNT(tm.user_id) as member_count
        FROM teams t
        LEFT JOIN team_memberships tm ON t.team_id = tm.team_id
        GROUP BY t.team_id
        ORDER BY member_count DESC
    """)
    
    logger.info("Team size distribution:")
    for name, team_type, count in cursor.fetchall()[:10]:
        logger.info(f"  {name} ({team_type}): {count} members")
