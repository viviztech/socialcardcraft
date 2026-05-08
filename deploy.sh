#!/bin/bash
# Run this on EC2 to deploy SocialCardCraft
set -e

EC2_USER=ubuntu
EC2_IP=13.205.180.69
KEY=~/.ssh/copytrade-key.pem
REMOTE_DIR=/home/ubuntu/projects/socialcardcraft

echo "=== Deploying SocialCardCraft to EC2 ==="

# Sync project files
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude 'exports' --exclude 'uploads' --exclude '.env' \
  ~/projects/socialcardcraft/ \
  -e "ssh -i $KEY" \
  $EC2_USER@$EC2_IP:$REMOTE_DIR/

echo "Files synced."

# Remote commands
ssh -i $KEY $EC2_USER@$EC2_IP << 'REMOTE'
  cd ~/projects/socialcardcraft
  source venv/bin/activate
  pip install -r requirements.txt -q
  playwright install chromium --with-deps 2>/dev/null || true

  sudo cp socialcardcraft.service /etc/systemd/system/
  sudo cp socialcardcraft-worker.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable socialcardcraft socialcardcraft-worker
  sudo systemctl restart socialcardcraft socialcardcraft-worker

  echo "Services restarted."
  sudo systemctl status socialcardcraft --no-pager | tail -5
REMOTE

echo "=== Deploy complete: http://$EC2_IP:8010 ==="
