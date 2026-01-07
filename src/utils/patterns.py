"""
Pattern templates and data for realistic Asana simulation.
Based on analysis of real project management systems.
"""
import random

# ============================================
# TEAM NAMES BY TYPE
# ============================================

TEAM_NAMES = {
    'engineering': [
        'Platform Engineering', 'Backend Services', 'Frontend Experience',
        'Mobile Apps', 'Infrastructure', 'Data Engineering', 'API Services',
        'Security', 'DevOps', 'Cloud Infrastructure', 'ML/AI Engineering',
        'Core Platform', 'Developer Tools', 'Search & Discovery'
    ],
    'marketing': [
        'Growth Marketing', 'Content & Brand', 'Product Marketing',
        'Demand Generation', 'Digital Marketing', 'Marketing Operations'
    ],
    'operations': [
        'Business Operations', 'Revenue Operations', 'IT Operations',
        'Facilities & Workplace', 'Program Management Office'
    ],
    'sales': [
        'Enterprise Sales', 'Sales Operations', 'Customer Success'
    ],
    'design': [
        'Product Design', 'UX Research', 'Design Systems'
    ],
    'hr': [
        'People Operations', 'Recruiting'
    ],
    'it': [
        'IT Support', 'Enterprise Systems'
    ],
    'executive': [
        'Executive Team'
    ]
}

# ============================================
# PROJECT NAMES BY TYPE
# ============================================

PROJECT_TEMPLATES = {
    'sprint': [
        'Sprint {num}',
        'Q{quarter} Sprint {num}',
        '{team_name} Sprint {num}',
        '{month} Sprint',
    ],
    'campaign': [
        'Q{quarter} {campaign_type}',
        '{month} Product Launch',
        '{season} Campaign',
        '{event_name} Event',
        '{channel} Growth Initiative Q{quarter}',
    ],
    'ongoing': [
        '{team_name} Operations',
        'Bug Tracking & Maintenance',
        'Customer Requests',
        'Tech Debt',
        'Content Calendar',
        'Social Media Management',
    ],
    'milestone': [
        'Q{quarter} Product Release',
        '{version} Launch',
        '{feature_name} Beta',
        'Annual Planning {year}',
        '{month} Infrastructure Upgrade',
    ],
    'process': [
        '{process_name} Process Improvement',
        'Q{quarter} OKR Planning',
        '{department} Workflow Optimization',
        'Quarterly Business Review Q{quarter}',
    ]
}

CAMPAIGN_TYPES = [
    'Email Campaign', 'Social Media Push', 'Content Marketing',
    'Product Launch', 'Brand Awareness', 'Lead Generation',
    'Customer Retention', 'Partner Marketing'
]

PROCESS_NAMES = [
    'Hiring', 'Onboarding', 'Performance Review', 'Budget Planning',
    'Vendor Management', 'Security Audit', 'Compliance Review'
]

# ============================================
# SECTIONS BY PROJECT TYPE
# ============================================

SECTIONS_BY_PROJECT_TYPE = {
    'sprint': ['Backlog', 'To Do', 'In Progress', 'In Review', 'Done'],
    'campaign': ['Planning', 'Creative Development', 'In Progress', 'Review & Approval', 'Published'],
    'ongoing': ['New', 'To Do', 'In Progress', 'Done'],
    'milestone': ['Planning', 'Design', 'Development', 'Testing', 'Launch', 'Post-Launch'],
    'process': ['Proposed', 'In Review', 'Approved', 'In Progress', 'Completed']
}

# ============================================
# TASK NAME PATTERNS
# ============================================

# Engineering components
ENGINEERING_COMPONENTS = [
    'API Gateway', 'Auth Service', 'Dashboard', 'Database', 'Payment System',
    'Notification Service', 'Search Engine', 'Analytics Service', 'Cache Layer',
    'Message Queue', 'File Storage', 'Email Service', 'Reporting Engine',
    'Admin Panel', 'Mobile App', 'Web App', 'Backend API', 'Frontend',
    'Deployment Pipeline', 'Monitoring System', 'Logging Service', 'CDN',
    'Load Balancer', 'Data Pipeline', 'ML Model', 'Integration Service',
    'User Management', 'Billing System', 'Content Management', 'Recommendation Engine'
]

