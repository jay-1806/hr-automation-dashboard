# HR Automation Dashboard 👥

An intelligent HR automation dashboard built with **Streamlit, SQLite, and Google Gemini AI**. This application enables HR teams to query employee data using natural language and visualize workforce analytics with 10+ interactive chart types.

🚀 **[Live Demo](https://7n7vfknydcbrhy7nwb6hl8.streamlit.app/)** | 💡 **100% FREE to run** - No credit card required! 

## 📸 Dashboard Preview
<img width="1500" height="736" alt="HR Dashboard" src="https://github.com/user-attachments/assets/831bc542-dd53-42ac-b908-68a608d6cf0e" />

## Features ✨

### 1. Interactive Dashboard 📊
- Real-time workforce metrics (total employees, average salary, feedback ratings)
- Visual analytics with interactive charts (department distribution, salary analysis)
- Employee transfer tracking
- Simulated time-saving metrics showing automation impact

### 2. AI-Powered Assistant 🤖
- Natural language query interface powered by Google Gemini 2.0 Flash
- Automatic SQL query generation from plain English questions
- Intelligent response formatting
- Query history tracking
- Sample questions for quick access

### 3. Advanced Analytics 🔬
- Interactive filters (department, salary range, tenure)
- 3D visualizations and scatter plots
- Heatmaps showing salary trends
- Violin and box plots for distribution analysis
- Statistical summaries and insights

### 4. Data Explorer 📋
- Searchable employee directory with filters
- Transfer history viewer
- Feedback overview with statistics
- Export-ready data tables

## Technology Stack 🛠️

- **Frontend**: Streamlit
- **Database**: SQLite
- **AI/ML**: Google Gemini 2.0 Flash 
- **Visualization**: Plotly
- **Data Processing**: Pandas

## Project Structure 📁

```
hr-automation-dashboard/
├── app.py                  # Main Streamlit application
├── db_utils.py            # Database utilities and queries
├── ai_utils.py            # Google Gemini AI integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── hr_peopleops.db       # SQLite database (auto-generated)
```

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (100% FREE at https://aistudio.google.com/app/apikey)

### Setup Steps

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure API key**
   - Copy `.env.example` to `.env`
   - Get your FREE Gemini API key from https://aistudio.google.com/app/apikey
   - Add your Gemini API key to `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```
   - **100% FREE** with generous rate limits, no credit card required!

5. **Run the application**
```powershell
python -m streamlit run app.py
```


### Step 1: Push to GitHub
```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: HR Automation Dashboard"

# Create repository on GitHub (https://github.com/new)
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/hr-automation-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your repository: `YOUR_USERNAME/hr-automation-dashboard`
5. Set main file path: `app.py`
6. Click "Advanced settings" and add secrets:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
7. Click "Deploy"!

Your app will be live at: `https://YOUR_USERNAME-hr-automation-dashboard.streamlit.app`

## Usage Guide 📖

### Dashboard View
- View real-time metrics about your workforce
- Explore interactive visualizations
- Track recent employee transfers
- Monitor automation time savings

### AI Assistant
Ask questions in natural language, such as:
- "How many employees are in Engineering?"
- "What is the average salary by department?"
- "Show me recent employee transfers"
- "Who are the top 5 highest paid employees?"
- "What's the average feedback rating?"

The AI will:
1. Convert your question to SQL
2. Execute the query
3. Format results in natural language
4. Show the SQL query used (expandable)

### Data Explorer
- Browse all employees with search and filters
- View complete transfer history
- Analyze feedback trends
- Export data as needed

## Database Schema 🗄️

### Employees Table
- `employee_id`: Unique identifier (EMP####)
- `first_name`, `last_name`: Employee name
- `email`: Contact email
- `department`: Engineering, Sales, Marketing, HR, Finance, Operations
- `position`: Job title
- `hire_date`: Date of hiring
- `salary`: Annual salary
- `status`: Active or On Leave

### Transfers Table
- `employee_id`: Reference to employee
- `from_department`, `to_department`: Transfer details
- `transfer_date`: Date of transfer
- `reason`: Transfer reason

## Performance Notes ⚡

- Database uses SQLite (sufficient for demo/small teams)
- For production with >1000 employees, consider PostgreSQL
- AI responses typically take 2-5 seconds
- Dashboard renders in <1 second with sample data

## Future Enhancements 🚀

Potential additions:
- User authentication and role-based access
- Email notifications for transfers
- Advanced analytics (predictive attrition)
- Integration with HRIS systems
- Export reports to PDF
- Multi-language support

## License 📄

This project is provided as-is for educational and commercial use.

## Support 💬

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Verify API key configuration

## Credits 🙏

Built with:
- [Streamlit](https://streamlit.io) for the UI framework
- [Google Gemini 2.0 Flash](https://ai.google.dev) for AI capabilities (100% FREE!)
- [Plotly](https://plotly.com) for interactive visualizations
- [SQLite](https://www.sqlite.org) for data storage

---

**Version**: 1.0.0  
**Last Updated**: 1 November 2025  
**Author**: Jay Vithlani
