#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI backend server
echo "Starting FastAPI backend server on port 8000..."
python task_api.py &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 3

# Start the Streamlit frontend
echo "Starting Streamlit frontend on port 8501..."
streamlit run main.py &
FRONTEND_PID=$!

# Function to cleanup processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Both servers are running!"
echo "API Server: http://localhost:8000"
echo "Streamlit UI: http://localhost:8501"
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
