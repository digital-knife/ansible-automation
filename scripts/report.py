#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from datetime import datetime

def generate_html_report(json_file, output_file):
    """Generate HTML report from validation JSON"""
    
    # Load validation results
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Calculate statistics
    summary = data.get('summary', {})
    total = summary.get('total', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    pass_rate = summary.get('pass_rate', '0%')
    
    # Determine overall status
    if passed == total:
        status_color = '#28a745'
        status_text = 'PASSED'
    elif passed >= total * 0.7:
        status_color = '#ffc107'
        status_text = 'WARNING'
    else:
        status_color = '#dc3545'
        status_text = 'FAILED'
    
    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Security Hardening Validation Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 1000px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid {status_color};
            padding-bottom: 10px;
        }}
        .status {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            background: {status_color};
            color: white;
            font-weight: bold;
            font-size: 18px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #333;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .check-section {{
            margin: 30px 0;
        }}
        .check-item {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #ccc;
        }}
        .check-item.pass {{
            border-left-color: #28a745;
        }}
        .check-item.fail {{
            border-left-color: #dc3545;
        }}
        .check-item.error {{
            border-left-color: #ffc107;
        }}
        .check-item.skip {{
            border-left-color: #6c757d;
        }}
        .check-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .check-status {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-pass {{ background: #28a745; color: white; }}
        .status-fail {{ background: #dc3545; color: white; }}
        .status-error {{ background: #ffc107; color: black; }}
        .status-skip {{ background: #6c757d; color: white; }}
        .metadata {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Security Hardening Validation Report</h1>
        <div class="status">{status_text}</div>
        
        <div class="metadata">
            <strong>Timestamp:</strong> {data.get('timestamp', 'N/A')}<br>
            <strong>Inventory:</strong> {data.get('inventory', 'N/A')}<br>
            <strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="summary">
            <div class="stat-box">
                <div class="stat-number">{total}</div>
                <div class="stat-label">Total Checks</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" style="color: #28a745;">{passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" style="color: #dc3545;">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{pass_rate}</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>
"""
    
    # SSH Checks
    ssh_checks = data.get('checks', {}).get('ssh', [])
    if ssh_checks:
        html += """
        <div class="check-section">
            <h2>SSH Configuration</h2>
"""
        for check in ssh_checks:
            status = check.get('status', 'UNKNOWN').lower()
            check_class = 'pass' if status == 'pass' else 'fail' if status == 'fail' else 'error'
            status_class = f'status-{status}'
            
            html += f"""
            <div class="check-item {check_class}">
                <div class="check-name">
                    {check.get('check', 'Unknown')}
                    <span class="check-status {status_class}">{status.upper()}</span>
                </div>
                <div>Expected: <code>{check.get('expected', 'N/A')}</code></div>
            </div>
"""
        html += "</div>"
    
    # Firewall Check
    firewall = data.get('checks', {}).get('firewall', {})
    if firewall:
        status = firewall.get('status', 'UNKNOWN').lower()
        check_class = 'pass' if status == 'pass' else 'fail'
        status_class = f'status-{status}'
        
        html += f"""
        <div class="check-section">
            <h2>Firewall Status</h2>
            <div class="check-item {check_class}">
                <div class="check-name">
                    Firewall Service
                    <span class="check-status {status_class}">{status.upper()}</span>
                </div>
                <div>Result: {firewall.get('result', 'N/A')}</div>
            </div>
        </div>
"""
    
    # Lynis Check
    lynis = data.get('checks', {}).get('lynis', {})
    if lynis and lynis.get('status') != 'SKIPPED':
        status = lynis.get('status', 'UNKNOWN').lower()
        check_class = 'pass' if status == 'pass' else 'error' if status in ['warn', 'error'] else 'skip'
        status_class = f'status-{status}'
        
        html += f"""
        <div class="check-section">
            <h2>Compliance Scan (Lynis)</h2>
            <div class="check-item {check_class}">
                <div class="check-name">
                    Security Audit
                    <span class="check-status {status_class}">{status.upper()}</span>
                </div>
"""
        if 'score' in lynis:
            html += f"<div>Hardening Index: <strong>{lynis['score']}/100</strong> (Threshold: {lynis.get('threshold', 70)})</div>"
        
        html += """
            </div>
        </div>
"""
    
    # Close HTML
    html += """
    </div>
</body>
</html>
"""
    
    # Write HTML file
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"HTML report generated: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 report.py <validation-json-file> [output-html-file]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'reports/validation-report.html'
    
    generate_html_report(json_file, output_file)
