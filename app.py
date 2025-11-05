"""
HR Automation Dashboard - Main Application
Built with Streamlit, SQLite, and LangChain 
This application provides an interactive dashboard for HR operations,
allowing users to query employee data using natural language and view
comprehensive analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Import custom modules
from db_utils import (
    initialize_database,
    get_all_employees,
    get_department_stats,
    get_recent_transfers,
    get_feedback_summary
)
from ai_utils import (
    answer_hr_question,
    calculate_time_saved,
    get_sample_questions
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="HR Automation Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI with vibrant colors and better readability
st.markdown("""
    <style>
    /* Main theme colors */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Content area with white background */
    .block-container {
        background-color: #ffffff !important;
        padding: 3rem 2rem 2rem 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    
    /* Override Streamlit's dark theme elements */
    div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    
    /* SQL code syntax highlighting override */
    .language-sql {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
    }
    
    /* Prevent ANY element from having black background */
    div[style*="background-color: rgb(0, 0, 0)"],
    div[style*="background-color: black"],
    div[style*="background: rgb(0, 0, 0)"],
    div[style*="background: black"] {
        background-color: #f9fafb !important;
        background: #f9fafb !important;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        padding-top: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }
    
    /* Fix for all headings and text in main content */
    h1, h2, h3, h4, h5, h6 {
        color: #1f2937 !important;
    }
    
    /* Subheaders in sections */
    .element-container h2, .element-container h3 {
        color: #374151 !important;
        font-weight: 600 !important;
    }
    
    /* All paragraph text */
    p {
        color: #1f2937 !important;
    }
    
    /* Chart titles and labels */
    .plot-container text {
        fill: #1f2937 !important;
    }
    
    /* Code blocks - always visible */
    code {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: monospace;
    }
    
    /* Pre-formatted text blocks */
    pre {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        overflow-x: auto;
    }
    
    /* Stale code blocks */
    .stCodeBlock {
        background-color: #f9fafb !important;
    }
    .stCodeBlock code {
        color: #1f2937 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stSidebar"] .element-container {
        color: white;
    }
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    [data-testid="stMetricLabel"] {
        color: #374151;
        font-weight: 600;
    }
    
    /* Chat messages - User messages */
    [data-testid="stChatMessageContent"] {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    /* Chat messages - make text visible */
    .stChatMessage p {
        color: #1f2937 !important;
    }
    
    /* User messages background */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]:first-child) {
        background-color: #e0e7ff !important;
    }
    
    /* Assistant messages background */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]:last-child) {
        background-color: #f0fdf4 !important;
    }
    
    /* Chat input - clean and professional */
    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        margin: 1rem 0;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 1rem !important;
        color: #1f2937 !important;
        background-color: #ffffff !important;
        padding: 0.5rem;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #9ca3af !important;
    }
    [data-testid="stChatInput"] input {
        color: #1f2937 !important;
        background-color: #ffffff !important;
    }
    
    /* Chat input container positioning */
    .stChatInputContainer {
        padding: 1rem;
        background-color: #f9fafb;
        border-top: 1px solid #e5e7eb;
        border-radius: 0 0 12px 12px;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f3f4f6;
        border-radius: 8px 8px 0 0;
        color: #374151;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Expander - always visible text, never black background */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
    
    [data-testid="stExpander"] summary {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border-radius: 8px;
    }
    
    [data-testid="stExpander"] summary:hover {
        background-color: #e5e7eb !important;
        color: #111827 !important;
    }
    
    [data-testid="stExpander"] summary * {
        color: #1f2937 !important;
    }
    
    /* Expander content area */
    [data-testid="stExpander"] > div > div {
        background-color: #ffffff !important;
        padding: 1rem;
    }
    
    /* Code blocks inside expander - prevent black background */
    [data-testid="stExpander"] .stCodeBlock {
        background-color: #f9fafb !important;
    }
    
    [data-testid="stExpander"] code {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
        display: block;
        padding: 1rem !important;
        border-radius: 4px;
        white-space: pre-wrap;
    }
    
    [data-testid="stExpander"] pre {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    /* JSON viewer in expander */
    [data-testid="stExpander"] .stJson {
        background-color: #f9fafb !important;
        color: #1f2937 !important;
    }
    
    /* Legacy expander selectors */
    .streamlit-expanderHeader {
        background-color: #f3f4f6 !important;
        border-radius: 8px;
        color: #1f2937 !important;
        font-weight: 600;
    }
    .streamlit-expanderHeader:hover {
        background-color: #e5e7eb !important;
        color: #1f2937 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        color: #065f46;
    }
    .stInfo {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        color: #1e40af;
    }
    .stError {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        color: #991b1b;
    }
    
    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)


def initialize_app():
    """
    Initializes the application by setting up the database and session state.
    """
    # Initialize database on first run
    if 'db_initialized' not in st.session_state:
        with st.spinner('Initializing database...'):
            initialize_database()
            st.session_state.db_initialized = True
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize query counter for time savings
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0


def render_sidebar():
    """
    Renders the sidebar with navigation and configuration options.
    """
    with st.sidebar:
        st.markdown("### 👥 HR Automation Dashboard")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigate to:",
            ["📊 Dashboard", "🔬 Advanced Analytics", "🤖 AI Assistant", "📋 Data Explorer"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # API Key status
        st.markdown("### ⚙️ Configuration")
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if api_key:
            st.success("✓ Gemini API Key Configured")
        else:
            st.error("✗ API Key Missing")
            st.info("Add GEMINI_API_KEY to your .env file")
        
        st.markdown("---")
        
        # Sample questions
        st.markdown("### 💡 Sample Questions")
        sample_questions = get_sample_questions()
        
        st.markdown("*Click to use:*")
        for i, question in enumerate(sample_questions[:5]):
            if st.button(question, key=f"sample_{i}", use_container_width=True):
                st.session_state.selected_question = question
        
        st.markdown("---")
        st.markdown("### 📈 Statistics")
        st.metric("Total Queries", st.session_state.query_count)
        
        time_saved = calculate_time_saved(st.session_state.query_count)
        if st.session_state.query_count > 0:
            st.metric(
                "Time Saved",
                f"{time_saved['time_saved_hours']} hrs",
                delta=time_saved['efficiency_improvement']
            )
    
    return page


def render_dashboard():
    """
    Renders the main dashboard view with metrics and visualizations.
    """
    st.markdown('<p class="main-header">📊 HR Operations Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time insights into your workforce</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Get data
    dept_stats = get_department_stats()
    feedback_summary = get_feedback_summary()
    recent_transfers = get_recent_transfers(5)
    all_employees = get_all_employees()
    
    # Convert to DataFrames
    df_dept = pd.DataFrame([dict(row) for row in dept_stats])
    df_employees = pd.DataFrame([dict(row) for row in all_employees])
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_employees = df_dept['employee_count'].sum()
        st.metric(
            "Total Active Employees",
            f"{total_employees}",
            delta="Active workforce"
        )
    
    with col2:
        avg_salary = df_dept['avg_salary'].mean()
        st.metric(
            "Average Salary",
            f"${avg_salary:,.0f}",
            delta=f"Across {len(df_dept)} departments"
        )
    
    with col3:
        st.metric(
            "Total Feedback",
            f"{feedback_summary['total_feedback']}",
            delta=f"{feedback_summary['avg_rating']}⭐ avg rating"
        )
    
    with col4:
        positive_rate = (feedback_summary['positive_feedback'] / feedback_summary['total_feedback']) * 100
        st.metric(
            "Positive Feedback",
            f"{positive_rate:.1f}%",
            delta="Ratings 4+"
        )
    
    st.markdown("---")
    
    # Visualization row 1 - Enhanced with better tooltips
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Employee Distribution by Department")
        fig_dept = px.bar(
            df_dept,
            x='department',
            y='employee_count',
            color='employee_count',
            color_continuous_scale='Blues',
            title='',
            labels={'employee_count': 'Number of Employees', 'department': 'Department'},
            text='employee_count'
        )
        fig_dept.update_traces(
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Employees: %{y}<extra></extra>'
        )
        fig_dept.update_layout(
            showlegend=False, 
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_dept, use_container_width=True)
    
    with col2:
        st.subheader("💰 Average Salary by Department")
        fig_salary = px.bar(
            df_dept,
            x='department',
            y='avg_salary',
            color='avg_salary',
            color_continuous_scale='Greens',
            title='',
            labels={'avg_salary': 'Average Salary ($)', 'department': 'Department'},
            text='avg_salary'
        )
        fig_salary.update_traces(
            texttemplate='$%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Avg Salary: $%{y:,.0f}<extra></extra>'
        )
        fig_salary.update_layout(
            showlegend=False, 
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_salary, use_container_width=True)
    
    st.markdown("---")
    
    # Visualization row 2 - Interactive Sunburst and Salary Range Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Workforce Composition")
        # Create sunburst chart for hierarchical view
        df_sunburst = df_employees[['department', 'position']].copy()
        df_sunburst['count'] = 1
        
        fig_sunburst = px.sunburst(
            df_sunburst,
            path=['department', 'position'],
            values='count',
            title='',
            color='department',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_sunburst.update_traces(
            hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
        )
        fig_sunburst.update_layout(
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=11),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
    
    with col2:
        st.subheader("💵 Salary Distribution")
        # Create salary ranges
        df_employees['salary_range'] = pd.cut(
            df_employees['salary'],
            bins=[0, 60000, 80000, 100000, 120000, float('inf')],
            labels=['< $60k', '$60k-$80k', '$80k-$100k', '$100k-$120k', '> $120k']
        )
        salary_dist = df_employees['salary_range'].value_counts().reset_index()
        salary_dist.columns = ['Salary Range', 'Count']
        
        fig_salary_dist = px.bar(
            salary_dist,
            x='Salary Range',
            y='Count',
            color='Salary Range',
            title='',
            text='Count',
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_salary_dist.update_traces(
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Employees: %{y}<extra></extra>'
        )
        fig_salary_dist.update_layout(
            showlegend=False,
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            ),
            xaxis_title="Salary Range",
            yaxis_title="Number of Employees"
        )
        st.plotly_chart(fig_salary_dist, use_container_width=True)
    
    st.markdown("---")
    
    # Visualization row 3 - Tenure Analysis and Department Comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Employee Tenure Distribution")
        # Calculate tenure
        df_employees['hire_date'] = pd.to_datetime(df_employees['hire_date'])
        df_employees['tenure_years'] = (datetime.now() - df_employees['hire_date']).dt.days / 365.25
        df_employees['tenure_category'] = pd.cut(
            df_employees['tenure_years'],
            bins=[0, 1, 3, 5, 10, float('inf')],
            labels=['< 1 year', '1-3 years', '3-5 years', '5-10 years', '> 10 years']
        )
        
        tenure_dist = df_employees['tenure_category'].value_counts().reset_index()
        tenure_dist.columns = ['Tenure', 'Count']
        tenure_dist = tenure_dist.sort_values('Tenure')
        
        fig_tenure = px.line(
            tenure_dist,
            x='Tenure',
            y='Count',
            markers=True,
            title='',
            text='Count'
        )
        fig_tenure.update_traces(
            line_color='#667eea',
            marker=dict(size=12, color='#764ba2'),
            textposition='top center',
            hovertemplate='<b>%{x}</b><br>Employees: %{y}<extra></extra>'
        )
        fig_tenure.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            ),
            xaxis_title="Tenure Period",
            yaxis_title="Number of Employees"
        )
        st.plotly_chart(fig_tenure, use_container_width=True)
    
    with col2:
        st.subheader("🔄 Department Transfer Flow")
        if recent_transfers:
            df_transfers = pd.DataFrame([dict(row) for row in recent_transfers])
            
            # Create Sankey diagram data
            from_depts = df_transfers['from_department'].tolist()
            to_depts = df_transfers['to_department'].tolist()
            
            # Get unique departments
            all_depts = list(set(from_depts + to_depts))
            dept_indices = {dept: i for i, dept in enumerate(all_depts)}
            
            # Create links
            links = {}
            for _, row in df_transfers.iterrows():
                key = (row['from_department'], row['to_department'])
                links[key] = links.get(key, 0) + 1
            
            source = [dept_indices[from_dept] for from_dept, _ in links.keys()]
            target = [dept_indices[to_dept] for _, to_dept in links.keys()]
            value = list(links.values())
            
            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=all_depts,
                    color="#667eea"
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color="rgba(102, 126, 234, 0.3)"
                )
            )])
            
            fig_sankey.update_layout(
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#1f2937', size=12),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=14,
                    font_family="Arial",
                    font_color="#1f2937"
                )
            )
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.info("No recent transfers to display")
    
    st.markdown("---")
    
    # Visualization row 4 - Scatter plot and Heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💼 Salary vs Tenure Analysis")
        fig_scatter = px.scatter(
            df_employees,
            x='tenure_years',
            y='salary',
            color='department',
            size='salary',
            hover_data=['first_name', 'last_name', 'position'],
            title='',
            labels={'tenure_years': 'Years of Service', 'salary': 'Annual Salary ($)'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_scatter.update_traces(
            hovertemplate='<b>%{customdata[0]} %{customdata[1]}</b><br>' +
                         'Position: %{customdata[2]}<br>' +
                         'Tenure: %{x:.1f} years<br>' +
                         'Salary: $%{y:,.0f}<extra></extra>'
        )
        fig_scatter.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        st.subheader("📊 Department Metrics Comparison")
        # Create a grouped bar chart
        fig_dept_comparison = go.Figure()
        
        fig_dept_comparison.add_trace(go.Bar(
            name='Employees',
            x=df_dept['department'],
            y=df_dept['employee_count'],
            marker_color='#667eea',
            hovertemplate='<b>%{x}</b><br>Employees: %{y}<extra></extra>'
        ))
        
        fig_dept_comparison.add_trace(go.Bar(
            name='Avg Salary (÷1000)',
            x=df_dept['department'],
            y=df_dept['avg_salary'] / 1000,
            marker_color='#764ba2',
            hovertemplate='<b>%{x}</b><br>Avg Salary: $%{y:.1f}k<extra></extra>'
        ))
        
        fig_dept_comparison.update_layout(
            barmode='group',
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            ),
            xaxis_title="Department",
            yaxis_title="Value",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_dept_comparison, use_container_width=True)
    
    st.markdown("---")
    
    # Time savings simulation
    st.subheader("⏱️ Automation Impact")
    col1, col2, col3, col4 = st.columns(4)
    
    # Simulate queries for demo purposes
    demo_queries = 50
    time_metrics = calculate_time_saved(demo_queries)
    
    with col1:
        st.metric("Queries Automated", time_metrics['queries_processed'])
    
    with col2:
        st.metric("Time Saved", f"{time_metrics['time_saved_hours']} hours")
    
    with col3:
        st.metric("Efficiency Gain", time_metrics['efficiency_improvement'])
    
    with col4:
        cost_saved = time_metrics['time_saved_hours'] * 50  # Assuming $50/hour
        st.metric("Cost Savings", f"${cost_saved:,.0f}")
    
    # Progress bar for time savings
    progress = min(time_metrics['time_saved_hours'] / 100, 1.0)
    st.progress(progress)
    st.caption(f"🎯 Goal: 100 hours saved | Current: {time_metrics['time_saved_hours']} hours")


def render_ai_assistant():
    """
    Renders the AI-powered chat assistant interface.
    """
    st.markdown('<p class="main-header">🤖 AI HR Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about your workforce in natural language</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check for API key
    if not (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')):
        st.error("⚠️ Gemini API Key not configured. Please add GEMINI_API_KEY to your .env file.")
        st.info("Get your FREE API key from: https://aistudio.google.com/app/apikey (100% FREE!)")
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show SQL query and results if available
            if message["role"] == "assistant" and "sql_query" in message and message["sql_query"]:
                with st.expander("🔍 View SQL Query & Results"):
                    st.code(message["sql_query"], language="sql")
                    if message.get("results"):
                        st.json(message["results"][:5])  # Show first 5 results
    
    # Handle selected question from sidebar
    if 'selected_question' in st.session_state:
        user_question = st.session_state.selected_question
        del st.session_state.selected_question
        process_question(user_question)
    
    # Chat input
    user_question = st.chat_input("Ask a question about your HR data...")
    
    if user_question:
        process_question(user_question)


def process_question(user_question):
    """
    Processes a user question through the AI assistant.
    
    Args:
        user_question (str): The user's question
    """
    # Add user message to chat
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_question
    })
    
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = answer_hr_question(user_question)
            
            if response['status'] == 'success':
                st.markdown(response['answer'])
                
                # Show SQL query and results in expander
                with st.expander("🔍 View SQL Query & Results"):
                    st.code(response['sql_query'], language="sql")
                    if response['results']:
                        st.json(response['results'][:5])
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response['answer'],
                    "sql_query": response['sql_query'],
                    "results": response['results']
                })
                
                # Increment query count
                st.session_state.query_count += 1
                
            else:
                error_msg = f"❌ {response['answer']}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })
    
    # Rerun to update chat display
    st.rerun()


