param(
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "freightgpt-uae"
)

$GREEN = "Green"; $YELLOW = "Yellow"; $CYAN = "Cyan"

Write-Host "`n===== FreightGPT UAE - GitHub Deploy =====`n" -ForegroundColor $CYAN

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: git not found. Install git from https://git-scm.com" -ForegroundColor Red
    exit 1
}

# Check gh CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "WARNING: gh CLI not found. Will use manual deploy." -ForegroundColor $YELLOW
    $use_gh = $false
} else {
    $use_gh = $true
}

# Initialize repo
if (-not (Test-Path ".git")) {
    Write-Host "[1/4] Initializing git repository..." -ForegroundColor $YELLOW
    git init
    Write-Host "  -> Done" -ForegroundColor $GREEN
} else {
    Write-Host "[1/4] Git already initialized" -ForegroundColor $GREEN
}

# Add and commit
Write-Host "[2/4] Staging and committing files..." -ForegroundColor $YELLOW
git add -A
$existing = git log --oneline -1
if ($LASTEXITCODE -eq 0) {
    git commit --allow-empty -m "Update FreightGPT UAE"
} else {
    git commit -m "Initial commit: FreightGPT UAE - Autonomous Logistics OS"
}
Write-Host "  -> Done" -ForegroundColor $GREEN

# Create GitHub repo
Write-Host "[3/4] Creating GitHub repository..." -ForegroundColor $YELLOW
if ($use_gh) {
    $existing_repo = gh repo view "$RepoName" --json name 2>$null
    if ($LASTEXITCODE -ne 0) {
        gh repo create "$RepoName" --public --source=. --remote=origin --push
        Write-Host "  -> Created and pushed to GitHub" -ForegroundColor $GREEN
    } else {
        git remote add origin "https://github.com/$((gh api user --jq '.login'))/$RepoName.git" 2>$null
        git push -u origin main 2>$null
        if ($LASTEXITCODE -ne 0) { git push -u origin master }
        Write-Host "  -> Pushed to existing repo" -ForegroundColor $GREEN
    }
} else {
    Write-Host "  Manual deploy. Run these commands:" -ForegroundColor $YELLOW
    Write-Host "`n  1. Create repo at https://github.com/new (name: $RepoName)"
    Write-Host "  2. Run:" -ForegroundColor $CYAN
    Write-Host "     git remote add origin https://github.com/YOUR_USER/$RepoName.git"
    Write-Host "     git push -u origin main`n"
}

# Final steps
Write-Host "[4/4] Verifying..." -ForegroundColor $YELLOW
git status --short
Write-Host "  -> Ready!" -ForegroundColor $GREEN

Write-Host "`n===== Deploy Complete =====" -ForegroundColor $CYAN
Write-Host "  Repo: $RepoName"
Write-Host "  URL:  https://github.com/YOUR_USER/$RepoName" -ForegroundColor $CYAN
Write-Host "`n=== GitHub Pages (Frontend) ===" -ForegroundColor $GREEN
Write-Host "After pushing to GitHub:"
Write-Host "  1. Go to your repo Settings > Pages"
Write-Host "  2. Source: GitHub Actions"
Write-Host "  3. The site will auto-deploy at:" -ForegroundColor $CYAN
Write-Host "     https://YOUR_USER.github.io/$RepoName/" -ForegroundColor $GREEN
Write-Host "`nOr push now and the Actions workflow handles everything."
Write-Host "`nTo deploy to a server, use:" -ForegroundColor $YELLOW
Write-Host "  git clone https://github.com/YOUR_USER/$RepoName.git"
Write-Host "  cd $RepoName"
Write-Host "  .\RUN.ps1`n"
