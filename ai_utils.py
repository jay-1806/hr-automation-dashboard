"""
AI Utilities Module - Google Gemini Version (FREE TIER AVAILABLE)
Handles Google Gemini integration for natural language HR queries
Enhanced with robust error handling, general question support, and RAG
"""

import os
import re
import time
import json
from google import genai
from db_utils import get_database_schema, execute_query

# Import document processor for RAG
try:
    from document_processor import (
        get_context_for_query, 
        has_uploaded_documents,
        simple_search
    )
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


def handle_api_error(error):
    """
    Handles API errors gracefully, especially rate limits.
    Returns a user-friendly error message and whether to retry.
    """
    error_str = str(error)
    
    # Rate limit / quota exhausted
    if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
        return {
            'is_rate_limit': True,
            'should_retry': False,
            'message': """⏳ **API Rate Limit Reached**

The free Gemini API quota has been temporarily exhausted. This is normal for free tier usage.

**Options:**
1. **Wait a few minutes** - The rate limit resets periodically
2. **Try again later** - Daily limits reset every 24 hours
3. **Use a different API key** - Get a new free key at [Google AI Studio](https://aistudio.google.com/app/apikey)

**Tip:** You can still browse employee data and analytics in the other tabs while waiting!

The database and dashboard features work without AI."""
        }
    
    # Other API errors
    return {
        'is_rate_limit': False,
        'should_retry': True,
        'message': f"API Error: {error_str}"
    }


# HR Knowledge Base for general questions
HR_KNOWLEDGE_BASE = """
You are an expert HR assistant with knowledge about:

1. **HR Best Practices:**
   - Employee onboarding and offboarding procedures
   - Performance review cycles (typically quarterly or annually)
   - Employee engagement and retention strategies
   - Workplace policies and compliance

2. **Common HR Metrics:**
   - Employee turnover rate = (Employees who left / Average employees) x 100
   - Time to hire = Days from job posting to offer acceptance
   - Employee satisfaction score (typically 1-5 or 1-10 scale)
   - Cost per hire = Total recruiting costs / Number of hires

3. **Department Types:**
   - Engineering: Software development, QA, DevOps
   - Sales: Account executives, sales development
   - Marketing: Brand, content, digital marketing
   - HR: Recruiting, employee relations, benefits
   - Finance: Accounting, FP&A, payroll
   - Operations: Supply chain, facilities, admin

4. **Salary Benchmarks (General):**
   - Entry level: $40,000 - $60,000
   - Mid-level: $60,000 - $100,000
   - Senior: $100,000 - $150,000
   - Management: $120,000 - $200,000
   - Executive: $200,000+

5. **Employee Status Types:**
   - Active: Currently employed
   - On Leave: Temporary absence (medical, parental, etc.)
   - Terminated: Employment ended
   - Probation: New hire evaluation period
"""

# Models to try in order of preference (fallback if one is rate-limited)
GEMINI_MODELS = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']


def get_gemini_client():
    """
    Initializes and returns the Gemini client.
    """
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.")
    
    return genai.Client(api_key=api_key)


def call_gemini_with_fallback(client, prompt):
    """
    Calls Gemini API with automatic model fallback if rate limited.
    """
    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response
        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                last_error = e
                continue  # Try next model
            else:
                raise e  # Non-rate-limit error, raise it
    
    # All models failed with rate limit
    if last_error:
        raise last_error
    raise Exception("All Gemini models are unavailable")


