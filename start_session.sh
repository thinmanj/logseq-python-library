#!/bin/bash

# Start IPython session with Logseq Python Library
# Usage: ./start_session.sh

echo "🚀 Starting IPython with Logseq Python Library..."
echo "📍 Current directory: $(pwd)"
echo "📁 Virtual environment: .venv"
echo ""

# Activate virtual environment and start IPython
source .venv/bin/activate && ipython -i ipython_startup.py