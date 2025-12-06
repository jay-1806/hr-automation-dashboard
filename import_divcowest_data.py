"""
Import DivcoWest directory data into the HR database.
Generates realistic values for missing fields like salary, status, hire_date, etc.
"""

import sqlite3
import csv
import random
from datetime import datetime, timedelta

# Salary ranges based on title level
SALARY_RANGES = {
    'Chief': (250000, 450000),
    'President': (220000, 380000),
    'Founder': (300000, 500000),
    'General Counsel': (200000, 350000),
    'Senior Managing Director': (180000, 300000),
    'Managing Director': (150000, 250000),
    'Head of': (140000, 230000),
    'Senior Director': (120000, 180000),
    'Director': (100000, 160000),
    'Associate Director': (85000, 130000),
    'Senior': (75000, 120000),
    'Manager': (70000, 110000),
    'Associate': (55000, 85000),
    'Analyst': (50000, 80000),
    'Coordinator': (45000, 65000),
    'Assistant': (40000, 60000),
    'Staff': (45000, 70000),
    'Specialist': (50000, 75000),
    'Engineer': (90000, 150000),
    'Default': (50000, 90000)
}

def get_salary_range(title):
    """Get appropriate salary range based on title."""
    title_upper = title.upper()
    for key, range_val in SALARY_RANGES.items():
        if key.upper() in title_upper:
            return range_val
    return SALARY_RANGES['Default']

def generate_email(name):
    """Generate email from name."""
    parts = name.lower().replace('.', '').replace(',', '').split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1]}@divcowest.com"
    return f"{parts[0]}@divcowest.com"

def generate_employee_id(index, department):
    """Generate employee ID."""
    dept_codes = {
        'EXECUTIVE TEAM': 'EXE',
        'EXECUTIVE LEADERSHIP': 'EXL',
        'INVESTMENTS': 'INV',
        'CONSTRUCTION & DEVELOPMENT': 'CND',
        'CAPITAL FORMATION & PORTFOLIO MGMT': 'CAP',
        'PROPERTY MANAGEMENT': 'PRM',
        'LEASING & MARKETING': 'LMK',
        'FINANCE LEGAL & ADMIN': 'FLA'
    }
    code = dept_codes.get(department, 'EMP')
    return f"{code}{str(index).zfill(4)}"

def generate_hire_date():
    """Generate random hire date within last 10 years."""
    days_ago = random.randint(30, 3650)  # 1 month to 10 years
    return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

def main():
    # Read CSV
    employees = []
    with open('divcowest_directory.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            employees.append(row)
    
    print(f"Read {len(employees)} employees from CSV")
    
    # Remove duplicates based on name (some people appear in multiple departments)
    seen_names = set()
    unique_employees = []
    for emp in employees:
        if emp['name'] not in seen_names:
            seen_names.add(emp['name'])
            unique_employees.append(emp)
    
    print(f"Unique employees: {len(unique_employees)}")
    
    # Connect to database
    conn = sqlite3.connect('hr_peopleops.db')
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM employees")
    cursor.execute("DELETE FROM transfers")
    cursor.execute("DELETE FROM feedback")
    conn.commit()
    print("Cleared existing data")
    
    # Insert employees
    statuses = ['Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'On Leave', 'Terminated']
    
    for i, emp in enumerate(unique_employees, 1):
        name = emp['name']
        name_parts = name.replace('.', '').replace(',', '').split()
        first_name = name_parts[0] if name_parts else 'Unknown'
        last_name = name_parts[-1] if len(name_parts) > 1 else 'Unknown'
        
        title = emp['title'] if emp['title'] else 'Employee'
        department = emp['department']
        location = emp['location'] if emp['location'] else random.choice(['San Francisco', 'Cambridge', 'Los Angeles', 'New York'])
        
        # Generate missing data
        salary_range = get_salary_range(title)
        salary = random.randint(salary_range[0], salary_range[1])
        email = generate_email(name)
        employee_id = generate_employee_id(i, department)
        hire_date = generate_hire_date()
        status = random.choice(statuses)
        
        cursor.execute("""
            INSERT INTO employees (employee_id, first_name, last_name, email, department, position, salary, hire_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (employee_id, first_name, last_name, email, department, title, salary, hire_date, status))
    
    conn.commit()
    print(f"Inserted {len(unique_employees)} employees")
    
    # Get list of employee IDs
    cursor.execute("SELECT employee_id, first_name, last_name, department FROM employees")
    all_emps = cursor.fetchall()
    
    # Get unique departments
    departments = list(set(emp[3] for emp in all_emps))
    
    # Generate some transfers (for about 20 employees)
    for emp_id, first, last, current_dept in random.sample(all_emps, min(20, len(all_emps))):
        other_depts = [d for d in departments if d != current_dept]
        if other_depts:
            from_dept = random.choice(other_depts)
            transfer_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
            cursor.execute("""
                INSERT INTO transfers (employee_id, from_department, to_department, transfer_date, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (emp_id, from_dept, current_dept, transfer_date, random.choice([
                'Promotion', 'Restructuring', 'Career Development', 'Team Expansion', 'Skills Match'
            ])))
    
    conn.commit()
    print("Inserted transfers")
    
    # Generate feedback (for about 40 employees)
    feedback_types = ['Performance Review', 'Peer Feedback', '360 Review', 'Manager Feedback', 'Self Assessment']
    reviewers = ['HR Team', 'Direct Manager', 'Department Head', 'Peer Review Committee', 'Self']
    
    for emp_id, first, last, dept in random.sample(all_emps, min(40, len(all_emps))):
        feedback_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d')
        rating = random.choices([3, 4, 5, 4, 5], weights=[10, 25, 35, 20, 10])[0]
        cursor.execute("""
            INSERT INTO feedback (employee_id, feedback_date, rating, feedback_type, comments, reviewer)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (emp_id, feedback_date, rating, random.choice(feedback_types), 
              random.choice([
                  "Excellent performance and team collaboration.",
                  "Consistently meets expectations and deadlines.",
                  "Shows great initiative and leadership potential.",
                  "Good work ethic, room for improvement in communication.",
                  "Outstanding contribution to recent projects.",
                  "Reliable team member with strong technical skills.",
                  "Demonstrates excellent problem-solving abilities.",
                  "Great attention to detail and quality work.",
                  "Strong communication and interpersonal skills.",
                  "Proactive in identifying and resolving issues."
              ]),
              random.choice(reviewers)))
    
    conn.commit()
    print("Inserted feedback")
    
    # Summary
    cursor.execute("SELECT COUNT(*) FROM employees")
    emp_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM transfers")
    transfer_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM feedback")
    feedback_count = cursor.fetchone()[0]
    cursor.execute("SELECT department, COUNT(*) as cnt FROM employees GROUP BY department ORDER BY cnt DESC")
    dept_stats = cursor.fetchall()
    
    print(f"\n=== Import Complete ===")
    print(f"Total Employees: {emp_count}")
    print(f"Total Transfers: {transfer_count}")
    print(f"Total Feedback Records: {feedback_count}")
    print(f"\nEmployees by Department:")
    for dept, count in dept_stats:
        print(f"  {dept}: {count}")
    
    # Show sample employees
    cursor.execute("SELECT employee_id, first_name, last_name, position, department, salary FROM employees LIMIT 5")
    print(f"\nSample Employees:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} {row[2]} - {row[3]} ({row[4]}) - ${row[5]:,}")
    
    conn.close()

if __name__ == "__main__":
    main()
