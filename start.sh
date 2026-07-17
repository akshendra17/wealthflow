#!/bin/bash

# WealthFlow Startup Script
# This script starts both the FastAPI backend and the Vite+React frontend simultaneously.
# Pressing Ctrl+C will gracefully shut down both servers.

echo "========================================="
echo "        🚀 Starting WealthFlow 🚀        "
echo "========================================="

# Start Backend
echo "Starting Backend (FastAPI on port 8000)..."
(cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend (Vite on port 5173)..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

# Trap SIGINT (Ctrl+C) and SIGTERM to kill both background processes
trap "echo -e '\nStopping WealthFlow servers...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" SIGINT SIGTERM EXIT

# Wait for background jobs to finish
wait