ENGINEERING_ISSUES = [
    'memory leak', 'race condition', 'timeout error', 'null pointer exception',
    'authentication failure', 'connection timeout', 'infinite loop', 'deadlock',
    'buffer overflow', 'stack overflow', 'performance degradation', 'data corruption',
    'broken redirect', 'missing validation', 'security vulnerability', 'API rate limit',
    'slow query', 'cache invalidation', 'session expiry', 'broken link'
]

ENGINEERING_FEATURES = [
    'two-factor authentication', 'dark mode', 'export to PDF', 'bulk operations',
    'advanced search', 'real-time updates', 'email notifications', 'mobile responsiveness',
    'API versioning', 'rate limiting', 'audit logging', 'data encryption',
    'SSO integration', 'webhook support', 'custom fields', 'advanced filters',
    'batch processing', 'automated backups', 'role-based access', 'activity feed'
]

TASK_PATTERNS = {
    'engineering_bug': [
        '{component} - Fix {issue}',
        'Debug {symptom} in {component}',
        'Resolve {issue} affecting {component}',
        '{component} - Address {issue}',
        'Fix: {component} {issue}',
    ],
    'engineering_feature': [
        '{component} - Implement {feature}',
        'Add {feature} to {component}',
        '{component} - Build {feature}',
        'Develop {feature} for {component}',
        'Create {feature} functionality',
    ],
    'engineering_refactor': [
        '{component} - Refactor {aspect}',
        'Optimize {component} performance',
        '{component} - Code cleanup',
        'Improve {component} architecture',
        'Modernize {component} codebase',
    ],
    'engineering_test': [
        '{component} - Write unit tests',
        'Add integration tests for {feature}',
        '{component} - Increase test coverage',
        'E2E tests for {feature}',
    ],
    'marketing_content': [
        '{campaign} - Create {content_type}',
        'Write {content_type} for {campaign}',
        '{campaign} - {content_type} draft',
        'Design {asset_type} for {campaign}',
    ],
    'marketing_campaign': [
        '{campaign} - Campaign setup',
        '{campaign} - Schedule {channel} posts',
        '{campaign} - Review analytics',
        '{campaign} - A/B test {element}',
        '{campaign} - Audience targeting',
    ],
    'operations_process': [
        '{process} - Document workflow',
        '{process} - Create template',
        'Update {process} guidelines',
        '{process} - Training materials',
        'Automate {process} steps',
    ],
    'operations_admin': [
        'Review {item} submissions',
        'Process {request_type} requests',
        'Update {system} configuration',
        '{department} quarterly planning',
        'Vendor evaluation for {service}',
    ]
}

CONTENT_TYPES = [
    'blog post', 'case study', 'whitepaper', 'email copy', 'social media posts',
    'landing page', 'video script', 'infographic', 'press release', 'newsletter'
]

ASSET_TYPES = [
    'banner image', 'social graphics', 'email template', 'presentation deck',
    'video thumbnail', 'ad creative', 'landing page mockup', 'brand guidelines'
]

CHANNELS = ['Email', 'Social Media', 'Blog', 'Paid Ads', 'Events', 'Partnerships']

# ============================================
# TASK DESCRIPTIONS
# ============================================

DESCRIPTION_TEMPLATES = {
    'empty': '',
    'short': [
        'Need to complete this by {date}.',
        'Quick task - should take {hours} hours.',
        'Follow-up from meeting on {date}.',
        'Blocked by {blocker} - unblock ASAP.',
        'Customer request from {customer}.',
    ],
    'medium': [
        '## Context\n{context}\n\n## Action Items\n- {item1}\n- {item2}\n\n## Notes\n{notes}',
        '## Description\n{description}\n\n## Requirements\n- {req1}\n- {req2}\n- {req3}',
        '## Background\n{background}\n\n## Next Steps\n1. {step1}\n2. {step2}\n3. {step3}',
    ],
    'detailed': [
        '## Overview\n{overview}\n\n## Context\n{context}\n\n## Requirements\n- {req1}\n- {req2}\n- {req3}\n\n## Acceptance Criteria\n- [ ] {criteria1}\n- [ ] {criteria2}\n- [ ] {criteria3}\n\n## Resources\n- {resource1}\n- {resource2}',
        '## Problem Statement\n{problem}\n\n## Proposed Solution\n{solution}\n\n## Implementation Plan\n1. {step1}\n2. {step2}\n3. {step3}\n\n## Success Metrics\n- {metric1}\n- {metric2}\n\n## Timeline\n{timeline}',
    ]
}

