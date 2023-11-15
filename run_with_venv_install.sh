#!/bin/bash

#!!! Run at own risk !!!

# set verbose output
# set -x

# var to define virtual environment directory
VENV_DIR=".venv"

# cleanup function to call when script ends
# important to shutdown all background processes and deaactivate venv
cleanup() {
    echo "Cleaning up..."
    # deactivate
    # Kills all processes started by script
    kill 0
    echo "Shutdown complete."
}

# Trap SIGINT (Ctrl+C) and SIGTERM signals and call cleanup function
# -> https://stackoverflow.com/questions/360201/how-do-i-kill-background-processes-jobs-when-my-shell-script-exits
trap cleanup SIGINT SIGTERM

# check if venv already exists
if [ ! -d "$VENV_DIR" ]; then
    # if not create it
    echo "Creating virtual environment..."
    python -m venv $VENV_DIR
    echo "Virtual environment created."
fi

# make venv executable
chmod +x $VENV_DIR/bin/activate

echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# if activation failed exit script to avoid installing dependencies in wrong environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Failed to activate virtual environment. Exiting..."
    exit 1
fi

echo "Installing dependencies..."
# Install dependencies from requirements.txt
pip install -r requirements.txt

echo "Starting API..."
python api/model_api.py & # run in background

echo "Starting Streamlit App..."
streamlit run ui/app.py & # run in background

wait
# cleanup
cleanup
