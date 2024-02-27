#!/bin/bash

# cleanup function to call when script ends
# important to shutdown all background processes
cleanup() {
    echo "Cleaning up..."
    kill 0
    echo "Shutdown complete."
}
trap cleanup SIGINT SIGTERM

echo "Starting API..."
python answering-model/model_api.py & # run in background

echo "Starting Streamlit App..."
streamlit run ui/app.py & # run in background

wait
# cleanup
cleanup
