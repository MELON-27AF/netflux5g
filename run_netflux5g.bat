@echo off
echo NetFlux5G - 5G Network Simulation Tool
echo =====================================

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Checking Docker installation...
docker --version
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not running
    echo Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting NetFlux5G...
cd src
python main.py

pause
