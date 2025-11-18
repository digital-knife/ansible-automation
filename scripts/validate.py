#!/usr/bin/env python3

import argparse
import logging
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Setup logging
log_file = "reports/validation.log"
Path("reports").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Security Hardening Validation")
    parser.add_argument(
        "--inventory", required=True, help="Inventory file used for hardening"
    )
    parser.add_argument(
        "--output",
        default="reports/validation-report.json",
        help="Output file for validation results",
    )
    return parser.parse_args()


def check_ssh_config(inventory):
    """Validate SSH hardening was applied"""
    logger.info("Checking SSH configuration...")

    checks = {
        "PermitRootLogin": "no",
        "PasswordAuthentication": "no",
        "PermitEmptyPasswords": "no",
        "X11Forwarding": "no",
    }

    results = []

    for setting, expected in checks.items():
        # Use Ansible ad-hoc command to check
        cmd = [
            "ansible",
            "all",
            "-i",
            inventory,
            "-m",
            "shell",
            "-a",
            f"grep '^{setting}' /etc/ssh/sshd_config || echo 'NOT FOUND'",
            "--one-line",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip()

            if expected in output:
                logger.info(f"  ✓ {setting}: Correctly set to {expected}")
                results.append(
                    {"check": setting, "status": "PASS", "expected": expected}
                )
            else:
                logger.warning(f"  ✗ {setting}: Not set correctly")
                results.append(
                    {
                        "check": setting,
                        "status": "FAIL",
                        "expected": expected,
                        "actual": output,
                    }
                )

        except subprocess.TimeoutExpired:
            logger.error(f"  ✗ {setting}: Timeout checking configuration")
            results.append({"check": setting, "status": "ERROR", "error": "Timeout"})
        except Exception as e:
            logger.error(f"  ✗ {setting}: Error - {e}")
            results.append({"check": setting, "status": "ERROR", "error": str(e)})

    return results


def check_firewall_status(inventory):
    """Validate firewall is enabled"""
    logger.info("Checking firewall status...")

    # Check for firewalld or ufw
    cmd = [
        "ansible",
        "all",
        "-i",
        inventory,
        "-m",
        "shell",
        "-a",
        "systemctl is-active firewalld || systemctl is-active ufw || echo 'INACTIVE'",
        "--one-line",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()

        if "active" in output:
            logger.info("  ✓ Firewall is active")
            return {"check": "firewall_status", "status": "PASS", "result": "active"}
        else:
            logger.warning("  ✗ Firewall is not active")
            return {"check": "firewall_status", "status": "FAIL", "result": "inactive"}

    except Exception as e:
        logger.error(f"  ✗ Error checking firewall: {e}")
        return {"check": "firewall_status", "status": "ERROR", "error": str(e)}


def run_lynis_scan(inventory):
    """Run Lynis security audit if available"""
    logger.info("Running Lynis security audit...")

    # Check if Lynis is installed
    check_cmd = [
        "ansible",
        "all",
        "-i",
        inventory,
        "-m",
        "shell",
        "-a",
        'which lynis || echo "NOT_INSTALLED"',
        "--one-line",
    ]

    try:
        result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)

        if "NOT_INSTALLED" in result.stdout:
            logger.warning("  ⚠ Lynis not installed - skipping compliance scan")
            logger.info(
                "  Install with: sudo apt install lynis (Ubuntu) or sudo yum install lynis (RHEL)"
            )
            return {
                "check": "lynis_scan",
                "status": "SKIPPED",
                "reason": "not_installed",
            }

        # Run Lynis audit
        logger.info("  Running audit (this may take 30-60 seconds)...")
        audit_cmd = [
            "ansible",
            "all",
            "-i",
            inventory,
            "-b",  # become root
            "-m",
            "shell",
            "-a",
            "lynis audit system --quick --quiet",
            "--one-line",
        ]

        audit_result = subprocess.run(
            audit_cmd, capture_output=True, text=True, timeout=120
        )

        # Parse hardening index from output
        if "Hardening index" in audit_result.stdout:
            # Extract score (format: "Hardening index : [75]")
            import re

            match = re.search(r"Hardening index.*\[(\d+)\]", audit_result.stdout)
            if match:
                score = int(match.group(1))
                logger.info(f"  ✓ Lynis Hardening Index: {score}/100")

                status = "PASS" if score >= 70 else "WARN"
                return {
                    "check": "lynis_scan",
                    "status": status,
                    "score": score,
                    "threshold": 70,
                }

        logger.info("  ✓ Lynis scan completed")
        return {"check": "lynis_scan", "status": "PASS", "result": "completed"}

    except subprocess.TimeoutExpired:
        logger.error("  ✗ Lynis scan timed out")
        return {"check": "lynis_scan", "status": "ERROR", "error": "timeout"}
    except Exception as e:
        logger.error(f"  ✗ Lynis scan error: {e}")
        return {"check": "lynis_scan", "status": "ERROR", "error": str(e)}


def main():
    """Main validation entry point"""
    args = parse_arguments()

    logger.info("=" * 60)
    logger.info("Security Hardening Validation Starting...")
    logger.info(f"Inventory: {args.inventory}")
    logger.info("=" * 60)

    # Validate inventory exists
    if not Path(args.inventory).exists():
        logger.error(f"Inventory file not found: {args.inventory}")
        sys.exit(1)

    # Run validation checks
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "inventory": args.inventory,
        "checks": {},
    }

    # SSH checks
    ssh_results = check_ssh_config(args.inventory)
    all_results["checks"]["ssh"] = ssh_results

    # Firewall check
    firewall_result = check_firewall_status(args.inventory)
    all_results["checks"]["firewall"] = firewall_result

    # Lynis compliance scan
    lynis_result = run_lynis_scan(args.inventory)
    all_results["checks"]["lynis"] = lynis_result

    # Calculate summary
    total_checks = len(ssh_results) + 1  # +1 for firewall
    if lynis_result["status"] != "SKIPPED":
        total_checks += 1

    passed_checks = sum(1 for r in ssh_results if r["status"] == "PASS")
    if firewall_result["status"] == "PASS":
        passed_checks += 1
    if lynis_result["status"] == "PASS":
        passed_checks += 1

    all_results["summary"] = {
        "total": total_checks,
        "passed": passed_checks,
        "failed": total_checks - passed_checks,
        "pass_rate": f"{(passed_checks/total_checks)*100:.1f}%",
    }

    # Write results
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    logger.info("=" * 60)
    logger.info(f"Validation complete: {passed_checks}/{total_checks} checks passed")
    logger.info(f"Results written to: {args.output}")
    logger.info("=" * 60)

    # Exit with appropriate code
    if passed_checks == total_checks:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
