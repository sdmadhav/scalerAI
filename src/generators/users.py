"""
Generate 7,000 synthetic DoorDash employees using
state-wise labour participation-weighted name generation
via Indigen.

Requirements:
    pip install pandas
    git clone https://github.com/ghatesudi/Indigen.git
    # Add Indigen to your Python path or install it

Output: doordash_users.csv
"""

import csv
import uuid
import random
import os
from datetime import datetime, timedelta
from indigen.main import dynamic_import_state_functions
import pandas as pd

# -------------------------------------------------
# 1. Reproducibility
# -------------------------------------------------
random.seed(42)

# -------------------------------------------------
# 2. Configuration
# -------------------------------------------------
TOTAL_EMPLOYEES = 7000
ORGANIZATION_ID = "doordash_org_001"
ORGANIZATION_NAME = "DoorDash"
ORG_CREATED_AT = datetime(2020, 1, 1)
OUTPUT_FOLDER = "output"
CSV_PATH = os.path.join(OUTPUT_FOLDER, "doordash_users.csv")

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ROLES = ["admin", "member", "guest", "limited_access"]

# -------------------------------------------------
# 3. State-wise Labour Force Participation Rates
# -------------------------------------------------
# Mapping Indigen file names to readable state names
STATE_FILES_MAPPING = {
    "Andhra_Pradesh": "Andhrapradesh_File.py",
    "Bihar": "Bihar_File.py",
    "Jammu_&_Kashmir": "JK_File.py",
    "Karnataka": "Karnataka_File.py",
    "Madhya_Pradesh": "Madhyapradesh_File.py",
    "Haryana": "Haryana_File.py",
    "Telangana": "Telengana_File.py",
    "West_Bengal": "Bengal_File.py",
    "Maharashtra": "Maharashtra_File.py",
    "Assam": "Assam_File.py",
    "Uttar_Pradesh": "Uttarpradesh_File.py",
    "Chhattisgarh": "Chattisgarh_File.py",
    "Tripura": "Tripura_File.py",
    "Jharkhand": "Jharkhand_File.py",
    "Rajasthan": "Rajasthan_File.py",
    "Delhi": "Delhi_File.py",
    "Tamil_Nadu": "Tamil_File.py",
    "Kerala": "Kerala_File.py",
    "Odisha": "Orissa_File.py",
    "Goa": "Goa_File.py",
    "Gujarat": "Gujrat_File.py",
    "Himachal_Pradesh": "Himachal_File.py",
    "Parsi": "Parsi_File.py",
    "Tribal": "Tribal_File.py",
    "Generic_Male": "Male_File.py"
}

# LFPR values for available states
STATE_LFPR = {
    "Andhra_Pradesh": 63.4,
    "Bihar": 40.5,
    "Jammu_&_Kashmir": 52.0,
    "Karnataka": 56.2,
    "Madhya_Pradesh": 55.6,
    "Haryana": 52.4,
    "Telangana": 65.2,
    "West_Bengal": 49.8,
    "Maharashtra": 57.8,
    "Assam": 51.9,
    "Uttar_Pradesh": 41.3,
    "Chhattisgarh": 63.1,
    "Tripura": 54.3,
    "Jharkhand": 48.7,
    "Rajasthan": 55.1,
    "Delhi": 45.8,
    "Tamil_Nadu": 66.0,
    "Kerala": 52.3,
    "Odisha": 61.2,
    "Goa": 62.3,
    "Gujarat": 59.7,
    "Himachal_Pradesh": 76.0,
}

# -------------------------------------------------
# 4. Normalize LFPR to probabilities
# -------------------------------------------------
total_lfpr = sum(STATE_LFPR.values())
STATE_PROBABILITIES = {
    state: lfpr / total_lfpr
    for state, lfpr in STATE_LFPR.items()
}

# -------------------------------------------------
# 5. Compute employee count per state
# -------------------------------------------------
state_employee_counts = {
    state: round(prob * TOTAL_EMPLOYEES)
    for state, prob in STATE_PROBABILITIES.items()
}

