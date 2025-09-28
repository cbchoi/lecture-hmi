#!/bin/bash

echo "Stopping Vite development server..."

# Find and kill vite processes
VITE_PIDS=$(ps aux | grep -E "(vite|node.*vite)" | grep -v grep | awk '{print $2}')

if [ -n "$VITE_PIDS" ]; then
    echo "Found Vite processes: $VITE_PIDS"
    echo "$VITE_PIDS" | xargs kill -TERM
    sleep 2

    # Force kill if still running
    REMAINING_PIDS=$(ps aux | grep -E "(vite|node.*vite)" | grep -v grep | awk '{print $2}')
    if [ -n "$REMAINING_PIDS" ]; then
        echo "Force killing remaining processes: $REMAINING_PIDS"
        echo "$REMAINING_PIDS" | xargs kill -KILL
    fi

    echo "Development server stopped."
else
    echo "No Vite development server found running."
fi

# Alternative: Kill by port (assuming default vite port 5173)
PORT_PID=$(lsof -ti:5173 2>/dev/null)
if [ -n "$PORT_PID" ]; then
    echo "Killing process on port 5173: $PORT_PID"
    kill -TERM $PORT_PID
fi