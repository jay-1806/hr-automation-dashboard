"""
Database Utilities Module
Handles SQLite database operations for the HR Automation Dashboard
"""

import sqlite3
from datetime import datetime, timedelta
import random


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect('hr_peopleops.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def initialize_database():
    """
    Creates the database schema and populates it with dummy data.
    Creates three tables: employees, transfers, and feedback.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date DATE NOT NULL,
            salary REAL NOT NULL,
            status TEXT DEFAULT 'Active'
        )
    ''')
    
    # Create transfers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            from_department TEXT NOT NULL,
            to_department TEXT NOT NULL,
            transfer_date DATE NOT NULL,
            reason TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            feedback_date DATE NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            feedback_type TEXT NOT NULL,
            comments TEXT,
            reviewer TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
    ''')
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM employees')
    if cursor.fetchone()[0] == 0:
        # Populate with dummy data
        _populate_dummy_data(cursor)
    
    conn.commit()
    conn.close()


def _populate_dummy_data(cursor):
    """
    Populates the database with realistic dummy data.
    
    Args:
        cursor: SQLite cursor object
    """
    # Dummy employee data
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    positions = {
        'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead', 'Engineering Manager'],
        'Sales': ['Sales Rep', 'Account Executive', 'Sales Manager', 'VP Sales'],
        'Marketing': ['Marketing Specialist', 'Content Writer', 'Marketing Manager', 'CMO'],
        'HR': ['HR Coordinator', 'HR Manager', 'Recruiter', 'CHRO'],
        'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager', 'CFO'],
        'Operations': ['Operations Analyst', 'Operations Manager', 'COO', 'Project Manager']
    }
    
    first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 
                   'James', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Thomas', 
                   'Linda', 'Charles', 'Barbara', 'Daniel', 'Susan']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 
                  'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    employees_data = []
    base_date = datetime.now() - timedelta(days=365*3)  # 3 years ago
    
    for i in range(50):
        emp_id = f'EMP{str(i+1).zfill(4)}'
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        department = random.choice(departments)
        position = random.choice(positions[department])
        hire_date = base_date + timedelta(days=random.randint(0, 1095))
        salary = random.randint(50000, 150000)
        status = 'Active' if random.random() > 0.1 else 'On Leave'
        
        employees_data.append((
            emp_id, first_name, last_name, 
            f'{first_name.lower()}.{last_name.lower()}@company.com',
            department, position, hire_date.strftime('%Y-%m-%d'), 
            salary, status
        ))
    
    cursor.executemany('''
        INSERT INTO employees (employee_id, first_name, last_name, email, department, 
                             position, hire_date, salary, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', employees_data)
    
    # Dummy transfer data
    transfers_data = []
    for i in range(15):
        emp_id = f'EMP{str(random.randint(1, 50)).zfill(4)}'
        from_dept = random.choice(departments)
        to_dept = random.choice([d for d in departments if d != from_dept])
        transfer_date = datetime.now() - timedelta(days=random.randint(30, 730))
        reasons = ['Promotion', 'Career Growth', 'Project Requirements', 'Restructuring', 'Employee Request']
        reason = random.choice(reasons)
        
        transfers_data.append((
            emp_id, from_dept, to_dept, 
            transfer_date.strftime('%Y-%m-%d'), reason
        ))
    
    cursor.executemany('''
        INSERT INTO transfers (employee_id, from_department, to_department, 
                             transfer_date, reason)
        VALUES (?, ?, ?, ?, ?)
    ''', transfers_data)
    
    # Dummy feedback data
    feedback_data = []
    feedback_types = ['Performance Review', 'Peer Review', '360 Feedback', 'Manager Feedback', 'Self Assessment']
    
    for i in range(100):
        emp_id = f'EMP{str(random.randint(1, 50)).zfill(4)}'
        feedback_date = datetime.now() - timedelta(days=random.randint(1, 365))
        rating = random.randint(3, 5)
        feedback_type = random.choice(feedback_types)
        comments = [
            'Excellent performance and team collaboration',
            'Meets expectations, room for growth',
            'Outstanding technical skills',
            'Great leadership qualities',
            'Needs improvement in communication',
            'Consistently exceeds goals',
            'Strong problem-solving abilities',
            'Good team player'
        ]
        comment = random.choice(comments)
        reviewer = f'{random.choice(first_names)} {random.choice(last_names)}'
        
        feedback_data.append((
            emp_id, feedback_date.strftime('%Y-%m-%d'), 
            rating, feedback_type, comment, reviewer
        ))
    
    cursor.executemany('''
        INSERT INTO feedback (employee_id, feedback_date, rating, 
                            feedback_type, comments, reviewer)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', feedback_data)


def get_all_employees():
    """
    Retrieves all employees from the database.
    
    Returns:
        list: List of employee records
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees ORDER BY department, last_name')
    employees = cursor.fetchall()
    conn.close()
    return employees


def get_department_stats():
    """
    Calculates statistics by department.
    
    Returns:
        list: Department statistics including count, average salary, and headcount
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            department,
            COUNT(*) as employee_count,
            ROUND(AVG(salary), 2) as avg_salary,
            MIN(salary) as min_salary,
            MAX(salary) as max_salary
        FROM employees
        WHERE status = 'Active'
        GROUP BY department
        ORDER BY employee_count DESC
    ''')
    stats = cursor.fetchall()
    conn.close()
    return stats


def get_recent_transfers(limit=10):
    """
    Retrieves recent employee transfers.
    
    Args:
        limit (int): Maximum number of records to return
        
    Returns:
        list: Recent transfer records
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            t.employee_id,
            e.first_name || ' ' || e.last_name as employee_name,
            t.from_department,
            t.to_department,
            t.transfer_date,
            t.reason
        FROM transfers t
        JOIN employees e ON t.employee_id = e.employee_id
        ORDER BY t.transfer_date DESC
        LIMIT ?
    ''', (limit,))
    transfers = cursor.fetchall()
    conn.close()
    return transfers


def get_feedback_summary():
    """
    Calculates feedback summary statistics.
    
    Returns:
        dict: Summary statistics including average rating and total feedback count
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_feedback,
            ROUND(AVG(rating), 2) as avg_rating,
            COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback
        FROM feedback
    ''')
    summary = cursor.fetchone()
    conn.close()
    return dict(summary)


def execute_query(query):
    """
    Executes a custom SQL query and returns results.
    Used by the AI to answer natural language questions.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        list: Query results
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def get_database_schema():
    """
    Returns the database schema information for AI context.
    
    Returns:
        str: Formatted database schema description
    """
    schema = """
    Database Schema:
    
    1. employees table:
       - id: INTEGER PRIMARY KEY
       - employee_id: TEXT UNIQUE (format: EMP####)
       - first_name: TEXT
       - last_name: TEXT
       - email: TEXT
       - department: TEXT (Engineering, Sales, Marketing, HR, Finance, Operations)
       - position: TEXT
       - hire_date: DATE
       - salary: REAL
       - status: TEXT (Active, On Leave)
    
    2. transfers table:
       - id: INTEGER PRIMARY KEY
       - employee_id: TEXT (foreign key to employees)
       - from_department: TEXT
       - to_department: TEXT
       - transfer_date: DATE
       - reason: TEXT
    
    3. feedback table:
       - id: INTEGER PRIMARY KEY
       - employee_id: TEXT (foreign key to employees)
       - feedback_date: DATE
       - rating: INTEGER (1-5)
       - feedback_type: TEXT
       - comments: TEXT
       - reviewer: TEXT
    """
    return schema
