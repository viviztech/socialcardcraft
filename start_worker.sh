#!/bin/bash
set -e
cd ~/projects/socialcardcraft
source venv/bin/activate
export $(grep -v '^#' .env | xargs)
celery -A worker.celery_app worker --loglevel=info --concurrency=2
