#!/usr/bin/env python3
"""
🏠 COMPLETE ROOT MAINTENANCE VALIDATOR
100% File Placement Compliance Enforcement System

MISSION: Ensure 100% file placement compliance across all enterprise folders
- Validate ALL logs are in logs/ folder
- Validate ALL reports are in reports/ folder  
- Validate ALL results are in results/ folder
- Validate ALL documentation is in documentation/ folder
- Validate ALL configs are in config/ folder
- Generate compliance reports with violation details

Author: GitHub Copilot with Enterprise Intelligence
Created: July 16, 2025
"""

import json
import logging
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from tqdm import tqdm

# Severity weights for compliance scoring
SEVERITY_WEIGHTS = {
    "LOW": 1,
    "MEDIUM": 3,
    "HIGH": 5,
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ComplianceViolation:
    """Individual compliance violation details"""
    file_path: str
    expected_folder: str
    current_location: str
    violation_type: str
    severity: str = "MEDIUM"
    auto_fixable: bool = True
    fix_command: str = ""

@dataclass
class ComplianceResult:
    """Complete compliance validation result"""
    session_id: str
    validation_time: datetime
    total_files_checked: int = 0
    compliant_files: int = 0
    violations: List[ComplianceViolation] = field(default_factory=list)
    compliance_score: float = 0.0
    folder_compliance: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class CompleteRootMaintenanceValidator:
    """
    🏠 Complete Root Maintenance Validator
    
    Ensures 100% file placement compliance with:
    - Database-driven pattern recognition
    - Automated violation detection
    - Compliance scoring and reporting
    - Auto-fix recommendations
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.session_id = f"compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Database connection
        self.production_db = self.workspace_path / "databases" / "production.db"
        
        # File organization rules
        self.organization_rules = {
            'logs': {
                'folder': 'logs',
                'patterns': ['.log', '_log_', 'log_', '.logfile', 'logging'],
                'extensions': ['.log', '.txt'],
                'description': 'Log files and logging outputs'
            },
            'reports': {
                'folder': 'reports', 
                'patterns': ['report', 'summary', 'analysis', 'breakdown', 'assessment', 'evaluation'],
                'extensions': ['.md', '.txt', '.json', '.html', '.pdf'],
                'description': 'Analysis reports and summaries'
            },
            'results': {
                'folder': 'results',
                'patterns': ['result', 'output', 'data', 'processed', 'generated', 'extracted'],
                'extensions': ['.json', '.csv', '.txt', '.xml', '.data'],
                'description': 'Processing results and output data'
            },
            'documentation': {
                'folder': 'documentation',
                'patterns': ['doc', 'readme', 'guide', 'manual', 'help', 'instruction'],
                'extensions': ['.md', '.txt', '.rst', '.html'],
                'description': 'Documentation and guidance files'
            },
            'config': {
                'folder': 'config',
                'patterns': ['config', 'configuration', 'settings', 'env', 'environment'],
                'extensions': ['.json', '.yaml', '.yml', '.ini', '.cfg', '.toml', '.env'],
                'description': 'Configuration and settings files'
            }
        }
        
        # Essential files that should remain in root
        self.essential_root_files = {
            'README.md', 'CHANGELOG.md', 'LICENSE', 'LICENSE.txt',
            'requirements.txt', 'package.json', 'package-lock.json',
            'Makefile', 'docker-compose.yml', 'Dockerfile',
            'pyproject.toml', '.gitignore', '.env',
            'COPILOT_NAVIGATION_MAP.json'
        }
        
        logger.info("🏠 Complete Root Maintenance Validator initialized")
        logger.info("Session ID: %s", self.session_id)
        logger.info("Workspace: %s", self.workspace_path)
    
    def validate_complete_compliance(self) -> ComplianceResult:
        """
        🔍 Execute complete compliance validation
        
        Returns comprehensive compliance analysis with:
        - Detailed violation reports
        - Folder-by-folder compliance scores
        - Auto-fix recommendations
        - Executive summary
        """
        
        logger.info("🔍 Starting complete compliance validation")
        
        result = ComplianceResult(
            session_id=self.session_id,
            validation_time=datetime.now()
        )
        
        try:
            # Phase 1: Scan all files in workspace
            with tqdm(total=100, desc="🔍 Phase 1: File Discovery", unit="%") as pbar:
                all_files = self._discover_all_files(pbar)
                result.total_files_checked = len(all_files)
                pbar.update(100)
            
            # Phase 2: Validate file placements
            with tqdm(total=100, desc="📋 Phase 2: Compliance Check", unit="%") as pbar:
                violations = self._validate_file_placements(all_files, pbar)
                result.violations = violations
                pbar.update(100)
            
            # Phase 3: Calculate compliance scores
            with tqdm(total=100, desc="📊 Phase 3: Score Calculation", unit="%") as pbar:
                self._calculate_compliance_scores(result, pbar)
                pbar.update(100)
            
            # Phase 4: Generate recommendations
            with tqdm(total=100, desc="🎯 Phase 4: Recommendations", unit="%") as pbar:
                self._generate_compliance_recommendations(result, pbar)
                pbar.update(100)
            
            # Phase 5: Store results in database
            with tqdm(total=100, desc="💾 Phase 5: Database Storage", unit="%") as pbar:
                self._store_compliance_results(result, pbar)
                pbar.update(100)
            
            logger.info("✅ Compliance validation completed")
            logger.info("📊 Overall Compliance: %.1f%%", result.compliance_score)
            logger.info("📊 Violations Found: %d", len(result.violations))
            
        except Exception as e:
            logger.error("❌ Compliance validation failed: %s", e)
            if result.recommendations is None:
                result.recommendations = []
            result.recommendations.append(f"ERROR: Validation failed - {e}")
        
        return result
    
    def _discover_all_files(self, pbar: tqdm) -> List[Path]:
        """🔍 Discover all files in workspace for validation"""
        all_files = []
        
        # Scan root directory
        pbar.set_description("🔍 Scanning root directory")
        for item in self.workspace_path.iterdir():
            if item.is_file():
                all_files.append(item)
        
        # Scan subdirectories but skip certain folders
        skip_folders = {
            '__pycache__', '.git', '.venv', 'node_modules',
            Path(os.getenv('GH_COPILOT_BACKUP_ROOT', '/tmp')).name, '_ZERO_BYTE_QUARANTINE',
            'archives', 'builds'
        }
        
        pbar.set_description("🔍 Scanning subdirectories")
        for item in self.workspace_path.iterdir():
            if item.is_dir() and item.name not in skip_folders:
                try:
                    for sub_file in item.rglob('*'):
                        if sub_file.is_file():
                            all_files.append(sub_file)
                except (PermissionError, OSError) as e:
                    logger.warning("⚠️ Cannot access %s: %s", item, e)
        
        logger.info("📊 Discovered %d files for validation", len(all_files))
        return all_files
    
    def _validate_file_placements(self, all_files: List[Path], pbar: tqdm) -> List[ComplianceViolation]:
        """📋 Validate file placements against organization rules"""
        violations = []
        processed = 0
        
        for file_path in all_files:
            try:
                pbar.set_description(f"📋 Checking {file_path.name}")
                
                # Check if file should be organized
                violation = self._check_file_compliance(file_path)
                if violation:
                    violations.append(violation)
                
                processed += 1
                if processed % 10 == 0:  # Update progress every 10 files
                    progress = (processed / len(all_files)) * 100
                    pbar.n = min(progress, 99)  # Don't reach 100 until complete
                    pbar.refresh()
                
            except Exception as e:
                logger.warning("⚠️ Failed to check %s: %s", file_path, e)
        
        logger.info("📊 Found %d compliance violations", len(violations))
        return violations
    
    def _check_file_compliance(self, file_path: Path) -> Optional[ComplianceViolation]:
        """🔍 Check individual file compliance"""
        try:
            # Get relative path from workspace
            rel_path = file_path.relative_to(self.workspace_path)
            file_name = file_path.name.lower()
            file_extension = file_path.suffix.lower()
            
            # Skip files already in correct folders
            current_folder = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
            
            # Skip essential root files
            if file_path.name in self.essential_root_files and current_folder == "root":
                return None
            
            # Check against each organization rule
            for rule_name, rule_config in self.organization_rules.items():
                expected_folder = rule_config['folder']
                
                # Skip if already in correct folder
                if current_folder == expected_folder:
                    continue
                
                # Check if file matches this rule
                matches_pattern = any(pattern in file_name for pattern in rule_config['patterns'])
                matches_extension = file_extension in rule_config['extensions']
                
                if matches_pattern or matches_extension:
                    # File should be in this folder but isn't
                    violation_type = "MISPLACED_FILE"
                    severity = "HIGH" if current_folder == "root" else "MEDIUM"
                    
                    dest = self.workspace_path / expected_folder / file_path.name
                    return ComplianceViolation(
                        file_path=str(file_path),
                        expected_folder=expected_folder,
                        current_location=current_folder,
                        violation_type=violation_type,
                        severity=severity,
                        auto_fixable=True,
                        fix_command=f"mv '{file_path}' '{dest}'"
                    )
            
            # Check for files in root that should be organized
            if current_folder == "root" and file_path.name not in self.essential_root_files:
                # Determine best folder for this file
                best_folder = self._determine_best_folder(file_path)
                
                if best_folder:
                    dest = self.workspace_path / best_folder / file_path.name
                    return ComplianceViolation(
                        file_path=str(file_path),
                        expected_folder=best_folder,
                        current_location="root",
                        violation_type="ROOT_CLUTTER",
                        severity="MEDIUM",
                        auto_fixable=True,
                        fix_command=f"mv '{file_path}' '{dest}'"
                    )
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Compliance check failed for {file_path}: {e}")
            return None
    
    def _determine_best_folder(self, file_path: Path) -> Optional[str]:
        """🎯 Determine best folder for unorganized file"""
        file_name = file_path.name.lower()
        file_extension = file_path.suffix.lower()
        
        # Score each rule
        rule_scores = {}
        
        for rule_name, rule_config in self.organization_rules.items():
            score = 0
            
            # Pattern matching score
            for pattern in rule_config['patterns']:
                if pattern in file_name:
                    score += 2
            
            # Extension matching score
            if file_extension in rule_config['extensions']:
                score += 3
            
            if score > 0:
                rule_scores[rule_name] = score
        
        # Return best match
        if rule_scores:
            best_rule = max(rule_scores.items(), key=lambda x: x[1])
            return self.organization_rules[best_rule[0]]['folder']
        
        # Default fallback
        if file_extension in ['.py', '.ps1', '.sh', '.bat']:
            return 'scripts'
        elif file_extension in ['.md', '.txt', '.rst']:
            return 'documentation'
        else:
            return 'misc'  # Create misc folder for unclassified files
    
    def _calculate_compliance_scores(self, result: ComplianceResult, pbar: tqdm):
        """📊 Calculate detailed compliance scores"""
        total_files = result.total_files_checked

        # Weighted score based on violation severity
        weighted_violations = 0
        for v in result.violations:
            weighted_violations += SEVERITY_WEIGHTS.get(v.severity, 1)

        max_score = total_files * max(SEVERITY_WEIGHTS.values())
        compliance_ratio = 1 - (weighted_violations / max_score) if max_score > 0 else 1

        result.compliant_files = total_files - len(result.violations)
        result.compliance_score = round(compliance_ratio * 100, 1)
        
        # Folder-specific compliance scores
        folder_violations = {}
        
        pbar.set_description("📊 Calculating folder compliance")
        
        # Count violations by expected folder
        for violation in result.violations:
            folder = violation.expected_folder
            folder_violations[folder] = folder_violations.get(folder, 0) + 1
        
        # Count total files that should be in each folder
        for rule_name, rule_config in self.organization_rules.items():
            folder = rule_config['folder']
            folder_path = self.workspace_path / folder
            
            # Count files currently in correct folder
            correct_count = 0
            if folder_path.exists():
                correct_count = len([f for f in folder_path.rglob('*') if f.is_file()])
            
            # Add violations for this folder
            violations_count = folder_violations.get(folder, 0)
            total_should_be = correct_count + violations_count
            
            # Calculate folder compliance
            if total_should_be > 0:
                folder_compliance = (correct_count / total_should_be) * 100
                result.folder_compliance[folder] = round(folder_compliance, 1)
            else:
                result.folder_compliance[folder] = 100.0
        
        logger.info("📊 Compliance calculated: %.1f%%", result.compliance_score)
    
    def _generate_compliance_recommendations(self, result: ComplianceResult, pbar: tqdm):
        """🎯 Generate actionable compliance recommendations"""
        recommendations = []
        
        pbar.set_description("🎯 Generating recommendations")
        
        # Overall recommendations
        if result.compliance_score < 50:
            recommendations.append("🚨 CRITICAL: Major compliance issues detected - immediate action required")
        elif result.compliance_score < 80:
            recommendations.append("⚠️ WARNING: Moderate compliance issues - organization needed")
        elif result.compliance_score < 95:
            recommendations.append("📋 NOTICE: Minor compliance issues - fine-tuning recommended")
        else:
            recommendations.append("✅ EXCELLENT: High compliance achieved - maintain current standards")
        
        # Folder-specific recommendations
        for folder, compliance_score in result.folder_compliance.items():
            if compliance_score < 80:
                violation_count = len([v for v in result.violations if v.expected_folder == folder])
                recommendations.append(
                    (
                        f"📁 {folder.upper()}: {violation_count} files need organization "
                        f"(compliance: {compliance_score:.1f}%)"
                    )
                )
        
        # Auto-fix recommendations
        auto_fixable = len([v for v in result.violations if v.auto_fixable])
        if auto_fixable > 0:
            recommendations.append(f"🔧 AUTO-FIX: {auto_fixable} violations can be automatically resolved")
            for v in result.violations[:5]:
                if v.auto_fixable and v.fix_command:
                    recommendations.append(f"  - {v.fix_command}")
        
        # High-priority recommendations
        high_priority = len([v for v in result.violations if v.severity == "HIGH"])
        if high_priority > 0:
            recommendations.append(f"🔥 HIGH PRIORITY: {high_priority} violations require immediate attention")
        
        # Root cleanup recommendations
        root_violations = len([v for v in result.violations if v.current_location == "root"])
        if root_violations > 0:
            recommendations.append(
                f"🏠 ROOT CLEANUP: {root_violations} files should be moved from root directory"
            )
        
        result.recommendations = recommendations
        
        logger.info("🎯 Generated %d recommendations", len(recommendations))
    
    def _store_compliance_results(self, result: ComplianceResult, pbar: tqdm):
        """💾 Store compliance results in database"""
        try:
            pbar.set_description("💾 Storing in database")
            
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()
                
                # Create compliance results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_validation_results (
                        session_id TEXT PRIMARY KEY,
                        validation_time TEXT,
                        total_files_checked INTEGER,
                        compliant_files INTEGER,
                        compliance_score REAL,
                        violations_count INTEGER,
                        folder_compliance TEXT,
                        recommendations TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert main results
                cursor.execute("""
                    INSERT OR REPLACE INTO compliance_validation_results
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.session_id,
                    result.validation_time.isoformat(),
                    result.total_files_checked,
                    result.compliant_files,
                    result.compliance_score,
                    len(result.violations),
                    json.dumps(result.folder_compliance),
                    json.dumps(result.recommendations),
                    datetime.now().isoformat()
                ))
                
                # Create violations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        file_path TEXT,
                        expected_folder TEXT,
                        current_location TEXT,
                        violation_type TEXT,
                        severity TEXT,
                        auto_fixable BOOLEAN,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES compliance_validation_results (session_id)
                    )
                """)
                
                # Insert violations
                for violation in result.violations:
                    cursor.execute("""
                        INSERT INTO compliance_violations
                        (session_id, file_path, expected_folder, current_location, 
                         violation_type, severity, auto_fixable)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        result.session_id,
                        violation.file_path,
                        violation.expected_folder,
                        violation.current_location,
                        violation.violation_type,
                        violation.severity,
                        violation.auto_fixable
                    ))
                
                conn.commit()
                logger.info("💾 Compliance results stored in database")
                
        except Exception as e:
            logger.error("❌ Database storage failed: %s", e)
    
    def generate_compliance_report(self, result: ComplianceResult) -> str:
        """📊 Generate comprehensive compliance report"""
        
        report_lines = [
            "# 🏠 COMPLETE ROOT MAINTENANCE VALIDATION REPORT",
            "",
            "## 📊 Executive Summary",
            f"- **Session ID**: {result.session_id}",
            f"- **Validation Time**: {result.validation_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Overall Compliance**: {result.compliance_score:.1f}%",
            f"- **Files Checked**: {result.total_files_checked:,}",
            f"- **Compliant Files**: {result.compliant_files:,}",
            f"- **Violations Found**: {len(result.violations):,}",
            "",
            "## 📁 Folder Compliance Breakdown"
        ]
        
        # Folder compliance details
        for folder, score in sorted(result.folder_compliance.items()):
            status_icon = "✅" if score >= 95 else "⚠️" if score >= 80 else "❌"
            report_lines.append(f"- **{folder}/**: {score:.1f}% {status_icon}")
        
        report_lines.extend([
            "",
            "## 🚨 Compliance Violations",
            ""
        ])
        
        # Group violations by severity
        violations_by_severity = {}
        for violation in result.violations:
            severity = violation.severity
            if severity not in violations_by_severity:
                violations_by_severity[severity] = []
            violations_by_severity[severity].append(violation)
        
        # Display violations by severity
        for severity in ["HIGH", "MEDIUM", "LOW"]:
            if severity in violations_by_severity:
                violations = violations_by_severity[severity]
                icon = "🔥" if severity == "HIGH" else "⚠️" if severity == "MEDIUM" else "📝"
                
                report_lines.extend([
                    f"### {icon} {severity} Priority ({len(violations)} violations)",
                    ""
                ])
                
                for violation in violations[:10]:  # Limit to first 10 per severity
                    file_name = Path(violation.file_path).name
                    report_lines.append(
                        f"- `{file_name}` → should be in `{violation.expected_folder}/` "
                        f"(currently in `{violation.current_location}`)"
                    )
                
                if len(violations) > 10:
                    report_lines.append(f"- ... and {len(violations) - 10} more")
                
                report_lines.append("")
        
        # Recommendations section
        report_lines.extend([
            "## 🎯 Recommendations",
            ""
        ])
        
        for recommendation in result.recommendations:
            report_lines.append(f"- {recommendation}")
        
        # Auto-fix section
        auto_fixable_count = len([v for v in result.violations if v.auto_fixable])
        if auto_fixable_count > 0:
            report_lines.extend([
                "",
                "## 🔧 Auto-Fix Available",
                "",
                f"{auto_fixable_count} violations can be automatically resolved using the file organization tools.",
                "",
                "Run the following command to auto-fix violations:",
                "```bash",
                "python scripts/orchestrators/unified_wrapup_orchestrator.py",
                "```",
                "",
                "### Suggested Commands",
            ])
            for v in result.violations[:5]:
                if v.auto_fixable and v.fix_command:
                    report_lines.append(f"- {v.fix_command}")
        
        report_lines.extend([
            "",
            "---",
            "*Generated by Complete Root Maintenance Validator v4.0*",
            "*Database-First Enterprise Compliance Framework*"
        ])
        
        return "\n".join(report_lines)
    
    def export_compliance_report(self, result: ComplianceResult) -> Path:
        """📤 Export compliance report to reports folder"""
        # Ensure reports folder exists
        reports_folder = self.workspace_path / 'reports'
        reports_folder.mkdir(exist_ok=True)
        
        # Generate report content
        report_content = self.generate_compliance_report(result)
        
        # Save report
        report_file = reports_folder / f"root_maintenance_compliance_{result.session_id}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info("📊 Compliance report exported: %s", report_file)
        
        return report_file

