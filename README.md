# Asana Simulation - High-Quality Seed Data Generator

This project generates realistic seed data for an Asana RL environment, simulating a B2B SaaS company with 5000-10000 employees using Asana for product development, marketing, and operations workflows.

## Overview

The simulation creates a complete, realistic Asana workspace with:
- **1 Organization** representing a B2B SaaS company
- **7,000 Users** with diverse roles and team memberships
- **35 Teams** across Engineering, Marketing, Operations, and other functions
- **350 Projects** with varied types (sprints, campaigns, milestones, ongoing work)
- **~28,000 Tasks** with realistic names, descriptions, assignments, and due dates
- **Comments, Custom Fields, Tags, and Attachments** for rich collaboration data

## Key Features

### Data Realism
- **Pattern-based task names**: Engineering tasks follow "[Component] - [Action] - [Detail]" format
- **Research-backed distributions**: Due dates, completion rates based on industry benchmarks
- **Temporal consistency**: All dates maintain logical relationships (completed_at > created_at)
- **Workload realism**: Pareto distribution for task assignment (some users busier than others)
- **Business patterns**: More tasks created Mon-Wed, fewer on weekends

### Architecture
- **Modular design**: Separate generators for each entity type
- **Pattern templates**: 300+ templates for realistic content without LLM APIs
- **Configurable**: All parameters adjustable in `config.py`
- **Validated**: Built-in data quality checks

## Prerequisites

- Python 3.8+
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <repo-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. **Generate Organizations and Users** (already done in your case):
```bash
# Your organizations and users are already in the database
```

2. **Generate Complete Simulation**:
```bash
python src/main.py
```

This will:
- Create teams and team memberships
- Generate projects and sections
- Create tasks with realistic patterns
- Add subtasks, comments, custom fields, tags, and attachments
- Validate data quality

### Output

The script generates:
- **Database**: `output/asana_simulation.sqlite`
- **Logs**: `generation.log`

### Configuration

Edit `src/config.py` to adjust:
- Number of teams, projects, tasks
- Team type distribution
- Task completion rates
- Due date distribution
- Custom field settings
- And more...

## Project Structure

```
.
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── schema.sql                   # Database schema DDL
├── src/
│   ├── config.py               # Configuration parameters
│   ├── main.py                 # Main orchestration script
│   ├── data/                   # External data sources
│   │   └── *.csv              # Y Combinator companies data
│   ├── generators/             # Data generation modules
│   │   ├── teams.py           # Team and membership generation
│   │   ├── projects.py        # Project and section generation
│   │   ├── tasks.py           # Task generation (core logic)
│   │   └── comments.py        # Comments, custom fields, tags
│   └── utils/                  # Utility functions
│       ├── db.py              # Database utilities
│       ├── dates.py           # Date generation with realistic patterns
│       ├── distributions.py    # Statistical distributions
│       └── patterns.py         # Pattern templates for realistic content
└── output/
    └── asana_simulation.sqlite # Generated database
```

## Methodology Highlights

### Task Name Generation
Tasks use pattern-based generation with variable substitution:
- **Engineering**: "[Component] - Fix [issue]", "[Component] - Implement [feature]"
- **Marketing**: "[Campaign] - [deliverable]", "Create [asset] for [campaign]"
- **Operations**: "[Process] - Document workflow", "Review [item] submissions"

Variables are selected from curated lists of 30-50 realistic options per category.

### Due Date Distribution
Based on Asana's "Anatomy of Work" research:
- 25% within 1 week (urgent work)
- 40% within 1 month (current sprint/cycle)
- 20% 1-3 months out (planned future work)
- 15% no due date (backlog items)

Dates avoid weekends 85% of the time (realistic planning behavior).

### Task Completion
Completion rates vary by project type:
- Sprint projects: 70-85% complete
- Campaigns: 60-75% complete
- Ongoing projects: 40-55% complete

Older tasks are more likely to be complete (age factor applied).

