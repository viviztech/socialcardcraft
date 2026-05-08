#!/bin/bash
set -e
cd ~/projects/socialcardcraft
source venv/bin/activate

export $(grep -v '^#' .env | xargs)

echo "Starting SocialCardCraft on port $PORT..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8010} --workers 2