def main():
    """🚀 Main execution function"""
    print("🏠 COMPLETE ROOT MAINTENANCE VALIDATOR")
    print("100% File Placement Compliance Enforcement")
    print("="*60)
    
    try:
        # Initialize validator
        validator = CompleteRootMaintenanceValidator()
        
        # Execute compliance validation
        result = validator.validate_complete_compliance()
        
        # Export compliance report
        report_file = validator.export_compliance_report(result)
        
        # Display summary
        print("\n" + "="*60)
        print("📊 COMPLIANCE VALIDATION SUMMARY")
        print("="*60)
        print(f"Overall Compliance: {result.compliance_score:.1f}%")
        print(f"Files Checked: {result.total_files_checked:,}")
        print(f"Violations Found: {len(result.violations):,}")
        print(f"Report Exported: {report_file}")
        
        # Display folder compliance
        print("\n📁 Folder Compliance:")
        for folder, score in sorted(result.folder_compliance.items()):
            status = "✅" if score >= 95 else "⚠️" if score >= 80 else "❌"
            print(f"  {folder}/: {score:.1f}% {status}")
        
        # Display top recommendations
        print("\n🎯 Top Recommendations:")
        for rec in result.recommendations[:3]:
            print(f"  - {rec}")
        
        if result.compliance_score >= 95:
            print("\n🎉 EXCELLENT COMPLIANCE ACHIEVED!")
            return 0
        elif result.compliance_score >= 80:
            print("\n📋 GOOD COMPLIANCE - Minor improvements needed")
            return 0
        else:
            print("\n⚠️ COMPLIANCE ISSUES DETECTED - Action required")
            return 1
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
