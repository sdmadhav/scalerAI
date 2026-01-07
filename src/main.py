"""
Main script to orchestrate Asana simulation data generation.
Combines organization loading, user loading, and data generation into one script.
"""
import logging
import sys
import sqlite3
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from src.utils.db import create_database
from src.generators.teams import generate_teams, generate_team_memberships
from src.generators.projects import generate_projects, generate_sections
from src.generators.tasks import generate_tasks, generate_subtasks
from src.generators.comments import (generate_comments, generate_custom_fields,
                                     generate_tags, generate_attachments)
from src import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('generation.log')
    ]
)

logger = logging.getLogger(__name__)

# Configuration
DB_PATH = "output/asana_simulation.sqlite"
ORGANIZATIONS_CSV = "src/data/2023-02-27-yc-companies.csv"
USERS_CSV = "src/data/doordash_users.csv"


def extract_domain(url):
    """Extract domain from URL."""
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urlparse(url)
    return parsed.netloc.lower() if parsed.netloc else None


def load_organizations():
    """Load organizations from CSV into database."""
    logger.info("\n[Step 1a] Loading organizations from CSV...")
    
    if not Path(ORGANIZATIONS_CSV).exists():
        logger.error(f"❌ Organizations CSV not found: {ORGANIZATIONS_CSV}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop and recreate organizations table
    cursor.execute("DROP TABLE IF EXISTS organizations;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS organizations (
        organization_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        domain TEXT,
        created_at TIMESTAMP NOT NULL,
        is_organization BOOLEAN NOT NULL DEFAULT TRUE
    );
    """)
    
    # Read CSV and insert data
    inserted = 0
    with open(ORGANIZATIONS_CSV, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            organization_id = row.get("company_id")
            name = row.get("company_name")
            website = row.get("website")
            year_founded = row.get("year_founded")
            
            if not organization_id or not name or not year_founded:
                continue
            
            domain = extract_domain(website)
            
            # Convert to timestamp of NEXT year
            try:
                next_year = int(year_founded) + 1
                created_at = datetime(next_year, 1, 1).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            
            cursor.execute("""
            INSERT OR IGNORE INTO organizations
            (organization_id, name, domain, created_at)
            VALUES (?, ?, ?, ?);
            """, (organization_id, name, domain, created_at))
            inserted += 1
    
    conn.commit()
    org_count = cursor.execute("SELECT COUNT(*) FROM organizations").fetchone()[0]
    conn.close()
    
    logger.info(f"✓ Loaded {org_count} organizations from CSV")
    return org_count


def load_users():
    """Load users from CSV into database."""
    logger.info("\n[Step 1b] Loading users from CSV...")
    
    if not Path(USERS_CSV).exists():
        logger.error(f"❌ Users CSV not found: {USERS_CSV}")
        sys.exit(1)
    
    # Load CSV
    df = pd.read_csv(USERS_CSV)
    logger.info(f"Found {len(df)} users in CSV")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert users
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO users (user_id, organization_id, email, name, role, 
                                  profile_photo_url, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['user_id'],
                row['organization_id'],
                row['email'],
                row['name'],
                row['role'],
                row['profile_photo_url'] if pd.notna(row['profile_photo_url']) else None,
                row['created_at'],
                row['is_active']
            ))
            inserted += 1
        except sqlite3.IntegrityError as e:
            logger.warning(f"Skipping duplicate user: {row['email']}")
    
    conn.commit()
    user_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    
    logger.info(f"✓ Loaded {user_count} users from CSV")
    return user_count


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    logger.info("="*60)
    logger.info("Asana Simulation Data Generation")
    logger.info("="*60)
    logger.info(f"Configuration:")
    logger.info(f"  Organization: {config.ORGANIZATION_NAME}")
    logger.info(f"  Users: {config.NUM_USERS}")
    logger.info(f"  Teams: {config.NUM_TEAMS}")
    logger.info(f"  Projects: {config.NUM_PROJECTS}")
    logger.info(f"  Tasks: ~{config.NUM_TASKS}")
    logger.info(f"  Simulation period: {config.SIMULATION_START_DATE.date()} to {config.SIMULATION_END_DATE.date()}")
    logger.info("="*60)
    
    try:
        # Step 1: Create database and schema
        logger.info("\n[1/11] Creating database and schema...")
        db = create_database(config.DATABASE_PATH, config.SCHEMA_PATH)
        logger.info("✓ Database created successfully")
        db.close()  # Close the connection before loading data
        
        # Step 1a: Load organizations
        org_count = load_organizations()
        
        # Step 1b: Load users
        user_count = load_users()
        
        # Reconnect to database for data generation
        db = create_database(config.DATABASE_PATH, config.SCHEMA_PATH)
        
        # Step 2: Verify organization and users exist
        logger.info("\n[2/11] Verifying organizations and users...")
        cursor = db.connection.cursor()
        
        if org_count == 0:
            logger.error("❌ No organizations found!")
            return
        
        if user_count == 0:
            logger.error("❌ No users found!")
            return
        
        # Get the first organization
        org_id = cursor.execute("SELECT organization_id FROM organizations LIMIT 1").fetchone()[0]
        logger.info(f"✓ Found {org_count} organizations and {user_count} users")
        logger.info(f"✓ Using organization: {org_id}")
        
        # Step 3: Generate teams
        logger.info("\n[3/11] Generating teams...")
        team_ids = generate_teams(db, org_id)
        
        # Step 4: Generate team memberships
        logger.info("\n[4/11] Generating team memberships...")
        generate_team_memberships(db)
        
        # Step 5: Generate projects
        logger.info("\n[5/11] Generating projects...")
        project_metadata = generate_projects(db)
        
        # Step 6: Generate sections
        logger.info("\n[6/11] Generating sections...")
        generate_sections(db, project_metadata)
        
        # Step 7: Generate tasks
        logger.info("\n[7/11] Generating tasks...")
        generate_tasks(db, project_metadata)
        
        # Step 8: Generate subtasks
        logger.info("\n[8/11] Generating subtasks...")
        generate_subtasks(db)
        
        # Step 9: Generate comments
        logger.info("\n[9/11] Generating comments and metadata...")
        generate_comments(db)
        generate_custom_fields(db)
        generate_tags(db, org_id)
        generate_attachments(db)
        
        # Step 10: Validation
        logger.info("\n[10/11] Running validation checks...")
        validate_database(db)
        
        # Close database
        db.close()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "="*60)
        logger.info("✓ GENERATION COMPLETE!")
        logger.info("="*60)
        logger.info(f"Database: {config.DATABASE_PATH}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Logs: generation.log")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"\n❌ Error during generation: {e}", exc_info=True)
        sys.exit(1)


def validate_database(db):
    """Run validation checks on generated data."""
    cursor = db.connection.cursor()
    
    checks = {
        'organizations': 'SELECT COUNT(*) FROM organizations',
        'users': 'SELECT COUNT(*) FROM users',
        'teams': 'SELECT COUNT(*) FROM teams',
        'team_memberships': 'SELECT COUNT(*) FROM team_memberships',
        'projects': 'SELECT COUNT(*) FROM projects',
        'sections': 'SELECT COUNT(*) FROM sections',
        'tasks': 'SELECT COUNT(*) FROM tasks',
        'comments': 'SELECT COUNT(*) FROM comments',
        'custom_field_definitions': 'SELECT COUNT(*) FROM custom_field_definitions',
        'custom_field_values': 'SELECT COUNT(*) FROM custom_field_values',
        'tags': 'SELECT COUNT(*) FROM tags',
        'task_tags': 'SELECT COUNT(*) FROM task_tags',
        'attachments': 'SELECT COUNT(*) FROM attachments',
    }
    
    logger.info("\nRecord counts:")
    for table, query in checks.items():
        count = cursor.execute(query).fetchone()[0]
        logger.info(f"  {table}: {count:,}")
    
    # Data quality checks
    logger.info("\nData quality checks:")
    
    # Check for invalid completion dates
    invalid_dates = cursor.execute("""
        SELECT COUNT(*) FROM tasks 
        WHERE completed_at IS NOT NULL AND completed_at < created_at
    """).fetchone()[0]
    
    if invalid_dates == 0:
        logger.info("  ✓ All completion dates are valid")
    else:
        logger.warning(f"  ⚠ Found {invalid_dates} tasks with invalid completion dates")
    
    # Check for orphaned subtasks
    orphaned = cursor.execute("""
        SELECT COUNT(*) FROM tasks t1
        WHERE t1.parent_task_id IS NOT NULL
        AND NOT EXISTS (SELECT 1 FROM tasks t2 WHERE t2.task_id = t1.parent_task_id)
    """).fetchone()[0]
    
    if orphaned == 0:
        logger.info("  ✓ No orphaned subtasks")
    else:
        logger.warning(f"  ⚠ Found {orphaned} orphaned subtasks")
    
    # Check unassigned task rate
    total_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NULL").fetchone()[0]
    unassigned = cursor.execute("SELECT COUNT(*) FROM tasks WHERE parent_task_id IS NULL AND assignee_id IS NULL").fetchone()[0]
    unassigned_rate = unassigned / total_tasks if total_tasks > 0 else 0
    
    logger.info(f"  ✓ Unassigned task rate: {unassigned_rate:.1%} (target: {config.UNASSIGNED_TASK_RATE:.1%})")
    
    # Check completion rate
    completed = cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1 AND parent_task_id IS NULL").fetchone()[0]
    completion_rate = completed / total_tasks if total_tasks > 0 else 0
    
    logger.info(f"  ✓ Overall completion rate: {completion_rate:.1%}")
    
    logger.info("\n✓ Validation complete")


if __name__ == "__main__":
    main()
