#!/bin/bash

echo "Starting auto-commit script. Press Ctrl+C to stop."
echo "Monitoring directory: $(pwd)"

while true; do
    # Check if there are any changes
    if [[ -n $(git status -s) ]]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Changes detected. Committing..."
        git add .
        git commit -m "Auto-commit by AI workflow at $(date +'%Y-%m-%d %H:%M:%S')"
    fi
    # Wait 5 minutes (300 seconds)
    sleep 300
done
