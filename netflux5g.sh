#!/bin/bash

# NetFlux5G Launcher Script
# Run this script to start the NetFlux5G application

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the Python path to include the project directory
export PYTHONPATH="$SCRIPT_DIR/src:$SCRIPT_DIR:$PYTHONPATH"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
python3 -c "import PyQt5" 2>/dev/null || {
    echo "PyQt5 is not installed. Please install it with: pip install PyQt5"
    exit 1
}

# Launch the application
cd "$SCRIPT_DIR"
python3 src/main.py "$@"