#!/bin/bash
set -e

echo "=== SocialCardCraft Setup ==="

# System deps
sudo apt update -y
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Create DB
sudo -u postgres psql -c "CREATE USER socialcard_user WITH PASSWORD 'socialcard_pass';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE socialcardcraft_db OWNER socialcard_user;" 2>/dev/null || true

# Virtual env
cd ~/projects/socialcardcraft
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Playwright browsers
playwright install chromium
playwright install-deps chromium

# .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  Edit .env with your real values before starting!"
fi

# Directories
mkdir -p uploads exports static/css static/js static/fonts static/images

echo "=== Setup complete ==="
echo "Next: edit .env, then run: ./start.sh"
