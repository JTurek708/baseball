#!/bin/bash
# Starts both Fantasy Hub servers in separate Terminal windows, opens the browser.

# Figure out where this script lives — that's the project root.
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR' && source venv/bin/activate && uvicorn backend.main:app --reload --port 8000"
    do script "cd '$PROJECT_DIR/frontend' && npm run dev"
end tell
EOF

# Give the servers a moment to boot, then open the browser
sleep 4
open http://localhost:5173