"""
AI Utilities Module - Google Gemini Version (FREE TIER AVAILABLE)
Handles Google Gemini integration for natural language HR queries
"""

import os
from google import genai
from db_utils import get_database_schema, execute_query
import json


def get_gemini_client():
    """
    Initializes and returns the Gemini client.
    
    Returns:
        genai.Client: Configured Gemini client
        
    Raises:
        ValueError: If GEMINI_API_KEY is not set
    """
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set. Please configure your API key.")
    
    client = genai.Client(api_key=api_key)
    return client


def generate_sql_query(user_question):
    """
    Converts a natural language HR question into a SQL query using Gemini.
    
    Args:
        user_question (str): Natural language question from user
        
    Returns:
        tuple: (sql_query, explanation) or (None, error_message)
    """
    try:
        client = get_gemini_client()
        schema = get_database_schema()
        
        # System prompt for SQL generation
        prompt = f"""You are an expert SQL query generator. Convert the user's question into a valid SQL query.

DATABASE SCHEMA:
{schema}

AVAILABLE TABLES:
- employees: employee information (id, name, department, position, salary, hire_date, status)
- transfers: department transfer history
- feedback: employee feedback and ratings

NOTE: If the question asks about data NOT in the database (like leave/attendance, current location, etc.), respond with exactly: "DATA_NOT_AVAILABLE"

CRITICAL RULES:
1. Output ONLY the SQL query - no explanations, no markdown, no extra text
2. Do not include the word "SQL" or "SQLite" in your output
3. Use standard SQL syntax compatible with SQLite
4. Always filter by status = 'Active' when querying employees unless specifically asked for all statuses
5. Use appropriate JOINs when needed
6. Return meaningful column aliases (use AS)
7. For questions about department heads/managers, look for positions containing: Manager, Director, VP, Chief, Head, Lead

EXAMPLE QUERIES:
Question: "How many employees are in Engineering?"
SELECT COUNT(*) as employee_count FROM employees WHERE department = 'Engineering' AND status = 'Active'

Question: "What is the average salary by department?"
SELECT department, ROUND(AVG(salary), 2) as average_salary FROM employees WHERE status = 'Active' GROUP BY department ORDER BY average_salary DESC

Question: "Show me the top 5 highest paid employees"
SELECT first_name, last_name, department, position, salary FROM employees WHERE status = 'Active' ORDER BY salary DESC LIMIT 5

Question: "Who are the department heads?"
SELECT department, first_name, last_name, position, salary FROM employees WHERE status = 'Active' AND (position LIKE '%Manager%' OR position LIKE '%Head%' OR position LIKE '%Director%' OR position LIKE '%VP%' OR position LIKE '%Chief%' OR position LIKE '%Lead%') ORDER BY department

USER QUESTION: {user_question}

SQL QUERY:"""
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',  # Fast and free model
            contents=prompt
        )
        
        sql_query = response.text.strip()
        
        # Clean up the query (remove markdown code blocks if present)
        if sql_query.startswith("```sql"):
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query.replace("```", "").strip()
        
        # Remove any leading/trailing quotes
        sql_query = sql_query.strip('"\'')
        
        # Remove any "SQL QUERY:" prefix if present
        if sql_query.upper().startswith("SQL QUERY:"):
            sql_query = sql_query[10:].strip()
        
        # Remove any line breaks and extra spaces
        sql_query = ' '.join(sql_query.split())
        
        # Check if data is not available
        if "DATA_NOT_AVAILABLE" in sql_query.upper():
            return None, "The requested information is not available in the database. The database only contains: employee information (name, department, position, salary, hire date), transfer history, and feedback/ratings. There is no leave/attendance data available."
        
        # Validate that it's a SELECT statement
        if not sql_query.upper().startswith("SELECT"):
            return None, f"Generated query must be a SELECT statement. Got: {sql_query[:100]}"
        
        return sql_query, "Query generated successfully"
        
    except Exception as e:
        return None, f"Error generating SQL query: {str(e)}"