def classify_question(user_question):
    """
    Classifies if a question requires database lookup, document search, or general knowledge.
    
    Returns:
        str: 'database', 'document', or 'general'
    """
    question_lower = user_question.lower()
    
    # Keywords that indicate database queries
    db_keywords = [
        'how many', 'count', 'list', 'show', 'display', 'find', 'search',
        'who is', 'who are', 'which employees', 'what employees',
        'average salary', 'total salary', 'highest paid', 'lowest paid',
        'employees in', 'employee named', 'is there', 'are there',
        'department has', 'hired', 'joined', 'transferred', 'feedback',
        'rating', 'performance', 'top', 'bottom', 'recent', 'latest'
    ]
    
    # Keywords that suggest document-based questions
    doc_keywords = [
        'policy', 'procedure', 'rule', 'guideline', 'training', 'manual',
        'handbook', 'document', 'according to', 'based on', 'what does',
        'compliance', 'regulation', 'process', 'step', 'instruction',
        'protocol', 'standard', 'requirement', 'uploaded', 'file'
    ]
    
    # Check for document-related questions first (if documents exist)
    if RAG_AVAILABLE and has_uploaded_documents():
        for keyword in doc_keywords:
            if keyword in question_lower:
                return 'document'
        
        # Also check if the question might match uploaded document content
        search_results = simple_search(user_question, top_k=1)
        if search_results and search_results[0].get('score', 0) > 5:
            return 'document'
    
    for keyword in db_keywords:
        if keyword in question_lower:
            return 'database'
    
    return 'general'


def fix_sql_quotes(sql_query):
    """
    Fixes common SQL issues like smart quotes, encoding problems, and incomplete quotes.
    """
    if not sql_query:
        return sql_query
    
    # Replace smart/curly quotes with straight quotes
    replacements = {
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '`': "'",       # Backtick to single quote for values
    }
    
    for old, new in replacements.items():
        sql_query = sql_query.replace(old, new)
    
    # Fix incomplete quotes - count single quotes, if odd, add one at the end
    single_quote_count = sql_query.count("'")
    if single_quote_count % 2 != 0:
        # Check if the query ends with % (common in LIKE patterns)
        if sql_query.rstrip().endswith('%'):
            sql_query = sql_query.rstrip() + "'"
        else:
            sql_query = sql_query + "'"
    
    return sql_query


def generate_sql_query(user_question):
    """
    Converts a natural language HR question into a SQL query using Gemini.
    """
    try:
        client = get_gemini_client()
        schema = get_database_schema()
        
        prompt = f"""You are a SQL expert. Generate ONLY a valid SQLite SELECT query.

DATABASE SCHEMA:
{schema}

CRITICAL RULES:
1. Output ONLY the raw SQL query - no explanations, no markdown
2. Use only STRAIGHT SINGLE QUOTES (') for string values, NEVER smart quotes
3. Use SELECT statements only (no INSERT, UPDATE, DELETE)
4. For name searches: use LIKE '%name%' or exact match with first_name/last_name
5. Always use proper column names from the schema
6. For employee lookups: SELECT id, first_name, last_name, email, department, position, salary FROM employees WHERE condition
7. For counts: SELECT COUNT(*) as count FROM table WHERE condition
8. For averages: SELECT ROUND(AVG(column), 2) as average FROM table
9. Use LIMIT 20 for list queries unless user specifies a number

EXAMPLES:
Q: "Is there an employee named John Smith?"
A: SELECT id, first_name, last_name, email, department, position FROM employees WHERE first_name LIKE '%John%' AND last_name LIKE '%Smith%'

Q: "How many employees in Engineering?"
A: SELECT COUNT(*) as count FROM employees WHERE department = 'Engineering'

Q: "Show top 5 highest paid employees"
A: SELECT first_name, last_name, department, salary FROM employees ORDER BY salary DESC LIMIT 5

Question: {user_question}

SQL Query:"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = call_gemini_with_fallback(client, prompt)
                
                sql_query = response.text.strip()
                
                # Extract SQL from markdown if present
                sql_match = re.search(r'```(?:sql|sqlite)?\n(.*?)\n?```', sql_query, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    sql_query = sql_match.group(1)
                
                # Clean up
                sql_query = sql_query.replace("SQL:", "").replace("Query:", "")
                sql_query = sql_query.strip('"\'` \n\r\t')
                sql_query = sql_query.rstrip(';').strip()
                sql_query = ' '.join(sql_query.split())
                
                # FIX SMART QUOTES - Critical for SQLite
                sql_query = fix_sql_quotes(sql_query)
                
                if sql_query.upper().startswith("SELECT"):
                    return sql_query, "Query generated successfully"
                    
            except Exception as retry_error:
                error_info = handle_api_error(retry_error)
                if error_info['is_rate_limit']:
                    return None, error_info['message']
                if attempt == max_retries - 1:
                    return None, f"Error generating SQL: {str(retry_error)}"
                time.sleep(1)
                continue
        
        return None, "Failed to generate valid SQL query"
        
    except Exception as e:
        error_info = handle_api_error(e)
        return None, error_info['message']


def answer_general_question(user_question):
    """
    Answers general HR questions that don't require database lookup.
    """
    try:
        client = get_gemini_client()
        
        prompt = f"""{HR_KNOWLEDGE_BASE}

