#!/bin/bash

set -e

echo "=================================================="
echo "Security Hardening Automation"
echo "=================================================="
echo ""

# Check for Python 3
echo "[1/4] Checking Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  ✓ Found: Python $PYTHON_VERSION at $(which python3)"
else
    echo "  ✗ Python 3 not found"
    echo "  Please install Python 3.8 or higher"
    exit 1
fi

# Check for pip
echo "[2/4] Checking pip..."
if python3 -m pip --version &> /dev/null; then
    PIP_VERSION=$(python3 -m pip --version | awk '{print $2}')
    echo "  ✓ Found: pip $PIP_VERSION"
else
    echo "  ✗ pip not found"
    echo "  Please install pip: sudo apt-get install python3-pip (Ubuntu) or sudo yum install python3-pip (RHEL)"
    exit 1
fi

# Check for venv
echo "[3/4] Checking venv module..."
if python3 -c "import venv" &> /dev/null; then
    echo "  ✓ Found: venv module available"
else
    echo "  ✗ venv module not found"
    echo "  Please install: sudo apt-get install python3-venv (Ubuntu)"
    exit 1
fi

# Check for Ansible (will be installed in venv if not present)
echo "[4/4] Checking Ansible..."
if [ -f "venv/bin/ansible-playbook" ]; then
    ANSIBLE_VERSION=$(venv/bin/ansible-playbook --version | head -1 | awk '{print $2}')
    echo "  ✓ Found: Ansible $ANSIBLE_VERSION in venv"
elif command -v ansible-playbook &> /dev/null; then
    ANSIBLE_VERSION=$(ansible-playbook --version | head -1 | awk '{print $2}')
    echo "  ✓ Found: Ansible $ANSIBLE_VERSION (system-wide)"
else
    echo "  ⚠ Ansible not found - will be installed in venv"
fi

echo ""
echo "All dependencies satisfied!"
echo "=================================================="
echo ""

# Pass all arguments to Python script
python3 harden.py "$@"
