#!/bin/bash
set -e
# Extract token from .env file
TOKEN=$(grep '^GITHUB_TOKEN=*** /home/samue/hermes-free/.env | cut -d'=' -f2)
echo "Token extracted: ${TOKEN:0:4}...${TOKEN: -4}"
# Set remote URL with token
git remote set-url origin https://$TOKEN@github.com/samue/hermes-config-tracker.git
# Push to main
git push -u origin main