def render_advanced_analytics():
    """
    Renders advanced analytics with interactive visualizations.
    """
    st.markdown('<p class="main-header">� Advanced Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Deep dive into workforce trends and patterns</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Get data
    all_employees = get_all_employees()
    df_employees = pd.DataFrame([dict(row) for row in all_employees])
    df_employees['hire_date'] = pd.to_datetime(df_employees['hire_date'])
    df_employees['tenure_years'] = (datetime.now() - df_employees['hire_date']).dt.days / 365.25
    
    # Interactive filters
    st.subheader("🎛️ Filter Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_depts = st.multiselect(
            "Select Departments",
            options=df_employees['department'].unique(),
            default=df_employees['department'].unique()
        )
    
    with col2:
        salary_range = st.slider(
            "Salary Range ($)",
            min_value=int(df_employees['salary'].min()),
            max_value=int(df_employees['salary'].max()),
            value=(int(df_employees['salary'].min()), int(df_employees['salary'].max())),
            step=5000
        )
    
    with col3:
        tenure_range = st.slider(
            "Tenure Range (years)",
            min_value=0.0,
            max_value=float(df_employees['tenure_years'].max()),
            value=(0.0, float(df_employees['tenure_years'].max())),
            step=0.5
        )
    
    # Apply filters
    filtered_df = df_employees[
        (df_employees['department'].isin(selected_depts)) &
        (df_employees['salary'] >= salary_range[0]) &
        (df_employees['salary'] <= salary_range[1]) &
        (df_employees['tenure_years'] >= tenure_range[0]) &
        (df_employees['tenure_years'] <= tenure_range[1])
    ]
    
    st.info(f"📊 Showing {len(filtered_df)} of {len(df_employees)} employees")
    st.markdown("---")
    
    # Row 1: 3D Scatter and Bubble Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 3D Department Analysis")
        fig_3d = px.scatter_3d(
            filtered_df,
            x='tenure_years',
            y='salary',
            z='employee_id',
            color='department',
            size='salary',
            hover_data=['first_name', 'last_name', 'position'],
            title='',
            labels={
                'tenure_years': 'Tenure (years)',
                'salary': 'Salary ($)',
                'employee_id': 'Employee Index'
            },
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_3d.update_traces(
            hovertemplate='<b>%{customdata[0]} %{customdata[1]}</b><br>' +
                         'Position: %{customdata[2]}<br>' +
                         'Tenure: %{x:.1f} years<br>' +
                         'Salary: $%{y:,.0f}<extra></extra>'
        )
        fig_3d.update_layout(
            height=500,
            scene=dict(
                bgcolor='white',
                xaxis=dict(backgroundcolor='white', gridcolor='#e5e7eb'),
                yaxis=dict(backgroundcolor='white', gridcolor='#e5e7eb'),
                zaxis=dict(backgroundcolor='white', gridcolor='#e5e7eb')
            ),
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_3d, use_container_width=True)
    
    with col2:
        st.subheader("💎 Position Salary Ranges")
        # Group by position and department
        position_stats = filtered_df.groupby(['department', 'position']).agg({
            'salary': ['mean', 'min', 'max', 'count']
        }).reset_index()
        position_stats.columns = ['department', 'position', 'avg_salary', 'min_salary', 'max_salary', 'count']
        position_stats = position_stats.sort_values('avg_salary', ascending=False).head(15)
        
        fig_bubble = px.scatter(
            position_stats,
            x='avg_salary',
            y='position',
            size='count',
            color='department',
            title='',
            labels={
                'avg_salary': 'Average Salary ($)',
                'position': 'Position',
                'count': 'Employees'
            },
            size_max=40,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bubble.update_traces(
            hovertemplate='<b>%{y}</b><br>' +
                         'Department: %{marker.color}<br>' +
                         'Avg Salary: $%{x:,.0f}<br>' +
                         'Employees: %{marker.size}<extra></extra>'
        )
        fig_bubble.update_layout(
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            ),
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2: Heatmap and Violin Plot
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Salary Heatmap by Department & Tenure")
        # Create tenure bins
        filtered_df['tenure_bin'] = pd.cut(
            filtered_df['tenure_years'],
            bins=[0, 2, 5, 10, float('inf')],
            labels=['0-2 yrs', '2-5 yrs', '5-10 yrs', '10+ yrs']
        )
        
        # Create pivot table
        heatmap_data = filtered_df.pivot_table(
            values='salary',
            index='department',
            columns='tenure_bin',
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(
            heatmap_data,
            title='',
            labels=dict(x="Tenure Range", y="Department", color="Avg Salary ($)"),
            color_continuous_scale='RdYlGn',
            aspect="auto",
            text_auto='.0f'
        )
        fig_heatmap.update_traces(
            hovertemplate='Department: %{y}<br>Tenure: %{x}<br>Avg Salary: $%{z:,.0f}<extra></extra>'
        )
        fig_heatmap.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        st.subheader("🎻 Salary Distribution by Department")
        fig_violin = px.violin(
            filtered_df,
            y='department',
            x='salary',
            color='department',
            title='',
            box=True,
            points='all',
            labels={'salary': 'Salary ($)', 'department': 'Department'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_violin.update_traces(
            hovertemplate='<b>%{y}</b><br>Salary: $%{x:,.0f}<extra></extra>'
        )
        fig_violin.update_layout(
            showlegend=False,
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_violin, use_container_width=True)
    
    st.markdown("---")
    
    # Row 3: Histogram and Box Plot
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Tenure Distribution Histogram")
        fig_hist = px.histogram(
            filtered_df,
            x='tenure_years',
            nbins=20,
            title='',
            labels={'tenure_years': 'Tenure (years)', 'count': 'Number of Employees'},
            color_discrete_sequence=['#667eea'],
            marginal='box'
        )
        fig_hist.update_traces(
            hovertemplate='Tenure: %{x:.1f} years<br>Employees: %{y}<extra></extra>'
        )
        fig_hist.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            ),
            bargap=0.1
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("📦 Salary Box Plot by Department")
        fig_box = px.box(
            filtered_df,
            x='department',
            y='salary',
            color='department',
            title='',
            labels={'salary': 'Salary ($)', 'department': 'Department'},
            color_discrete_sequence=px.colors.qualitative.Safe,
            points='all'
        )
        fig_box.update_traces(
            hovertemplate='<b>%{x}</b><br>Salary: $%{y:,.0f}<extra></extra>'
        )
        fig_box.update_layout(
            showlegend=False,
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1f2937', size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#1f2937"
            )
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    st.markdown("---")
    
    # Statistical Summary
    st.subheader("📋 Statistical Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Salary Statistics**")
        st.metric("Mean", f"${filtered_df['salary'].mean():,.0f}")
        st.metric("Median", f"${filtered_df['salary'].median():,.0f}")
        st.metric("Std Dev", f"${filtered_df['salary'].std():,.0f}")
    
    with col2:
        st.markdown("**Tenure Statistics**")
        st.metric("Mean Tenure", f"{filtered_df['tenure_years'].mean():.1f} years")
        st.metric("Median Tenure", f"{filtered_df['tenure_years'].median():.1f} years")
        st.metric("Max Tenure", f"{filtered_df['tenure_years'].max():.1f} years")
    
    with col3:
        st.markdown("**Department Distribution**")
        top_dept = filtered_df['department'].value_counts().index[0]
        st.metric("Largest Department", top_dept)
        st.metric("Employees", filtered_df['department'].value_counts().iloc[0])
        st.metric("Departments", filtered_df['department'].nunique())


def render_data_explorer():
    """
    Renders the data explorer view with searchable tables.
    """
    st.markdown('<p class="main-header">📋 Data Explorer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Browse and explore your HR data</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Tabs for different data views
    tab1, tab2, tab3 = st.tabs(["👥 Employees", "🔄 Transfers", "⭐ Feedback"])
    
    with tab1:
        st.subheader("Employee Directory")
        employees = get_all_employees()
        df_employees = pd.DataFrame([dict(row) for row in employees])
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            dept_filter = st.multiselect(
                "Filter by Department",
                options=df_employees['department'].unique(),
                default=None
            )
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=df_employees['status'].unique(),
                default=['Active']
            )
        with col3:
            search = st.text_input("Search by name")
        
        # Apply filters
        filtered_df = df_employees.copy()
        if dept_filter:
            filtered_df = filtered_df[filtered_df['department'].isin(dept_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if search:
            filtered_df = filtered_df[
                filtered_df['first_name'].str.contains(search, case=False) |
                filtered_df['last_name'].str.contains(search, case=False)
            ]
        
        st.dataframe(
            filtered_df[['employee_id', 'first_name', 'last_name', 'department', 'position', 'hire_date', 'salary', 'status']],
            use_container_width=True,
            height=400
        )
        st.caption(f"Showing {len(filtered_df)} of {len(df_employees)} employees")
    
    with tab2:
        st.subheader("Transfer History")
        transfers = get_recent_transfers(50)
        df_transfers = pd.DataFrame([dict(row) for row in transfers])
        
        st.dataframe(
            df_transfers,
            use_container_width=True,
            height=400
        )
        st.caption(f"Showing {len(df_transfers)} recent transfers")
    
    with tab3:
        st.subheader("Feedback Overview")
        feedback_summary = get_feedback_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Feedback", feedback_summary['total_feedback'])
        with col2:
            st.metric("Average Rating", f"{feedback_summary['avg_rating']}⭐")
        with col3:
            st.metric("Positive (4+)", feedback_summary['positive_feedback'])
        
        st.info("💡 Use the AI Assistant to query specific feedback data")


def main():
    """
    Main application entry point.
    """
    # Initialize application
    initialize_app()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "📊 Dashboard":
        render_dashboard()
    elif page == "🔬 Advanced Analytics":
        render_advanced_analytics()
    elif page == "🤖 AI Assistant":
        render_ai_assistant()
    elif page == "📋 Data Explorer":
        render_data_explorer()


if __name__ == "__main__":
    main()
