param([switch]$Deploy)

$GREEN = "Green"; $YELLOW = "Yellow"; $CYAN = "Cyan"

Write-Host "`n===== FreightGPT UAE - One-Click Run =====`n" -ForegroundColor $CYAN

# Step 1: Check Ollama
Write-Host "[1/4] Checking Ollama (qwen model)..." -ForegroundColor $YELLOW
try {
    $models = ollama list 2>$null
    if ($LASTEXITCODE -eq 0 -and $models -match "qwen") {
        Write-Host "  -> qwen model ready" -ForegroundColor $GREEN
    } else {
        Write-Host "  -> qwen not found. AI uses fallback." -ForegroundColor $YELLOW
    }
} catch {
    Write-Host "  -> Ollama not running. Fallback mode." -ForegroundColor $YELLOW
}

# Step 2: Install Python deps
Write-Host "[2/4] Installing Python packages..." -ForegroundColor $YELLOW
pip install -r backend/requirements.txt 2>$null
Write-Host "  -> Done" -ForegroundColor $GREEN

# Step 3: Create directories
New-Item -ItemType Directory -Path "backend/uploads" -Force | Out-Null
Write-Host "[3/4] Directories created" -ForegroundColor $GREEN

# Step 4: Start server
Write-Host "[4/4] Starting FreightGPT API..." -ForegroundColor $GREEN
Write-Host "`n  API Docs: http://localhost:8000/docs" -ForegroundColor $CYAN
Write-Host "  Health:   http://localhost:8000/health" -ForegroundColor $CYAN
Write-Host "  Setup:    http://localhost:8000/setup`n" -ForegroundColor $CYAN

cd backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Deploy to GitHub (optional)
if ($Deploy) {
    Write-Host "`nDeploying to GitHub..." -ForegroundColor $YELLOW
    git init
    git add .
    git commit -m "Initial commit: FreightGPT UAE"
    git remote add origin https://github.com/YOUR_USER/freightgpt-uae.git
    git push -u origin main
    Write-Host "-> Deployed!" -ForegroundColor $GREEN
}