CONTEXTS = [
    'This is a high priority item for Q{quarter}',
    'Customer reported this issue affecting {num} users',
    'Technical debt that needs addressing',
    'Part of the {project_name} initiative',
    'Required for {deadline} launch',
]

BACKGROUNDS = [
    'We noticed performance issues during peak hours',
    'Multiple customers have requested this feature',
    'This will improve our {metric} by {percent}%',
    'Compliance requirement for {standard}',
    'Competitive analysis shows we\'re behind on this',
]

# ============================================
# COMMENTS
# ============================================

COMMENT_TEMPLATES = [
    'Updated status to {status}',
    'Moving this to {section}',
    'Blocked by {blocker} - need help from {team}',
    'Completed! {outcome}',
    'Question: {question}',
    'Found an issue: {issue}',
    'This is taking longer than expected because {reason}',
    'PR ready for review: {url}',
    'Design approved, moving forward',
    'Need clarification on {aspect}',
    'Added {hours}h to time estimate',
    'Dependencies: {dependency}',
    'Starting work on this today',
    'Reassigning to {person} - better fit for their expertise',
    'Documentation updated at {url}',
]

STATUSES = ['in progress', 'blocked', 'done', 'in review', 'on hold']
BLOCKERS = ['another task', 'waiting for approval', 'external dependency', 'missing requirements', 'technical blocker']
OUTCOMES = ['Merged and deployed', 'Tested and verified', 'Launched to production', 'Completed on schedule']
QUESTIONS = [
    'Should we prioritize performance or readability here?',
    'What\'s the expected timeline for this?',
    'Do we need stakeholder approval?',
    'Should this be split into multiple tasks?',
]

# ============================================
# CUSTOM FIELDS
# ============================================

CUSTOM_FIELDS_BY_TEAM_TYPE = {
    'engineering': [
        {'name': 'Story Points', 'type': 'dropdown', 'options': ['1', '2', '3', '5', '8', '13', '21']},
        {'name': 'Priority', 'type': 'dropdown', 'options': ['Critical', 'High', 'Medium', 'Low']},
        {'name': 'Sprint', 'type': 'text'},
        {'name': 'Component', 'type': 'dropdown', 'options': ['Backend', 'Frontend', 'Mobile', 'Infrastructure', 'Data']},
    ],
    'marketing': [
        {'name': 'Campaign', 'type': 'text'},
        {'name': 'Channel', 'type': 'dropdown', 'options': ['Email', 'Social', 'Paid', 'Events', 'Partnerships']},
        {'name': 'Budget', 'type': 'number'},
        {'name': 'Target Audience', 'type': 'dropdown', 'options': ['SMB', 'Enterprise', 'Individual', 'All']},
    ],
    'operations': [
        {'name': 'Process Stage', 'type': 'dropdown', 'options': ['Planning', 'Approval', 'Implementation', 'Review']},
        {'name': 'ROI Impact', 'type': 'dropdown', 'options': ['High', 'Medium', 'Low']},
        {'name': 'Department', 'type': 'dropdown', 'options': ['Finance', 'HR', 'IT', 'Legal', 'Sales']},
    ],
    'default': [
        {'name': 'Priority', 'type': 'dropdown', 'options': ['High', 'Medium', 'Low']},
        {'name': 'Status', 'type': 'dropdown', 'options': ['Not Started', 'In Progress', 'Complete']},
    ]
}

# ============================================
# TAGS
# ============================================

