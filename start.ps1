# Quick Start Script for HR Automation Dashboard

Write-Host "🚀 Starting HR Automation Dashboard..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠ Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    Write-Host "✓ Installing dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "⚠ WARNING: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host "You can copy .env.example and add your API key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Get FREE API key at: https://aistudio.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

# Start Streamlit
Write-Host ""
Write-Host "🎉 Launching dashboard..." -ForegroundColor Green
Write-Host "   URL will open in your browser automatically" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

streamlit run app.py
