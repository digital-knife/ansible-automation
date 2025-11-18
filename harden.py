#!/usr/bin/env python3

import argparse
import logging
import sys
import json
import tempfile
import subprocess
import os
from pathlib import Path


# Setup logging
log_file = "reports/hardening.log"
Path("reports").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file}")


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Security Hardening Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use static inventory
  ./harden.sh --inventory ansible/inventory/local.ini

  # Single target (IP/hostname/instance-id)
  ./harden.sh --target 10.0.1.50

  # AWS dynamic inventory
  ./harden.sh --dynamic-aws

  # With validation
  ./harden.sh --target 10.0.1.50 --validate
        """,
    )

    # Inventory options (mutually exclusive)
    inv_group = parser.add_mutually_exclusive_group()
    inv_group.add_argument("--inventory", help="Path to static inventory file")
    inv_group.add_argument(
        "--dynamic-aws", action="store_true", help="Use AWS EC2 dynamic inventory"
    )
    inv_group.add_argument(
        "--target",
        help="Single target: IP address, hostname, or AWS instance-id (i-xxxxx)",
    )

    # Optional flags
    parser.add_argument(
        "--validate", action="store_true", help="Run validation after hardening"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run Ansible in check mode (no changes)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times: -v, -vv, -vvv)",
    )

    return parser.parse_args()


def resolve_instance_id(instance_id):
    """Resolve AWS instance ID to IP address"""
    try:
        import boto3

        logger.info(f"Resolving instance ID: {instance_id}")
        ec2 = boto3.client("ec2")
        response = ec2.describe_instances(InstanceIds=[instance_id])
        ip = response["Reservations"][0]["Instances"][0]["PrivateIpAddress"]
        logger.info(f"Resolved to: {ip}")
        return ip
    except ImportError:
        logger.error("boto3 not installed. Cannot resolve instance ID.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to resolve instance ID: {e}")
        sys.exit(1)


def generate_single_target_inventory(target):
    """Generate Temporary inventory file for single target"""
    # is this an AWS instance id?
    if target.startswith("i-"):
        target = resolve_instance_id(target)

    logger.info(f"Generating inventory for target: {target}")

    # Create temp inventory file
    inventory_content = f"""[targets] {target} ansible_user=ec2-user ansible_ssh_common_args='-o StrictHostKeyChecking=no'"""

    # write to temp file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False)
    temp_file.write(inventory_content)
    temp_file.close()

    logger.info(f" Created temporary inventory: {temp_file.name}")
    return temp_file.name


def determine_inventory(args):
    """Determine which inventory to use based on arguments"""
    if args.target:
        return generate_single_target_inventory(args.target)
    elif args.dynamic_aws:
        inventory_path = "ansible/inventory/aws_ec2.yml"
        if not Path(inventory_path).exists():
            logger.error(f"Dynamic inventory file not found: {inventory_path}")
            sys.exit(1)
        logger.info(f"Using AWS dynamic inventory: {inventory_path}")
        return inventory_path
    elif args.inventory:
        if not Path(args.inventory).exists():
            logger.error(f"Inventory file not found: {args.inventory}")
            sys.exit(1)
        logger.info(f"Using static inventory: {args.inventory}")
        return args.inventory
    else:
        # Default to local
        default_inv = "ansible/inventory/local.ini"
        if not Path(default_inv).exists():
            logger.error(f"Default inventory not found: {default_inv}")
            sys.exit(1)
        logger.info(f"Using default inventory: {default_inv}")
        return default_inv


def run_ansible_playbook(inventory_path, args):
    """Execute playbooks with args"""
    playbook = "ansible/playbooks/main.yml"
    if not Path(playbook).exists():
        logger.error(f"Playbook not found: {playbook}")
        sys.exit(1)

    logger.info(f"Executing Playbook: {playbook}")

    # build playbook command
    cmd = ["ansible-playbook", playbook, "--inventory", inventory_path]

    if args.verbose > 0:
        cmd.append("-" + "v" * args.verbose)

    # add dry run
    if args.dry_run:
        cmd.append("--check")
        logger.info(f"Running Dry-Run mode (no changes made)")

    logger.info(f"Command: {' '.join(cmd)}")
    logger.info("=" * 60)

    try:
        result = subprocess.run(cmd, check=True, env=os.environ.copy())
        logger.info("=" * 60)
        logger.info("Hardening completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("=" * 60)
        logger.error(f"Ansible playbook failed with exit code: {e.returncode}")
        logger.error("Check the output above for errors")
        return False

    except FileNotFoundError:
        logger.error("ansible-playbook command not found!")
        logger.error("Make sure Ansible is installed in venv")
        logger.error("Run: ./setup.sh")
        return False


def get_mode_description(args):
    """Return human-readable mode description"""
    if args.target:
        return f"Single Target ({args.target})"
    elif args.dynamic_aws:
        return "AWS Dynamic Inventory"
    elif args.inventory:
        return f"Static Inventory ({args.inventory})"
    else:
        return "Default (local.ini)"


def main():
    """Main entry point"""
    args = parse_arguments()

    logger.info("Security Hardening Automation Starting...")
    logger.info(f"Mode: {get_mode_description(args)}")

    # Validate project structure
    if not Path("ansible/playbooks").exists():
        logger.error("ansible/playbooks directory not found. Run from project root.")
        sys.exit(1)

    logger.info("Project structure validated")
    logger.info("Ready to execute hardening")
    inventory_path = determine_inventory(args)
    logger.info(f"Inventory determined: {inventory_path}")

    # run the hardening
    success = run_ansible_playbook(inventory_path, args)
    if not success:
        sys.exit(1)

    if args.validate:
        logger.info("Validation requested but not yet implemented")


if __name__ == "__main__":
    main()
