#!/bin/bash

# NetFlux5G Safe Launcher Script
# This script provides better error handling and preparation steps

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 NetFlux5G Safe Launcher${NC}"
echo "=========================="

# Set the Python path to include the project directory
export PYTHONPATH="$SCRIPT_DIR/src:$SCRIPT_DIR:$PYTHONPATH"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python 3 is available
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $PYTHON_VERSION"

# Check if Docker is available
if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    echo "Please install Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✅ Docker found${NC}"

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✅ Docker daemon is running${NC}"

# Check if required Python packages are installed
echo "Checking Python dependencies..."

MISSING_PACKAGES=()

python3 -c "import PyQt5" 2>/dev/null || MISSING_PACKAGES+=("PyQt5")
python3 -c "import docker" 2>/dev/null || MISSING_PACKAGES+=("docker")
python3 -c "import yaml" 2>/dev/null || MISSING_PACKAGES+=("PyYAML")
python3 -c "import psutil" 2>/dev/null || MISSING_PACKAGES+=("psutil")

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing Python packages: ${MISSING_PACKAGES[*]}${NC}"
    echo "Installing missing packages..."
    
    # Try to install missing packages
    if pip3 install "${MISSING_PACKAGES[@]}" --user; then
        echo -e "${GREEN}✅ Packages installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install packages${NC}"
        echo "Please install manually with: pip3 install ${MISSING_PACKAGES[*]}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ All required packages are installed${NC}"
fi

# Check system resources
echo "Checking system resources..."

# Check available memory
AVAILABLE_MEMORY=$(python3 -c "import psutil; print(int(psutil.virtual_memory().available / (1024**3)))" 2>/dev/null || echo "unknown")
if [ "$AVAILABLE_MEMORY" != "unknown" ] && [ "$AVAILABLE_MEMORY" -lt 2 ]; then
    echo -e "${YELLOW}⚠️ Warning: Low available memory (${AVAILABLE_MEMORY}GB). Consider closing other applications.${NC}"
elif [ "$AVAILABLE_MEMORY" != "unknown" ]; then
    echo -e "${GREEN}✅ Available memory: ${AVAILABLE_MEMORY}GB${NC}"
fi

# Check disk space
AVAILABLE_DISK=$(python3 -c "import shutil; print(int(shutil.disk_usage('.').free / (1024**3)))" 2>/dev/null || echo "unknown")
if [ "$AVAILABLE_DISK" != "unknown" ] && [ "$AVAILABLE_DISK" -lt 5 ]; then
    echo -e "${YELLOW}⚠️ Warning: Low disk space (${AVAILABLE_DISK}GB). Docker images require ~2-3GB.${NC}"
elif [ "$AVAILABLE_DISK" != "unknown" ]; then
    echo -e "${GREEN}✅ Available disk space: ${AVAILABLE_DISK}GB${NC}"
fi

# Ask user if they want to pre-pull Docker images
echo ""
echo -e "${BLUE}Docker Image Preparation${NC}"
echo "NetFlux5G requires several Docker images (~800MB total download)"
echo "You can:"
echo "1. Pre-pull images now (recommended for first run)"
echo "2. Skip and let NetFlux5G pull them as needed"
echo "3. Run system check first"

read -p "Choose option [1/2/3]: " choice

case $choice in
    1)
        echo "Running environment preparation..."
        if python3 prepare_environment.py; then
            echo -e "${GREEN}✅ Environment preparation completed${NC}"
        else
            echo -e "${YELLOW}⚠️ Environment preparation had issues, but continuing...${NC}"
        fi
        ;;
    2)
        echo "Skipping image pre-pull"
        ;;
    3)
        echo "Running system check..."
        python3 check_system.py
        echo ""
        read -p "Press Enter to continue or Ctrl+C to exit..."
        ;;
    *)
        echo "Invalid choice, continuing without pre-pull"
        ;;
esac

# Change to script directory
cd "$SCRIPT_DIR"

echo ""
echo -e "${BLUE}🎯 Starting NetFlux5G...${NC}"
echo "Press Ctrl+C to stop the application"
echo ""

# Set up signal handlers
trap 'echo -e "\n${YELLOW}⚠️ NetFlux5G interrupted${NC}"; exit 130' INT
trap 'echo -e "\n${RED}❌ NetFlux5G terminated${NC}"; exit 143' TERM

# Launch the application with better error handling
if python3 src/main.py "$@"; then
    echo -e "${GREEN}✅ NetFlux5G exited normally${NC}"
else
    EXIT_CODE=$?
    echo -e "${RED}❌ NetFlux5G exited with error code $EXIT_CODE${NC}"
    
    # Provide helpful error messages based on exit code
    case $EXIT_CODE in
        130)
            echo "Application was interrupted by user (Ctrl+C)"
            ;;
        137)
            echo "Application was killed (possibly out of memory)"
            echo "Try closing other applications and running again"
            ;;
        *)
            echo "Check the netflux5g.log file for more details"
            ;;
    esac
    
    exit $EXIT_CODE
fi
