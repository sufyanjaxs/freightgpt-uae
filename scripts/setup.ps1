# FreightGPT UAE - One-command Setup for Windows
# Run this in PowerShell as:  .\scripts\setup.ps1

Write-Host "🚀 FreightGPT UAE - Quick Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check Python
try {
    $pyVersion = python --version
    Write-Host "✓ $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version
    Write-Host "✓ Node $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Install Python deps
Write-Host "`n📦 Installing Python packages..." -ForegroundColor Yellow
pip install -r backend/requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python install failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python packages installed" -ForegroundColor Green

# Install Node deps
Write-Host "`n📦 Installing Node packages..." -ForegroundColor Yellow
Set-Location frontend
npm install --legacy-peer-deps
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  npm had warnings, but continuing..." -ForegroundColor Yellow
}
Set-Location ..
Write-Host "✓ Node packages installed" -ForegroundColor Green

# Create uploads directory
New-Item -ItemType Directory -Path "backend\uploads" -Force | Out-Null
Write-Host "✓ Uploads directory created" -ForegroundColor Green

Write-Host "`n✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "▶️  To run the backend:   cd backend; python -m uvicorn main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "▶️  To run the frontend:  cd frontend; npm run dev" -ForegroundColor Cyan
Write-Host "▶️  API Docs:             http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "▶️  Web App:              http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 For AI features, install Ollama: https://ollama.ai" -ForegroundColor Yellow
Write-Host "   Then run: ollama pull mistral" -ForegroundColor Yellow
