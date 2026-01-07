"""
Configuration for Asana simulation data generation.

All parameters for the simulation can be adjusted here.
"""
import os
from datetime import datetime, timedelta

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', 'output/asana_simulation.sqlite')
SCHEMA_PATH = 'schema.sql'

# Organization
ORGANIZATION_NAME = "TechFlow Solutions"  # Our fictional B2B SaaS company
ORGANIZATION_DOMAIN = "techflow.com"

# Scale parameters
NUM_USERS = 7000  # 5000-10000 range, choosing 7000
NUM_TEAMS = 35    # ~1 team per 200 employees
NUM_PROJECTS = 350  # ~10 projects per team
NUM_TASKS = 28000   # ~80 tasks per project
NUM_TAGS = 50

# Team distribution (percentages should sum to ~1.0)
TEAM_TYPE_DISTRIBUTION = {
    'engineering': 0.40,  # 40% engineering (14 teams)
    'marketing': 0.15,    # 15% marketing (5 teams)
    'operations': 0.15,   # 15% operations (5 teams)
    'sales': 0.10,        # 10% sales (3 teams)
    'design': 0.08,       # 8% design (3 teams)
    'hr': 0.05,           # 5% HR (2 teams)
    'it': 0.05,           # 5% IT (2 teams)
    'executive': 0.02,    # 2% executive (1 team)
}

# Project type distribution by team type
PROJECT_TYPE_BY_TEAM = {
    'engineering': {
        'sprint': 0.60,      # Agile sprints
        'ongoing': 0.25,     # Bug tracking, tech debt
        'milestone': 0.15,   # Major releases
    },
    'marketing': {
        'campaign': 0.50,    # Marketing campaigns
        'ongoing': 0.30,     # Content calendar, social media
        'milestone': 0.20,   # Product launches, events
    },
    'operations': {
        'process': 0.40,     # Process improvement
        'ongoing': 0.40,     # Daily operations
        'milestone': 0.20,   # Quarterly initiatives
    },
    'default': {  # For sales, design, hr, it, executive
        'ongoing': 0.50,
        'milestone': 0.30,
        'process': 0.20,
    }
}

# Task parameters
TASKS_PER_PROJECT = {
    'sprint': (40, 100),      # Sprints have focused task sets
    'campaign': (30, 80),     # Campaigns have defined deliverables
    'ongoing': (60, 150),     # Ongoing projects accumulate tasks
    'milestone': (50, 120),   # Milestones have many tasks
    'process': (20, 60),      # Process projects are smaller
}

# Task assignment
UNASSIGNED_TASK_RATE = 0.15  # 15% of tasks unassigned

# Task completion rates by project type
COMPLETION_RATE_BY_TYPE = {
    'sprint': (0.70, 0.85),      # Sprints have high completion
    'campaign': (0.60, 0.75),    # Campaigns mostly complete
    'ongoing': (0.40, 0.55),     # Ongoing work is never "done"
    'milestone': (0.50, 0.70),   # Milestones partially complete
    'process': (0.55, 0.70),     # Process work moderately complete
}

# Due date distribution (weights)
DUE_DATE_DISTRIBUTION = {
    'within_week': 0.25,
    'within_month': 0.40,
    'one_to_three_months': 0.20,
    'no_due_date': 0.15,
}

# Subtask parameters
SUBTASK_RATE = 0.30  # 30% of tasks have subtasks
SUBTASKS_PER_TASK = (1, 4)  # 1-4 subtasks when they exist

# Comment parameters
COMMENT_RATE = 0.40  # 40% of tasks have comments
COMMENTS_PER_TASK = (1, 5)  # 1-5 comments when they exist

# Custom field parameters
CUSTOM_FIELDS_PER_PROJECT = (1, 4)  # Projects have 1-4 custom fields
CUSTOM_FIELD_FILL_RATE = 0.50  # 50% of tasks have custom field values

# Tag parameters
TASK_TAG_RATE = 0.25  # 25% of tasks are tagged
TAGS_PER_TASK = (1, 3)  # 1-3 tags when tagged

# Attachment parameters
ATTACHMENT_RATE = 0.30  # 30% of tasks have attachments
ATTACHMENTS_PER_TASK = (1, 3)  # 1-3 attachments when they exist

# Time parameters
SIMULATION_START_DATE = datetime.now() - timedelta(days=180)  # 6 months of history
SIMULATION_END_DATE = datetime.now()

# Data sources
YC_COMPANIES_CSV = 'src/data/2023-02-27-yc-companies.csv'

# Colors for projects/tags (Asana uses these)
ASANA_COLORS = [
    'dark-pink', 'dark-green', 'dark-blue', 'dark-red', 'dark-teal',
    'dark-brown', 'dark-orange', 'dark-purple', 'dark-warm-gray',
    'light-pink', 'light-green', 'light-blue', 'light-red', 'light-teal',
    'light-brown', 'light-orange', 'light-purple', 'light-warm-gray'
]

# User role distribution
USER_ROLE_DISTRIBUTION = {
    'member': 0.85,
    'admin': 0.10,
    'limited_access': 0.05,
}

# Team size parameters (how many users per team)
TEAM_SIZE_RANGE = (15, 150)  # Min and max members per team

# Logging
LOG_LEVEL = 'INFO'