### Task Assignment
Uses Pareto distribution (power law, alpha=1.5):
- Simulates realistic workload: 20% of people do ~50% of work
- 15% of tasks remain unassigned (realistic for new/backlog items)

## Data Quality Validation

The generator includes automatic validation:
- ✓ Temporal consistency (completed_at > created_at)
- ✓ Referential integrity (all foreign keys valid)
- ✓ No orphaned subtasks
- ✓ Realistic unassigned task rate
- ✓ Expected completion rates by project type

## Querying the Database

Example queries:

```sql
-- Get all tasks for a user
SELECT t.name, t.due_date, p.name as project_name
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
WHERE t.assignee_id = 'user_abc123'
AND t.completed = 0
ORDER BY t.due_date;

-- Get project completion statistics
SELECT 
    p.name,
    COUNT(t.task_id) as total_tasks,
    SUM(t.completed) as completed_tasks,
    ROUND(AVG(t.completed) * 100, 1) as completion_rate
FROM projects p
LEFT JOIN tasks t ON p.project_id = t.project_id
WHERE t.parent_task_id IS NULL
GROUP BY p.project_id
ORDER BY completion_rate DESC;

-- Get team workload
SELECT 
    u.name,
    COUNT(t.task_id) as assigned_tasks,
    SUM(CASE WHEN t.completed = 0 THEN 1 ELSE 0 END) as active_tasks
FROM users u
LEFT JOIN tasks t ON u.user_id = t.assignee_id
WHERE t.parent_task_id IS NULL
GROUP BY u.user_id
ORDER BY assigned_tasks DESC
LIMIT 20;
```

## Performance

Generation time: ~2-3 minutes for full dataset on modern hardware
- Organizations/Users: Pre-loaded
- Teams: < 1 second
- Projects: ~5 seconds
- Tasks: ~90 seconds (main bottleneck)
- Comments/Metadata: ~30 seconds

## Design Decisions

### Custom Fields
Uses separate definition and value tables (EAV pattern):
- **Pros**: Flexible, no schema changes for new fields, no NULL proliferation
- **Cons**: More complex queries
- **Why**: Matches Asana's model, supports different fields per project

### Task Hierarchy
Self-referencing foreign key (single table):
- **Pros**: Subtasks are first-class tasks, uniform treatment
- **Cons**: Requires recursive queries for deep hierarchies
- **Why**: Matches Asana's model where subtasks ARE tasks

### Pattern Templates vs. LLMs
Uses pattern templates with variable substitution:
- **Pros**: Fast, free, unlimited variety, no API dependencies
- **Cons**: Less creative than LLM-generated text
- **Why**: Pragmatic for 6-hour timeline, still produces realistic output

## Extending the Generator

### Adding New Task Patterns
Edit `src/utils/patterns.py`:
```python
TASK_PATTERNS['new_category'] = [
    'Pattern {variable1} and {variable2}',
    # ... more patterns
]

# Add variables
NEW_VARIABLES = ['option1', 'option2', ...]
```

### Adjusting Distributions
Edit `src/config.py`:
```python
DUE_DATE_DISTRIBUTION = {
    'within_week': 0.30,  # Increase urgency
    'within_month': 0.40,
    # ...
}
```

### Adding New Entities
1. Update `schema.sql` with new table
2. Create generator in `src/generators/new_entity.py`
3. Call from `main.py`

## Troubleshooting

**Issue**: "No organizations found"
- **Solution**: Ensure organizations are created before running main.py

**Issue**: Low task count
- **Solution**: Check `config.NUM_TASKS` and `TASKS_PER_PROJECT` settings

**Issue**: All tasks assigned to few users
- **Solution**: Verify Pareto distribution in `distributions.py` has alpha ~1.5

## Credits

- **Y Combinator Company Data**: Kaggle dataset by Miguel Corral Jr
- **Name Generation**:  Indigen library
- **Inspiration**: Asana's public templates and documentation


## Contact

Mail  - sdmadhav13@gmail.com


   