You are an HR assistant for a company. Answer this question helpfully and professionally.
If the question is completely unrelated to HR or workplace topics, politely redirect to HR-related topics.

Question: {user_question}

Provide a helpful, concise answer:"""
        
        response = call_gemini_with_fallback(client, prompt)
        
        return {
            'status': 'success',
            'answer': response.text.strip(),
            'sql_query': None,
            'results': None,
            'type': 'general'
        }
        
    except Exception as e:
        error_info = handle_api_error(e)
        return {
            'status': 'error',
            'answer': error_info['message'],
            'sql_query': None,
            'results': None,
            'type': 'general',
            'is_rate_limit': error_info.get('is_rate_limit', False)
        }


def answer_document_question(user_question):
    """
    Answers questions based on uploaded documents using RAG.
    
    Args:
        user_question: User's question about uploaded documents
        
    Returns:
        dict: Contains answer, sources, and status
    """
    try:
        if not RAG_AVAILABLE:
            return {
                'status': 'error',
                'answer': "Document search is not available. Please check the document_processor module.",
                'sql_query': None,
                'results': None,
                'type': 'document'
            }
        
        # Get relevant context from documents
        context = get_context_for_query(user_question, max_chunks=4, max_chars=4000)
        
        if not context:
            return {
                'status': 'success',
                'answer': "I couldn't find relevant information in the uploaded documents. Try uploading more documents or rephrasing your question.",
                'sql_query': None,
                'results': None,
                'type': 'document'
            }
        
        client = get_gemini_client()
        
        prompt = f"""You are an HR assistant answering questions based on company documents.

DOCUMENT CONTEXT:
{context}

INSTRUCTIONS:
1. Answer the question based ONLY on the provided document context
2. If the answer is not in the documents, say so clearly
3. Quote relevant parts of the documents when helpful
4. Be concise but thorough
5. If multiple documents are relevant, synthesize the information

Question: {user_question}