# Adjust rounding error to hit exactly 7000
difference = TOTAL_EMPLOYEES - sum(state_employee_counts.values())
if difference != 0:
    largest_state = max(state_employee_counts, key=state_employee_counts.get)
    state_employee_counts[largest_state] += difference

print(f"📊 Employees per state: {sum(state_employee_counts.values())} total")

# -------------------------------------------------
# 6. Helper: Wrap Indigen to generate names
# -------------------------------------------------
state_functions = dynamic_import_state_functions()

def generate_names(state, num_names, name_type="full", seed_value=42):
    """
    Wrapper around Indigen dynamic functions.
    Returns a list of names for a given state.
    """
    random.seed(seed_value)

    # Get the module key for this state
    state_key = STATE_FILES_MAPPING.get(state)
    if not state_key:
        raise ValueError(f"No mapping found for state: {state}")
    
    # Remove .py extension for function lookup
    module_key = state_key.replace(".py", "")
    func = state_functions.get(module_key)

    if not callable(func):
        raise ValueError(f"No name generator found for state: {state} (module: {module_key})")

    # Call state-specific function
    try:
        names_df = func(num_names, {'name_type': name_type}, seed_value)
        
        if isinstance(names_df, pd.DataFrame) and 'name' in names_df.columns:
            return names_df['name'].tolist()
        elif isinstance(names_df, pd.DataFrame) and 'Name' in names_df.columns:
            return names_df['Name'].tolist()
        elif isinstance(names_df, (list, pd.Series)):
            return list(names_df)
        else:
            print(f"⚠️ Unexpected return type for {state}: {type(names_df)}")
            return []
    except Exception as e:
        print(f"❌ Error generating names for {state}: {e}")
        return []

# -------------------------------------------------
# 7. Generate employees and write CSV
# -------------------------------------------------
used_emails = set()
employees_generated = 0

print(f"🚀 Starting generation of {TOTAL_EMPLOYEES} employees...")

with open(CSV_PATH, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # CSV header
    writer.writerow([
        "user_id",
        "organization_id",
        "email",
        "name",
        "role",
        "profile_photo_url",
        "created_at",
        "is_active",
        "state"
    ])

    is_admin_assigned = False

    for state, count in state_employee_counts.items():
        print(f"📝 Generating {count} names for {state.replace('_', ' ')}...")
        
        # Generate names state-wise
        try:
            names = generate_names(state=state, num_names=count, seed_value=42 + employees_generated)
            
            if not names:
                print(f"⚠️ No names generated for {state}, skipping...")
                continue
                
        except ValueError as e:
            print(f"⚠️ Warning: {e}")
            continue
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

        for name in names:
            # Handle names that might not have spaces
            if " " in name:
                first_name, last_name = name.split(" ", 1)
            else:
                first_name = name
                last_name = "Employee"

            user_id = str(uuid.uuid4())

            # Create unique email
            base_email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@doordash.com"
            email = base_email
            counter = 1
            while email in used_emails:
                email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}{counter}@doordash.com"
                counter += 1
            used_emails.add(email)

            # Ensure at least one admin
            if not is_admin_assigned:
                role = "admin"
                is_admin_assigned = True
            else:
                role = random.choice(ROLES)

            # Random creation date within first year
            created_at = (
                ORG_CREATED_AT +
                timedelta(days=random.randint(1, 365))
            ).strftime("%Y-%m-%d %H:%M:%S")

            # Write row
            writer.writerow([
                user_id,
                ORGANIZATION_ID,
                email,
                name,
                role,
                None,  # profile_photo_url
                created_at,
                True,  # is_active
                state.replace("_", " ")
            ])
            
            employees_generated += 1

print(f"\n✅ {employees_generated} DoorDash employees generated successfully!")
print(f"📄 Output file: {CSV_PATH}")
print(f"📊 File size: {os.path.getsize(CSV_PATH) / 1024:.2f} KB")

# Display first few rows as verification
print("\n📋 First 5 rows preview:")
with open(CSV_PATH, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i < 6:  # Header + 5 rows
            print(line.strip())