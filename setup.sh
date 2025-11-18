#!/bin/bash

set -e

echo "Setting up Python virtual environment..."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating venv..."
    python3 -m venv venv
    echo "  ✓ venv created"
else
    echo "  ✓ venv already exists"
fi

# Activate and install requirements
echo "  Installing requirements..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo "Ansible version: $(venv/bin/ansible-playbook --version | head -1 | grep -oP '\d+\.\d+\.\d+')"
echo ""
echo "To activate manually: source venv/bin/activate"
