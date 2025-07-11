#!/usr/bin/env python3
"""
DATABASE COMPLIANCE SCANNER
============================

Scan all database-tracked scripts for Flake8/PEP 8 compliance and emoji usage.
Enterprise-grade compliance verification without Unicode emoji characters.

Features:
- Database-first script discovery
- Flake8/PEP 8 compliance checking
- Emoji detection and reporting
- Windows console compatibility
- Comprehensive compliance reporting

Author: gh_COPILOT Enterprise Framework
Date: July 10, 2025
"""

import os
import sys
import sqlite3
import subprocess
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any
import json

# Windows-compatible visual indicators (NO Unicode emojis)
INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'warning': '[WARNING]',
    'info': '[INFO]',
    'database': '[DATABASE]',
    'check': '[CHECK]',
    'scan': '[SCAN]',
    'complete': '[COMPLETE]'
}

@dataclass
class ScriptComplianceStatus:
    """Script compliance status information"""
    file_path: str
    exists: bool = False
    flake8_compliant: bool = False
    emoji_free: bool = True
    flake8_violations: int = 0
    emojis_found: List[str] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.emojis_found is None:
            self.emojis_found = []

@dataclass
class ComplianceReport:
    """Overall compliance report"""
    total_scripts: int = 0
    existing_scripts: int = 0
    flake8_compliant_scripts: int = 0
    emoji_free_scripts: int = 0
    fully_compliant_scripts: int = 0
    scripts_with_issues: List[ScriptComplianceStatus] = None
    
    def __post_init__(self):
        if self.scripts_with_issues is None:
            self.scripts_with_issues = []

