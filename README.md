# Security Hardening Automation

Automated Linux security baseline configuration with CIS Level 1 compliance controls.

**Note:** This is a demonstration implementation covering key CIS Level 1 controls. Not a complete CIS benchmark implementation.

## Features

- Multi-platform: RHEL/CentOS/Amazon Linux, Ubuntu/Debian
- CIS Level 1 hardening controls (filesystem, network, services, logging, access)
- SSH hardening and firewall configuration
- Standalone or Jenkins pipeline execution
- Automated validation with HTML reports
- Flexible targeting: single host, inventory file, or AWS dynamic discovery
- Granular control: enable/disable individual checks

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
│   ├── cis-filesystem/         # Filesystem hardening
│   ├── cis-network/            # Network kernel parameters
│   ├── cis-services/           # Disable unnecessary services
│   ├── cis-logging/            # Rsyslog/journald configuration
│   ├── cis-access/             # Password policies, account controls
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

**CIS Section 1 - Filesystem:** Disable unused filesystems (cramfs, usb-storage, etc), mount options (noexec, nosuid), permissions
**CIS Section 2 - Services:** Disable unnecessary services (avahi, cups, dhcpd, nfs, samba, etc)
**CIS Section 3 - Network:** Disable IP forwarding, packet redirects, ICMP controls, TCP SYN cookies
**CIS Section 4 - Logging:** Configure rsyslog, journald, log file permissions
**CIS Section 5 - Access:** Password complexity, password aging, inactive account locking (90 days), shell timeout
**SSH:** Disable root login, disable password auth, limit retries
**Firewall:** Default deny, allow SSH/HTTP/HTTPS

## Configuration

All controls have individual toggles in `ansible/roles/*/defaults/main.yml`. Override in `group_vars/all.yml`:
```yaml
# Master toggles
cis_filesystem_enable: true
cis_network_enable: true
cis_services_enable: true
cis_logging_enable: true
cis_access_enable: true

# Individual control examples
cis_network_disable_ipv6: false
cis_services_disable_cups: true
cis_access_inactive_account_days: 90
```

## Testing Locally
```bash
cd tests && docker-compose up -d
./harden.sh --inventory ansible/inventory/docker.ini --validate
firefox reports/validation-report.html
```

## Jenkins Pipeline

1. Create Pipeline job pointing to this repo
2. Add SSH credential with ID `docker-ssh-key`
3. Build with parameters (target mode, inventory path, enable validation)
