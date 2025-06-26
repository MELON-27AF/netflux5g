# NetFlux5G - 5G Core Connectivity Test PowerShell Script
# Run this script to test end-to-end UE connectivity

Write-Host "NetFlux5G - 5G Core End-to-End Connectivity Test" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    $dockerStatus = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker is not available. Please ensure Docker Desktop is installed and running." -ForegroundColor Red
    exit 1
}

# Check if Python is available
Write-Host "Checking Python availability..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python is available: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python is not available. Please install Python 3.8+ and try again." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python is not available. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Install Python dependencies if needed
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Some dependencies may have failed to install" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Error installing dependencies" -ForegroundColor Yellow
}

# Run the connectivity test
Write-Host "`nStarting 5G core network connectivity test..." -ForegroundColor Yellow
Write-Host "This may take several minutes to complete..." -ForegroundColor Yellow

try {
    python test_5g_connectivity.py
    $testResult = $LASTEXITCODE
    
    if ($testResult -eq 0) {
        Write-Host "`n🎉 SUCCESS! 5G core network is working correctly." -ForegroundColor Green
        Write-Host "UE can now ping external networks end-to-end through the 5G core." -ForegroundColor Green
    } else {
        Write-Host "`n❌ FAILED! 5G core network test failed." -ForegroundColor Red
        Write-Host "Please check the error messages above and fix any issues." -ForegroundColor Red
    }
} catch {
    Write-Host "`n❌ Error running connectivity test: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nTest completed. Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