class DatabaseComplianceScanner:
    """Scan database-tracked scripts for compliance"""
    
    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.production_db = self.workspace_path / "production.db"
        self.analytics_db = self.workspace_path / "analytics.db"
        self.scan_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup logging
        log_file = self.workspace_path / f"compliance_scan_{self.scan_id}.log"
        self.log_file = log_file
        
    def log(self, message: str, indicator: str = "info"):
        """Log message with indicator"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} {INDICATORS.get(indicator, '[INFO]')} {message}"
        print(log_entry)
        
        # Write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception:
            pass  # Ignore logging errors
    
    def discover_scripts_from_databases(self) -> List[str]:
        """Discover all Python scripts tracked in databases"""
        self.log("Discovering scripts from databases", "database")
        
        discovered_scripts = set()
        
        # Check production.db
        if self.production_db.exists():
            try:
                with sqlite3.connect(self.production_db) as conn:
                    cursor = conn.cursor()
                    
                    # Get scripts from enterprise_script_tracking
                    try:
                        cursor.execute("SELECT script_path FROM enterprise_script_tracking WHERE script_path LIKE '%.py'")
                        scripts = cursor.fetchall()
                        for script_path, in scripts:
                            if script_path:
                                discovered_scripts.add(script_path)
                        self.log(f"Found {len(scripts)} scripts in production.db enterprise_script_tracking", "success")
                    except Exception as e:
                        self.log(f"Could not access enterprise_script_tracking: {e}", "warning")
                        
                    # Also check script_tracking table
                    try:
                        cursor.execute("SELECT script_path FROM script_tracking WHERE script_path LIKE '%.py'")
                        scripts = cursor.fetchall()
                        for script_path, in scripts:
                            if script_path:
                                discovered_scripts.add(script_path)
                        self.log(f"Found {len(scripts)} scripts in production.db script_tracking", "success")
                    except Exception as e:
                        self.log(f"Could not access script_tracking: {e}", "warning")
                        
            except Exception as e:
                self.log(f"Could not access production.db: {e}", "error")
        else:
            self.log("production.db not found", "warning")
        
        # Check analytics.db
        if self.analytics_db.exists():
            try:
                with sqlite3.connect(self.analytics_db) as conn:
                    cursor = conn.cursor()
                    
                    # Get scripts from pis_violations table
                    try:
                        cursor.execute("SELECT DISTINCT file_path FROM pis_violations WHERE file_path LIKE '%.py'")
                        scripts = cursor.fetchall()
                        for script_path, in scripts:
                            if script_path:
                                discovered_scripts.add(script_path)
                        self.log(f"Found {len(scripts)} scripts in analytics.db pis_violations", "success")
                    except Exception as e:
                        self.log(f"Could not access pis_violations table: {e}", "warning")
                        
                    # Also check compliance_violations if it has data
                    try:
                        cursor.execute("SELECT DISTINCT file_path FROM compliance_violations WHERE file_path LIKE '%.py'")
                        scripts = cursor.fetchall()
                        for script_path, in scripts:
                            if script_path:
                                discovered_scripts.add(script_path)
                        self.log(f"Found {len(scripts)} scripts in analytics.db compliance_violations", "success")
                    except Exception as e:
                        self.log(f"Could not access compliance_violations table: {e}", "warning")
                        
            except Exception as e:
                self.log(f"Could not access analytics.db: {e}", "error")
        else:
            self.log("analytics.db not found", "warning")
        
        discovered_list = list(discovered_scripts)
        self.log(f"Total unique scripts discovered: {len(discovered_list)}", "info")
        return discovered_list
    
    def check_script_compliance(self, script_path: str) -> ScriptComplianceStatus:
        """Check individual script for compliance"""
        status = ScriptComplianceStatus(file_path=script_path)
        
        # Check if file exists
        if not os.path.exists(script_path):
            status.error_message = "File does not exist"
            return status
        
        status.exists = True
        
        try:
            # Read file content
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for emojis (Unicode characters above ASCII range)
            emoji_patterns = [
                '🚀', '✅', '❌', '⚠️', '📊', '🔍', '💻', '🛡️', '🎯', '📁', 
                '🔧', '💡', '📋', '🌐', '🏢', '⚛️', '🎬', '🔄', '🤖', '📈'
            ]
            
            found_emojis = []
            for emoji in emoji_patterns:
                if emoji in content:
                    found_emojis.append(emoji)
            
            if found_emojis:
                status.emoji_free = False
                status.emojis_found = found_emojis
            else:
                status.emoji_free = True
            
            # Check Flake8 compliance
            try:
                result = subprocess.run(
                    ['flake8', '--max-line-length=120', script_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                if result.returncode == 0:
                    status.flake8_compliant = True
                    status.flake8_violations = 0
                else:
                    status.flake8_compliant = False
                    # Count violations
                    violations = result.stdout.strip().split('\n') if result.stdout.strip() else []
                    status.flake8_violations = len([v for v in violations if v.strip()])
                    
            except subprocess.TimeoutExpired:
                status.error_message = "Flake8 check timeout"
            except FileNotFoundError:
                status.error_message = "Flake8 not found"
            except Exception as e:
                status.error_message = f"Flake8 check failed: {e}"
                
        except Exception as e:
            status.error_message = f"File analysis failed: {e}"
        
        return status
    
    def scan_all_scripts(self) -> ComplianceReport:
        """Scan all database-tracked scripts for compliance"""
        self.log("Starting comprehensive compliance scan", "start")
        
        # Discover scripts
        script_paths = self.discover_scripts_from_databases()
        
        if not script_paths:
            self.log("No scripts found in databases", "warning")
            return ComplianceReport()
        
        report = ComplianceReport()
        report.total_scripts = len(script_paths)
        
        # Check each script
        for i, script_path in enumerate(script_paths, 1):
            self.log(f"Checking script {i}/{len(script_paths)}: {script_path}", "scan")
            
            status = self.check_script_compliance(script_path)
            
            if status.exists:
                report.existing_scripts += 1
                
                if status.flake8_compliant:
                    report.flake8_compliant_scripts += 1
                    
                if status.emoji_free:
                    report.emoji_free_scripts += 1
                    
                if status.flake8_compliant and status.emoji_free:
                    report.fully_compliant_scripts += 1
                else:
                    report.scripts_with_issues.append(status)
        
        self.log("Compliance scan completed", "complete")
        return report
    
    def generate_compliance_report(self, report: ComplianceReport) -> str:
        """Generate detailed compliance report"""
        self.log("Generating compliance report", "info")
        
        report_data = {
            "scan_id": self.scan_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_scripts_in_databases": report.total_scripts,
                "existing_scripts": report.existing_scripts,
                "flake8_compliant_scripts": report.flake8_compliant_scripts,
                "emoji_free_scripts": report.emoji_free_scripts,
                "fully_compliant_scripts": report.fully_compliant_scripts,
                "scripts_with_issues": len(report.scripts_with_issues)
            },
            "compliance_percentages": {
                "flake8_compliance": (report.flake8_compliant_scripts / report.existing_scripts * 100) if report.existing_scripts > 0 else 0,
                "emoji_free": (report.emoji_free_scripts / report.existing_scripts * 100) if report.existing_scripts > 0 else 0,
                "full_compliance": (report.fully_compliant_scripts / report.existing_scripts * 100) if report.existing_scripts > 0 else 0
            },
            "issues_found": []
        }
        
        # Add issue details
        for status in report.scripts_with_issues:
            issue = {
                "file_path": status.file_path,
                "flake8_compliant": status.flake8_compliant,
                "emoji_free": status.emoji_free,
                "flake8_violations": status.flake8_violations,
                "emojis_found": status.emojis_found,
                "error_message": status.error_message
            }
            report_data["issues_found"].append(issue)
        
        # Save report
        report_file = self.workspace_path / f"compliance_report_{self.scan_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        self.log(f"Report saved to: {report_file}", "success")
        return str(report_file)
    
    def print_summary(self, report: ComplianceReport):
        """Print compliance summary"""
        print("\n" + "=" * 80)
        print(f"{INDICATORS['complete']} DATABASE SCRIPT COMPLIANCE SUMMARY")
        print("=" * 80)
        
        print(f"Total scripts in databases: {report.total_scripts}")
        print(f"Existing scripts: {report.existing_scripts}")
        print(f"Flake8/PEP 8 compliant: {report.flake8_compliant_scripts}")
        print(f"Emoji-free scripts: {report.emoji_free_scripts}")
        print(f"FULLY COMPLIANT scripts: {report.fully_compliant_scripts}")
        
        if report.existing_scripts > 0:
            flake8_pct = (report.flake8_compliant_scripts / report.existing_scripts) * 100
            emoji_pct = (report.emoji_free_scripts / report.existing_scripts) * 100
            full_pct = (report.fully_compliant_scripts / report.existing_scripts) * 100
            
            print(f"\nCompliance Percentages:")
            print(f"  Flake8/PEP 8: {flake8_pct:.1f}%")
            print(f"  Emoji-free: {emoji_pct:.1f}%")
            print(f"  FULL COMPLIANCE: {full_pct:.1f}%")
            
            # Determine compliance status
            if full_pct == 100.0:
                print(f"\n{INDICATORS['success']} ALL DATABASE-TRACKED SCRIPTS ARE 100% COMPLIANT!")
            else:
                print(f"\n{INDICATORS['warning']} NOT ALL SCRIPTS ARE FULLY COMPLIANT")
                print(f"Scripts needing attention: {len(report.scripts_with_issues)}")
        
        print("=" * 80)

def main():
    """Main execution function"""
    print(f"{INDICATORS['start']} DATABASE COMPLIANCE SCANNER")
    print("Checking all database-tracked scripts for Flake8/PEP 8 compliance and emoji usage")
    print("=" * 80)
    
    try:
        scanner = DatabaseComplianceScanner()
        report = scanner.scan_all_scripts()
        scanner.print_summary(report)
        report_file = scanner.generate_compliance_report(report)
        
        print(f"\n{INDICATORS['info']} Detailed report saved to: {report_file}")
        print(f"{INDICATORS['info']} Log file saved to: {scanner.log_file}")
        
        return report
        
    except Exception as e:
        print(f"{INDICATORS['error']} CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