Answer based on the documents:"""
        
        response = call_gemini_with_fallback(client, prompt)
        
        # Get source documents
        search_results = simple_search(user_question, top_k=3)
        sources = list(set([r['doc_name'] for r in search_results])) if search_results else []
        
        answer = response.text.strip()
        if sources:
            answer += f"\n\n📄 **Sources:** {', '.join(sources)}"
        
        return {
            'status': 'success',
            'answer': answer,
            'sql_query': None,
            'results': None,
            'type': 'document',
            'sources': sources
        }
        
    except Exception as e:
        error_info = handle_api_error(e)
        return {
            'status': 'error',
            'answer': error_info['message'],
            'sql_query': None,
            'results': None,
            'type': 'document',
            'is_rate_limit': error_info.get('is_rate_limit', False)
        }


def answer_hr_question(user_question):
    """
    Processes a natural language HR question and returns a formatted answer.
    Automatically detects if it's a database query, document search, or general question.
    """
    try:
        # Step 0: Classify the question
        question_type = classify_question(user_question)
        
        # Handle document-based questions (RAG)
        if question_type == 'document':
            return answer_document_question(user_question)
        
        # Handle general questions without database
        if question_type == 'general':
            return answer_general_question(user_question)
        
        # Step 1: Generate SQL query
        sql_query, message = generate_sql_query(user_question)
        
        if sql_query is None:
            # Fall back to general answer if SQL generation fails
            return answer_general_question(user_question)
        
        # Step 2: Execute the query with error recovery
        try:
            results = execute_query(sql_query)
            results_list = [dict(row) for row in results] if results else []
            
        except Exception as e:
            error_str = str(e)
            
            # If SQL execution fails, try to fix common issues and retry
            if 'unrecognized token' in error_str or 'syntax error' in error_str:
                # Try fixing the query
                fixed_sql = fix_sql_quotes(sql_query)
                try:
                    results = execute_query(fixed_sql)
                    results_list = [dict(row) for row in results] if results else []
                    sql_query = fixed_sql
                except:
                    # Give up and answer generally
                    general_response = answer_general_question(user_question)
                    general_response['answer'] = f"I couldn't query the database directly, but here's what I know:\n\n{general_response['answer']}"
                    return general_response
            else:
                return {
                    'status': 'error',
                    'answer': f"Error executing query: {error_str}\n\nTry rephrasing your question.",
                    'sql_query': sql_query,
                    'results': None
                }
        
        # Step 3: Format the answer
        if not results_list:
            return {
                'status': 'success',
                'answer': f"No results found for your query.\n\nI searched for: *{user_question}*\n\nTry a different search term or check the spelling.",
                'sql_query': sql_query,
                'results': []
            }
        
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
    """
    if not results:
        return "No data found matching your query."
    
    try:
        # For simple single-value results
        if len(results) == 1 and len(results[0]) == 1:
            key = list(results[0].keys())[0]
            value = results[0][key]
            
            if 'count' in key.lower():
                return f"**Result:** {value} {'employee' if value == 1 else 'employees'}"
            elif 'salary' in key.lower() or 'avg' in key.lower():
                return f"**Result:** ${value:,.2f}" if isinstance(value, (int, float)) else f"**Result:** {value}"
            elif 'rating' in key.lower():
                return f"**Result:** {value}"
            else:
                return f"**Result:** {value}"
        
        # For employee lookup (single result with details)
        if len(results) == 1 and len(results[0]) > 1:
            emp = results[0]
            name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip()
            if name:
                answer = f"**Found:** {name}\n\n"
                for k, v in emp.items():
                    if k not in ['id', 'first_name', 'last_name']:
                        label = k.replace('_', ' ').title()
                        if 'salary' in k.lower() and isinstance(v, (int, float)):
                            answer += f"- **{label}:** ${v:,.2f}\n"
                        else:
                            answer += f"- **{label}:** {v}\n"
                return answer
        
        # For tabular results - use Gemini for formatting
        client = get_gemini_client()
        results_json = json.dumps(results[:15], indent=2, default=str)
        
        prompt = f"""Format this HR data into a clear answer.

Question: {question}
Data: {results_json}

Rules:
1. Start with a brief summary
2. Use bullet points or numbered lists
3. Format salaries as $X,XXX
4. Be concise but include key details
5. If showing employees, include name and relevant info

Answer:"""
        
        response = call_gemini_with_fallback(client, prompt)
        
        return response.text.strip()
        
    except Exception as e:
        # Fallback formatting
        answer = f"**Found {len(results)} result(s):**\n\n"
        
        for i, row in enumerate(results[:10], 1):
            row_text = " | ".join([f"**{k}**: {v}" for k, v in row.items()])
            answer += f"{i}. {row_text}\n"
        
        if len(results) > 10:
            answer += f"\n_...and {len(results) - 10} more results_"
        
        return answer


def calculate_time_saved(num_queries):
    """
    Simulates time savings from using AI automation vs manual work.
    """
    avg_manual_time = 7.5
    avg_ai_time = 0.5
    
    manual_total = num_queries * avg_manual_time
    ai_total = num_queries * avg_ai_time
    time_saved = manual_total - ai_total
    
    efficiency_pct = round((time_saved / manual_total) * 100, 1) if manual_total > 0 else 0.0
    
    return {
        'queries_processed': num_queries,
        'time_saved_minutes': round(time_saved, 1),
        'time_saved_hours': round(time_saved / 60, 2),
        'efficiency_improvement': f"{efficiency_pct}%"
    }


def get_sample_questions():
    """
    Returns sample HR questions users can ask.
    """
    return [
        # Database queries
        "How many employees are in each department?",
        "What is the average salary by department?",
        "Is there an employee named Thomas Lopez?",
        "Who are the top 5 highest paid employees?",
        "Show me employees in Engineering",
        "List recent employee transfers",
        "What's the average feedback rating?",
        # General questions
        "What are HR best practices for onboarding?",
        "How do you calculate employee turnover rate?",
        "What should be included in a performance review?",
    ]
