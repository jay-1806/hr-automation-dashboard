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
        
        # System prompt for SQL generation - MORE SPECIFIC AND ROBUST
        prompt = f"""You are a SQL expert. Generate ONLY a valid SQLite SELECT query for this question.

DATABASE TABLES:
{schema}

IMPORTANT RULES:
1. Output ONLY the SQL query - nothing else
2. Use SELECT statements only
3. For employee queries: JOIN with employees table and use status='Active'
4. For counts: use COUNT(*) or COUNT(column_name)
5. For averages: use AVG(column_name) and ROUND to 2 decimals
6. For listings: SELECT relevant columns and use LIMIT if not specified
7. Always use proper JOINs when combining tables
8. For "who" questions: return first_name, last_name, and relevant details
9. For "how many" questions: use COUNT(*)
10. For "average" questions: use AVG() and GROUP BY

COMMON PATTERNS:
- "How many X in Y?" → SELECT COUNT(*) FROM table WHERE condition
- "Average X by Y?" → SELECT Y, AVG(X) FROM table GROUP BY Y
- "Top N X" → SELECT columns FROM table ORDER BY column DESC LIMIT N
- "Who is/are X?" → SELECT first_name, last_name FROM employees WHERE condition
- "List X" → SELECT columns FROM table WHERE condition LIMIT 20

Question: {user_question}

Generate the SQL query:

"""
        
        # Try to generate the query with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt,
                    config={
                        'temperature': 0.1,  # Low temperature for more deterministic output
                        'max_output_tokens': 200,
                    }
                )
                
                sql_query = response.text.strip()
                
                # Aggressive cleanup
                sql_query = sql_query.replace("```sql", "").replace("```", "")
                sql_query = sql_query.replace("SQL:", "").replace("Query:", "")
                sql_query = sql_query.strip('"\'` \n\r')
                
                # Remove multiline and extra spaces
                sql_query = ' '.join(sql_query.split())
                
                # Validate
                if sql_query.upper().startswith("SELECT"):
                    return sql_query, "Query generated successfully"
                    
            except Exception as retry_error:
                if attempt == max_retries - 1:
                    raise retry_error
                continue
        
        return None, "Failed to generate valid SQL query after retries"
        
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
    Formats query results into a natural language answer.
    
    Args:
        question (str): Original user question
        results (list): Query results as list of dictionaries
        sql_query (str): The SQL query that was executed
        
    Returns:
        str: Natural language answer
    """
    # If no results
    if not results:
        return "❌ No data found matching your query."
    
    try:
        # For simple single-value results
        if len(results) == 1 and len(results[0]) == 1:
            key = list(results[0].keys())[0]
            value = results[0][key]
            
            # Format based on key name
            if 'count' in key.lower():
                return f"📊 **Result:** {value} {'employee' if value == 1 else 'employees'}"
            elif 'salary' in key.lower() or 'avg' in key.lower():
                return f"💰 **Result:** ${value:,.2f}" if isinstance(value, (int, float)) else f"**Result:** {value}"
            elif 'rating' in key.lower():
                return f"⭐ **Result:** {value}"
            else:
                return f"**Result:** {value}"
        
        # For tabular results - use Gemini for better formatting
        client = get_gemini_client()
        results_json = json.dumps(results[:20], indent=2, default=str)  # Limit to 20 results
        
        prompt = f"""Format this HR data into a clear, natural language answer.

Question: {question}
Data: {results_json}

Rules:
1. Start with a summary sentence
2. Use bullet points or numbered lists for clarity
3. Include relevant details (names, departments, numbers)
4. Format money as $X,XXX
5. Keep it professional and concise
6. If more than 10 items, show top 10 and mention total count

Answer:"""
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={'temperature': 0.3, 'max_output_tokens': 500}
        )
        
        return response.text.strip()
        
    except Exception as e:
        # Robust fallback formatting
        answer = f"📋 **Found {len(results)} result(s):**\n\n"
        
        for i, row in enumerate(results[:10], 1):
            row_text = " | ".join([f"**{k}**: {v}" for k, v in row.items()])
            answer += f"{i}. {row_text}\n"
        
        if len(results) > 10:
            answer += f"\n_...and {len(results) - 10} more results_"
        
        return answer


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