def answer_hr_question(user_question):
    """
    Processes a natural language HR question and returns a formatted answer.
    
    Args:
        user_question (str): User's natural language question
        
    Returns:
        dict: Contains 'answer', 'sql_query', 'results', and 'status'
    """
    try:
        # Step 1: Generate SQL query from natural language
        sql_query, message = generate_sql_query(user_question)
        
        if sql_query is None:
            return {
                'status': 'error',
                'answer': message,
                'sql_query': None,
                'results': None
            }
        
        # Step 2: Execute the query
        try:
            results = execute_query(sql_query)
            
            # Convert results to list of dicts for easier processing
            if results:
                results_list = [dict(row) for row in results]
            else:
                results_list = []
            
        except Exception as e:
            return {
                'status': 'error',
                'answer': f"Error executing query: {str(e)}",
                'sql_query': sql_query,
                'results': None
            }
        
        # Step 3: Generate natural language answer from results
        answer = format_answer(user_question, results_list, sql_query)
        
        return {
            'status': 'success',
            'answer': answer,
            'sql_query': sql_query,
            'results': results_list
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'answer': f"Unexpected error: {str(e)}",
            'sql_query': None,
            'results': None
        }


def format_answer(question, results, sql_query):
    """
    Formats query results into a natural language answer using Gemini.
    
    Args:
        question (str): Original user question
        results (list): Query results as list of dictionaries
        sql_query (str): The SQL query that was executed
        
    Returns:
        str: Natural language answer
    """
    try:
        client = get_gemini_client()
        
        # If no results, provide appropriate message
        if not results:
            return "No results found for your query. The data might not exist in the database or the query returned empty results."
        
        # Prepare results for Gemini
        results_json = json.dumps(results, indent=2, default=str)
        
        prompt = f"""You are a helpful HR assistant. You have access to query results from an HR database.
Your task is to convert these results into clear, natural language answers.

Guidelines:
1. Be concise but informative
2. Use proper formatting (bullet points, numbers) when appropriate
3. Highlight key insights or patterns in the data
4. If showing numerical data, include context (e.g., "The average salary is $85,000")
5. For lists of employees, format them nicely
6. Don't mention SQL or technical details unless relevant

Question: {question}

Query Results:
{results_json}

Please provide a clear, natural language answer based on these results."""
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        # Fallback to basic formatting if Gemini fails
        if len(results) == 1 and len(results[0]) == 1:
            # Single value result
            value = list(results[0].values())[0]
            return f"Result: {value}"
        else:
            # Multiple results - basic formatting
            return f"Found {len(results)} result(s). Data: {str(results[:5])}"


def calculate_time_saved(num_queries):
    """
    Simulates time savings from using AI automation vs manual work.
    Assumes average manual query takes 5-10 minutes.
    
    Args:
        num_queries (int): Number of queries processed
        
    Returns:
        dict: Time savings metrics
    """
    avg_manual_time = 7.5  # minutes per query
    avg_ai_time = 0.5  # minutes per query
    
    manual_total = num_queries * avg_manual_time
    ai_total = num_queries * avg_ai_time
    time_saved = manual_total - ai_total
    
    # Avoid division by zero
    if manual_total > 0:
        efficiency_pct = round((time_saved / manual_total) * 100, 1)
    else:
        efficiency_pct = 0.0
    
    return {
        'queries_processed': num_queries,
        'time_saved_minutes': round(time_saved, 1),
        'time_saved_hours': round(time_saved / 60, 2),
        'efficiency_improvement': f"{efficiency_pct}%"
    }


def get_sample_questions():
    """
    Returns a list of sample HR questions users can ask.
    
    Returns:
        list: Sample questions
    """
    return [
        "How many employees are in each department?",
        "What is the average salary by department?",
        "Show me recent employee transfers",
        "Who are the top 5 highest paid employees?",
        "What's the average feedback rating?",
        "How many employees were hired in the last year?",
        "Which department has the highest average rating?",
        "Show me employees with 5-star ratings",
        "What are the most common transfer reasons?",
        "List employees in the Engineering department"
    ]
