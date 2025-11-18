# Security Hardening Automation

Automated security baseline hardening for Linux systems using Ansible.

## Features
- CIS & STIG compliance baselines
- Multi-platform support (Amazon Linux, RHEL, Ubuntu)
- Standalone or Jenkins pipeline execution
- Validation & compliance reporting

## Quick Start

### Standalone
```bash
./harden.sh --inventory ansible/inventory/local.ini
```

### With validation
```bash
./harden.sh --target 10.0.1.50 --validate
```

## Requirements
- Python 3.8+
- Ansible 2.9+
- SSH access to target systems
