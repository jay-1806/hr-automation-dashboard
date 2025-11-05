# HR Automation Dashboard 👥

An intelligent HR automation dashboard built with Streamlit, SQLite, and Google Gemini AI. This application enables HR teams to query employee data using natural language and visualize workforce analytics in real-time.

🚀 **[Live Demo](https://your-app-name.streamlit.app)** | 📖 [Documentation](#usage-guide)

![Dashboard Preview](https://via.placeholder.com/800x400?text=Add+Your+Screenshot+Here)

> 💡 **100% FREE to run** - Uses Google Gemini API (free tier with generous limits, no credit card required!)

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
- **100% FREE** with generous rate limits (no credit card required!)

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
- **AI/ML**: Google Gemini 2.0 Flash (100% FREE, no credit card!)
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

The application will automatically:
- Create the SQLite database
- Generate 50 dummy employee records
- Populate transfer and feedback data
- Open in your default browser

## Deploy to Streamlit Community Cloud (100% FREE!) ☁️

**No credit card required. Forever free hosting!**

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

**That's it! 🎉 Your app is now live and accessible to anyone!**

### Alternative: Deploy to Hugging Face Spaces (Also FREE!)
1. Create account at [huggingface.co](https://huggingface.co)
2. Create new Space with Streamlit template
3. Upload your files
4. Add `GEMINI_API_KEY` in Settings → Repository secrets
5. Your app will be live at: `https://huggingface.co/spaces/YOUR_USERNAME/hr-dashboard`

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

### Feedback Table
- `employee_id`: Reference to employee
- `feedback_date`: Date of feedback
- `rating`: 1-5 star rating
- `feedback_type`: Type of feedback
- `comments`: Feedback text
- `reviewer`: Who provided the feedback

## Key Features Explained 🔍

### Modular Code Architecture
- **db_utils.py**: All database operations isolated for easy testing
- **ai_utils.py**: LangChain integration separated from UI logic
- **app.py**: Clean Streamlit UI with minimal business logic

### Well-Commented Code
Every function includes:
- Docstrings explaining purpose
- Parameter descriptions
- Return value documentation
- Usage examples where helpful

### Production-Ready Features
- Environment variable configuration
- Error handling throughout
- SQL injection protection via parameterized queries
- Efficient database connection management
- Session state management for chat history

### Simulated Metrics
- Time savings calculation (assumes 7.5 min manual vs 0.5 min AI)
- Cost savings based on hourly rates
- Efficiency improvement percentages

## Customization 🎨

### Adding More Departments
Edit `departments` list in `db_utils.py`

### Adjusting Sample Data
Modify `_populate_dummy_data()` function in `db_utils.py`

### Changing AI Model
Update model name in `get_claude_client()` in `ai_utils.py`

### Custom Visualizations
Add new charts in `render_dashboard()` in `app.py` using Plotly

## Troubleshooting 🔧

### "API Key not configured"
- Ensure `.env` file exists in project root
- Verify `GEMINI_API_KEY` is set correctly
- Get FREE key at: https://aistudio.google.com/app/apikey
- Restart the Streamlit app after adding the key

### Database errors
- Delete `hr_peopleops.db` and restart the app
- Database will be recreated automatically

### Import errors
- Verify all packages in `requirements.txt` are installed
- Try: `pip install -r requirements.txt --upgrade`

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
**Last Updated**: November 2025  
**Author**: HR Automation Dashboard Team
