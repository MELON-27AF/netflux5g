#!/bin/bash

# NetFlux5G Launcher Script
# Run this script to start the NetFlux5G application

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set the Python path to include the project directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Launch the application
python3 "$SCRIPT_DIR/src/main.py"