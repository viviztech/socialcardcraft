#!/bin/bash
# Deploy SocialCardCraft to EC2
set -e

EC2_USER=ubuntu
EC2_IP=13.205.180.69
KEY=~/.ssh/copytrade-key.pem
REMOTE_DIR=/home/ubuntu/projects/socialcardcraft

echo "=== Deploying SocialCardCraft to EC2 ==="

# Ensure remote project dir exists
ssh -i $KEY $EC2_USER@$EC2_IP "mkdir -p $REMOTE_DIR"

# Sync project files (exclude local-only artifacts)
rsync -avz \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'exports' \
  --exclude 'uploads' \
  --exclude '.env' \
  --exclude '.git' \
  ~/projects/socialcardcraft/ \
  -e "ssh -i $KEY" \
  $EC2_USER@$EC2_IP:$REMOTE_DIR/

echo "Files synced."

# Remote bootstrap + restart
ssh -i $KEY $EC2_USER@$EC2_IP << 'REMOTE'
  set -e
  cd ~/projects/socialcardcraft

  # Install system deps if not present
  if ! command -v psql &>/dev/null; then
    echo "Installing system packages..."
    sudo apt update -q
    sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server -q
    sudo systemctl enable postgresql redis-server
    sudo systemctl start postgresql redis-server
  fi

  # Create DB + user if not exists
  sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='socialcard_user'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER socialcard_user WITH PASSWORD 'socialcard_pass';"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='socialcardcraft_db'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE socialcardcraft_db OWNER socialcard_user;"

  # Create venv if missing
  if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
  fi

  source venv/bin/activate

  echo "Installing Python dependencies..."
  pip install --upgrade pip -q
  pip install -r requirements.txt -q

  # Install Playwright Chromium
  echo "Installing Playwright Chromium..."
  playwright install chromium
  playwright install-deps chromium 2>/dev/null || true

  # Create required dirs
  mkdir -p uploads exports static/css static/js static/fonts static/images

  # Create .env if missing
  if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  .env created from example — update AWS keys if needed"
  fi

  # Install systemd services
  sudo cp socialcardcraft.service /etc/systemd/system/
  sudo cp socialcardcraft-worker.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable socialcardcraft socialcardcraft-worker
  sudo systemctl restart socialcardcraft socialcardcraft-worker

  sleep 2
  echo ""
  echo "--- App status ---"
  sudo systemctl status socialcardcraft --no-pager | tail -8
  echo ""
  echo "--- Worker status ---"
  sudo systemctl status socialcardcraft-worker --no-pager | tail -5
REMOTE

echo ""
echo "=== Deploy complete ==="
echo "URL: http://$EC2_IP:8010"
