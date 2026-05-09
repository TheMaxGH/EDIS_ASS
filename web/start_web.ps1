# EDIS Control Center - PowerShell Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EDIS Control Center - Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[1/4] Checking Node.js..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js is not installed!" -ForegroundColor Red
    Write-Host "Download from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$nodeVersion = node --version
Write-Host "Node.js installed: $nodeVersion" -ForegroundColor Green

# Navigate to frontend directory
Write-Host "[2/4] Navigating to frontend directory..." -ForegroundColor Yellow
Set-Location -Path "frontend"

# Check for node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "[3/4] Installing dependencies (this may take a while)..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies!" -ForegroundColor Red
        Set-Location -Path ".."
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "[3/4] Dependencies already installed" -ForegroundColor Green
}

# Check .env.local
if (-not (Test-Path ".env.local")) {
    Write-Host "[4/4] Creating .env.local from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env.local"
    Write-Host ""
    Write-Host "[IMPORTANT] Edit frontend\.env.local" -ForegroundColor Red
    Write-Host "Set your server IP and API key!" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to continue"
} else {
    Write-Host "[4/4] Configuration found" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EDIS Control Center is starting!" -ForegroundColor Green
Write-Host "Open browser: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start dev server
npm run dev