ORGANIZATION_TAGS = [
    'urgent', 'bug', 'feature-request', 'tech-debt', 'customer-request',
    'security', 'performance', 'ui-ux', 'documentation', 'testing',
    'blocked', 'needs-review', 'quick-win', 'long-term', 'research',
    'compliance', 'accessibility', 'mobile', 'api', 'infrastructure',
    'analytics', 'marketing', 'sales', 'support', 'onboarding',
    'q1', 'q2', 'q3', 'q4', 'roadmap', 'backlog',
    'high-priority', 'low-priority', 'nice-to-have', 'critical',
    'design', 'engineering', 'product', 'growth', 'operations',
    'external-dependency', 'internal-tool', 'customer-facing',
    'experimental', 'beta', 'launch', 'deprecated', 'maintenance'
]

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_task_name(project_type, team_type):
    """Generate realistic task name based on project and team type."""
    if team_type == 'engineering':
        pattern_type = random.choice([
            'engineering_bug', 'engineering_feature', 
            'engineering_refactor', 'engineering_test'
        ])
        weights = [0.35, 0.40, 0.15, 0.10]  # More bugs and features
        pattern_type = random.choices(
            ['engineering_bug', 'engineering_feature', 'engineering_refactor', 'engineering_test'],
            weights=weights
        )[0]
    elif team_type == 'marketing':
        pattern_type = random.choice(['marketing_content', 'marketing_campaign'])
    elif team_type in ['operations', 'hr', 'it']:
        pattern_type = random.choice(['operations_process', 'operations_admin'])
    else:
        pattern_type = random.choice(['operations_admin'])
    
    pattern = random.choice(TASK_PATTERNS[pattern_type])
    
    # Fill in variables
    task_name = pattern
    if '{component}' in task_name:
        task_name = task_name.replace('{component}', random.choice(ENGINEERING_COMPONENTS))
    if '{issue}' in task_name:
        task_name = task_name.replace('{issue}', random.choice(ENGINEERING_ISSUES))
    if '{symptom}' in task_name:
        task_name = task_name.replace('{symptom}', random.choice(ENGINEERING_ISSUES))
    if '{feature}' in task_name:
        task_name = task_name.replace('{feature}', random.choice(ENGINEERING_FEATURES))
    if '{aspect}' in task_name:
        task_name = task_name.replace('{aspect}', random.choice(['performance', 'architecture', 'code quality', 'maintainability']))
    if '{campaign}' in task_name:
        task_name = task_name.replace('{campaign}', f'Q{random.randint(1,4)} {random.choice(CAMPAIGN_TYPES)}')
    if '{content_type}' in task_name:
        task_name = task_name.replace('{content_type}', random.choice(CONTENT_TYPES))
    if '{asset_type}' in task_name:
        task_name = task_name.replace('{asset_type}', random.choice(ASSET_TYPES))
    if '{channel}' in task_name:
        task_name = task_name.replace('{channel}', random.choice(CHANNELS))
    if '{process}' in task_name:
        task_name = task_name.replace('{process}', random.choice(PROCESS_NAMES))
    if '{item}' in task_name:
        task_name = task_name.replace('{item}', random.choice(['expense', 'time-off', 'purchase', 'access']))
    if '{request_type}' in task_name:
        task_name = task_name.replace('{request_type}', random.choice(['IT support', 'access', 'equipment', 'training']))
    if '{system}' in task_name:
        task_name = task_name.replace('{system}', random.choice(['CRM', 'ERP', 'HR system', 'billing']))
    if '{department}' in task_name:
        task_name = task_name.replace('{department}', random.choice(['Engineering', 'Marketing', 'Sales', 'Operations']))
    if '{service}' in task_name:
        task_name = task_name.replace('{service}', random.choice(['cloud hosting', 'analytics', 'monitoring', 'security']))
    
    return task_name


def generate_project_name(project_type, team_name):
    """Generate realistic project name."""
    template = random.choice(PROJECT_TEMPLATES[project_type])
    
    project_name = template
    if '{num}' in project_name:
        project_name = project_name.replace('{num}', str(random.randint(1, 24)))
    if '{quarter}' in project_name:
        project_name = project_name.replace('{quarter}', str(random.randint(1, 4)))
    if '{team_name}' in project_name:
        project_name = project_name.replace('{team_name}', team_name)
    if '{month}' in project_name:
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
        project_name = project_name.replace('{month}', random.choice(months))
    if '{campaign_type}' in project_name:
        project_name = project_name.replace('{campaign_type}', random.choice(CAMPAIGN_TYPES))
    if '{season}' in project_name:
        project_name = project_name.replace('{season}', random.choice(['Spring', 'Summer', 'Fall', 'Winter', 'Holiday']))
    if '{event_name}' in project_name:
        project_name = project_name.replace('{event_name}', random.choice(['Conference', 'Webinar', 'Product Launch', 'Trade Show']))
    if '{channel}' in project_name:
        project_name = project_name.replace('{channel}', random.choice(CHANNELS))
    if '{version}' in project_name:
        project_name = project_name.replace('{version}', f'v{random.randint(1,5)}.{random.randint(0,9)}')
    if '{feature_name}' in project_name:
        project_name = project_name.replace('{feature_name}', random.choice(ENGINEERING_FEATURES).title())
    if '{year}' in project_name:
        project_name = project_name.replace('{year}', str(random.randint(2024, 2025)))
    if '{process_name}' in project_name:
        project_name = project_name.replace('{process_name}', random.choice(PROCESS_NAMES))
    
    return project_name