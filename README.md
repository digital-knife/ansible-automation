# Security Hardening Automation

Automated Linux security baseline configuration with CIS compliance validation.

## Features

- Multi-platform: RHEL/CentOS/Amazon Linux, Ubuntu/Debian
- SSH hardening and firewall configuration
- Standalone or Jenkins pipeline execution
- Automated validation with HTML reports
- Flexible targeting: single host, inventory file, or AWS dynamic discovery

## Quick Start
```bash
git clone https://github.com/digital-knife/security-hardening.git
cd security-hardening
./setup.sh

# Harden a target
./harden.sh --target 10.0.1.50 --validate

# Use inventory file
./harden.sh --inventory ansible/inventory/production.ini --validate
```

## Project Structure
```
ansible/
├── playbooks/main.yml          # Main hardening playbook
├── roles/
│   ├── ssh-hardening/          # SSH CIS controls
│   └── firewall/               # Firewall rules
└── inventory/                  # Target definitions

scripts/
├── validate.py                 # Compliance checks
└── report.py                   # HTML report generator

tests/docker-compose.yml        # Local test environment
harden.py                       # Main orchestration
Jenkinsfile                     # CI/CD pipeline
```

## Hardening Controls

**SSH:** Disable root login, disable password auth, limit retries, configure timeouts

**Firewall:** Default deny, allow SSH/HTTP/HTTPS

## Testing Locally
```bash
cd tests && docker-compose up -d
./harden.sh --inventory ansible/inventory/docker.ini --validate
firefox reports/validation-report.html
```

## Jenkins Pipeline

1. Create Pipeline job pointing to this repo
2. Add SSH credential with ID `docker-ssh-key`
3. Build with parameters (target mode, inventory path)

## Configuration

Customize defaults in `ansible/roles/*/defaults/main.yml`
