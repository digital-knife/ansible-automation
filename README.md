# Security Hardening Automation

Automated security baseline configuration for Linux systems with CIS compliance checks.

## Features

- **Multi-platform support:** RHEL/CentOS/Amazon Linux, Ubuntu/Debian
- **CIS baseline controls:** SSH hardening, firewall configuration
- **Multiple deployment modes:**
  - Standalone execution (bash wrapper)
  - Jenkins CI/CD pipeline
  - Docker test environment
- **Validation & reporting:** Automated compliance scanning with HTML reports
- **Flexible targeting:**
  - Single target (IP/hostname/EC2 instance-id)
  - Static inventory files
  - AWS dynamic inventory (tag-based discovery)

## Prerequisites

- Python 3.9+
- Ansible 2.12+
- SSH access to target systems
- (Optional) Jenkins with Kubernetes plugin
- (Optional) AWS credentials for dynamic inventory

## Quick Start

### Local Execution
```bash
# Clone and setup
git clone https://github.com/digital-knife/security-hardening.git
cd security-hardening
./setup.sh

# Harden a single target
./harden.sh --target 10.0.1.50 --validate

# Use inventory file
./harden.sh --inventory ansible/inventory/production.ini --validate

# Dry run (no changes)
./harden.sh --target 10.0.1.50 --dry-run
```

### Jenkins Pipeline

1. Create new Pipeline job
2. Configure SCM: `https://github.com/digital-knife/security-hardening.git`
3. Set Script Path: `Jenkinsfile`
4. Add SSH key credential: ID `docker-ssh-key`
5. Run with parameters:
   - Target mode: manual/dynamic_aws/static_inventory
   - Inventory path or target IP
   - Enable/disable validation

## Project Structure
```
security-hardening/
├── ansible/
│   ├── playbooks/
│   │   └── main.yml           # Main hardening playbook
│   ├── roles/
│   │   ├── ssh-hardening/     # SSH CIS baseline
│   │   └── firewall/          # UFW/firewalld configuration
│   ├── inventory/             # Target inventories
│   └── requirements.yml       # Ansible collections
├── scripts/
│   ├── validate.py            # Compliance validation
│   └── report.py              # HTML report generation
├── tests/
│   └── docker-compose.yml     # Local test environment
├── harden.py                  # Main orchestration script
├── harden.sh                  # Wrapper with dependency checks
└── Jenkinsfile                # CI/CD pipeline definition
```

## Hardening Controls

### SSH Configuration
- Root login disabled
- Password authentication disabled
- Empty passwords disabled
- X11 forwarding disabled
- Max auth tries: 3
- Client alive interval: 300s

### Firewall
- Default deny incoming
- Allow SSH, HTTP, HTTPS
- Configurable additional ports

## Testing

### Docker Test Environment
```bash
# Start test container
cd tests
docker-compose up -d

# Run hardening
cd ..
./harden.sh --inventory ansible/inventory/docker.ini --validate

## Validation Reports

After hardening, validation generates:
- `reports/validation-report.json` - Machine-readable results
- `reports/validation-report.html` - Human-readable dashboard
- `reports/hardening.log` - Execution logs
