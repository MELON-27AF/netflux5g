# NetFlux5G Production Deployment Script for Windows
# Run this script as Administrator

param(
    [switch]$Force = $false
)

Write-Host "🚀 Starting NetFlux5G Production Deployment..." -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check Docker installation
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create production directory structure
$ProductionPath = "C:\NetFlux5G"
Write-Host "📁 Creating production directory structure..." -ForegroundColor Blue

if (Test-Path $ProductionPath) {
    if (-not $Force) {
        $response = Read-Host "Production directory already exists. Overwrite? (y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Host "Deployment cancelled" -ForegroundColor Yellow
            exit 0
        }
    }
    Remove-Item -Recurse -Force $ProductionPath
}

New-Item -ItemType Directory -Path $ProductionPath -Force | Out-Null
New-Item -ItemType Directory -Path "$ProductionPath\config" -Force | Out-Null
New-Item -ItemType Directory -Path "$ProductionPath\config\open5gs" -Force | Out-Null
New-Item -ItemType Directory -Path "$ProductionPath\config\ueransim" -Force | Out-Null
New-Item -ItemType Directory -Path "$ProductionPath\config\templates" -Force | Out-Null
New-Item -ItemType Directory -Path "$ProductionPath\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$ProductionPath\data" -Force | Out-Null

# Copy application files
Write-Host "📋 Copying application files..." -ForegroundColor Blue
Copy-Item -Recurse -Force "src\*" "$ProductionPath\src\"
Copy-Item -Recurse -Force "config\*" "$ProductionPath\config\"
Copy-Item -Force "requirements.txt" "$ProductionPath\"
Copy-Item -Force "production.cfg" "$ProductionPath\"
Copy-Item -Force "README.md" "$ProductionPath\"
Copy-Item -Force "LICENSE" "$ProductionPath\"

# Create Python virtual environment
Write-Host "🐍 Setting up Python environment..." -ForegroundColor Blue
Set-Location $ProductionPath

try {
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "✅ Python environment created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Python environment: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Pull required Docker images
Write-Host "🐳 Pulling Docker images..." -ForegroundColor Blue
$images = @(
    "openverso/open5gs:latest",
    "openverso/ueransim:latest", 
    "mongo:4.4"
)

foreach ($image in $images) {
    try {
        Write-Host "Pulling $image..." -ForegroundColor Cyan
        docker pull $image
    } catch {
        Write-Host "⚠️ Warning: Failed to pull $image" -ForegroundColor Yellow
    }
}

# Create Windows service wrapper script
$ServiceScript = @"
@echo off
cd /d C:\NetFlux5G
call venv\Scripts\activate.bat
python src\main.py --config production.cfg
"@

$ServiceScript | Out-File -FilePath "$ProductionPath\start_service.bat" -Encoding ASCII

# Create uninstall script
$UninstallScript = @"
# NetFlux5G Uninstall Script
Write-Host "Removing NetFlux5G..." -ForegroundColor Yellow

# Stop any running containers
try {
    docker ps -q --filter "name=netflux" | ForEach-Object { docker stop `$_ }
    docker ps -aq --filter "name=netflux" | ForEach-Object { docker rm `$_ }
} catch {
    Write-Host "No containers to clean up" -ForegroundColor Gray
}

# Remove installation directory
if (Test-Path "C:\NetFlux5G") {
    Remove-Item -Recurse -Force "C:\NetFlux5G"
    Write-Host "✅ NetFlux5G removed successfully" -ForegroundColor Green
} else {
    Write-Host "NetFlux5G directory not found" -ForegroundColor Yellow
}
"@

$UninstallScript | Out-File -FilePath "$ProductionPath\uninstall.ps1" -Encoding UTF8

# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\NetFlux5G.lnk")
$Shortcut.TargetPath = "$ProductionPath\start_service.bat"
$Shortcut.WorkingDirectory = $ProductionPath
$Shortcut.IconLocation = "$ProductionPath\src\assets\icons\logo netflux.png"
$Shortcut.Description = "NetFlux5G 5G Network Simulation Tool"
$Shortcut.Save()

Write-Host ""
Write-Host "✅ NetFlux5G has been deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Management:" -ForegroundColor Cyan
Write-Host "  Installation directory: C:\NetFlux5G" -ForegroundColor White
Write-Host "  Start application:      Run start_service.bat" -ForegroundColor White
Write-Host "  Configuration file:     C:\NetFlux5G\production.cfg" -ForegroundColor White
Write-Host "  Log directory:          C:\NetFlux5G\logs" -ForegroundColor White
Write-Host "  Desktop shortcut:       Created on Public Desktop" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Production Notes:" -ForegroundColor Yellow
Write-Host "  1. Configure Windows Firewall if needed" -ForegroundColor White
Write-Host "  2. Set up backup procedures for configuration" -ForegroundColor White
Write-Host "  3. Monitor system resources during operation" -ForegroundColor White
Write-Host "  4. Update Docker images regularly" -ForegroundColor White
Write-Host ""
Write-Host "🗑️  To uninstall: Run uninstall.ps1 from the installation directory" -ForegroundColor Gray
