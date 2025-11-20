# Security Hardening Automation

Automated Linux security baseline configuration with CIS Level 1 compliance controls.

**Note:** This is a demonstration implementation covering key CIS Level 1 controls. Not a complete CIS benchmark implementation.

## Features

- Multi-platform: RHEL/CentOS/Amazon Linux, Ubuntu/Debian
- CIS Level 1 hardening controls (filesystem, network, services, logging, access)
- SSH hardening and firewall configuration
- Standalone Ansible execution or Jenkins pipeline
- Granular control: enable/disable individual checks

## Quick Start
```bash
git clone https://github.com/digital-knife/security-hardening.git
cd security-hardening/ansible

# Run hardening playbook
ansible-playbook playbooks/main.yml -i inventory/production.ini
```

## Project Structure
```
ansible/
├── playbooks/
│   └── main.yml                # Main hardening playbook
├── roles/
│   ├── cis-filesystem/         # Filesystem hardening
│   ├── cis-network/            # Network kernel parameters
│   ├── cis-services/           # Disable unnecessary services
│   ├── cis-logging/            # Rsyslog/journald configuration
│   ├── cis-access/             # Password policies, account controls
│   ├── ssh-hardening/          # SSH CIS controls
│   └── firewall/               # Firewall rules
├── inventory/                  # Target definitions
├── group_vars/
│   └── all.yml                 # Global configuration toggles
├── ansible.cfg                 # Ansible configuration
└── requirements.yml            # Required Ansible collections

Jenkinsfile                     # CI/CD pipeline
```

## Hardening Controls

**CIS Section 1 - Filesystem:** Disable unused filesystems (cramfs, usb-storage, etc), mount options (noexec, nosuid), permissions
**CIS Section 2 - Services:** Disable unnecessary services (avahi, cups, dhcpd, nfs, samba, squid, etc)
**CIS Section 3 - Network:** Disable IP forwarding, packet redirects, ICMP controls, TCP SYN cookies
**CIS Section 4 - Logging:** Configure rsyslog, journald, log file permissions
**CIS Section 5 - Access:** Password complexity, password aging, inactive account locking (90 days), shell timeout
**SSH Hardening:** Disable root login, disable password auth, limit retries, configure timeouts
**Firewall:** Default deny incoming, allow SSH/HTTP/HTTPS

## Configuration

All controls have individual toggles. Override defaults in `ansible/group_vars/all.yml`:
```yaml
# Master role toggles
cis_filesystem_enable: true
cis_network_enable: true
cis_services_enable: true
cis_logging_enable: true
cis_access_enable: true
ssh_hardening_enable: true
firewall_enable: true

# Individual control examples
cis_network_disable_ipv6: false
cis_services_disable_cups: true
cis_access_inactive_account_days: 90
```

View all configurable options in `ansible/roles/*/defaults/main.yml`

## Usage

### Basic Execution
```bash
cd ansible
ansible-playbook playbooks/main.yml -i inventory/production.ini
```

### Override Variables
```bash
ansible-playbook playbooks/main.yml -i inventory/production.ini \
  --extra-vars "cis_network_disable_ipv6=true cis_services_disable_cups=false"
```

## Jenkins Pipeline

### Setup

1. Create Pipeline job in Jenkins
2. Point to repository: `https://github.com/digital-knife/security-hardening.git`
3. Set Script Path: `Jenkinsfile`
4. Add SSH credential with ID `docker-ssh-key`

### Parameters

- **inventory_path:** Path to inventory file (relative to ansible/ directory)
- **dry_run:** Run in check mode without making changes
- **ansible_user:** SSH user for target hosts
- **extra_vars:** Additional Ansible variables

## Testing Locally

Create an inventory file for your target:
```ini
[targets]
webserver ansible_host=10.0.1.50 ansible_user=ec2-user
```

Run hardening:
```bash
cd ansible
ansible-playbook playbooks/main.yml -i inventory/myservers.ini --private-key ~/.ssh/my-key.pem
```

## Requirements

- Ansible 2.12+
- Python 3.9+
- SSH access to target systems
- Sudo/root privileges on targets

Install Ansible collections:
```bash
ansible-galaxy collection install -r ansible/requirements.yml
ansible-galaxy collection install ansible.posix
```