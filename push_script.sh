#!/bin/bash
set -e
TOKEN=$(grep 'GITHUB_TOKEN' /home/samue/hermes-free/.env | cut -d'=' -f2)
cd /home/samue/hermes-free/hermes-config-tracker
git remote set-url origin https://$TOKEN@github.com/samue/hermes-config-tracker.git
git push -u origin main
