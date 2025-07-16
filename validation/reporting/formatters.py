"""
Validation report formatting utilities.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..core.validators import ValidationResult, ValidationStatus


class ValidationReportFormatter:
    """Formats validation results into various output formats"""
    
    def __init__(self):
        self.timestamp = datetime.now()
    
    def format_text_report(self, results: List[ValidationResult], title: str = "Validation Report") -> str:
        """Format validation results as text report"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"{title}")
        lines.append(f"Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        errors = sum(1 for r in results if r.status == ValidationStatus.ERROR)
        skipped = sum(1 for r in results if r.status == ValidationStatus.SKIPPED)
        
        lines.append("SUMMARY:")
        lines.append(f"  Total Validations: {len(results)}")
        lines.append(f"  Passed: {passed}")
        lines.append(f"  Failed: {failed}")
        lines.append(f"  Warnings: {warnings}")
        lines.append(f"  Errors: {errors}")
        lines.append(f"  Skipped: {skipped}")
        lines.append("")
        
        # Overall status
        if failed > 0 or errors > 0:
            overall_status = "FAILED"
        elif warnings > 0:
            overall_status = "PASSED WITH WARNINGS"
        else:
            overall_status = "PASSED"
        
        lines.append(f"OVERALL STATUS: {overall_status}")
        lines.append("")
        
        # Detailed results
        lines.append("DETAILED RESULTS:")
        lines.append("-" * 40)
        
        for i, result in enumerate(results, 1):
            status_symbol = self._get_status_symbol(result.status)
            lines.append(f"{i}. {status_symbol} {result.message}")
            
            if result.errors:
                for error in result.errors:
                    lines.append(f"     Error: {error}")
            
            if result.warnings:
                for warning in result.warnings:
                    lines.append(f"     Warning: {warning}")
            
            if result.details:
                lines.append(f"     Details: {self._format_details(result.details)}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def format_json_report(self, results: List[ValidationResult], title: str = "Validation Report") -> str:
        """Format validation results as JSON report"""
        report_data = {
            "title": title,
            "timestamp": self.timestamp.isoformat(),
            "summary": self._get_summary(results),
            "overall_status": self._get_overall_status(results),
            "results": []
        }
        
        for result in results:
            result_data = {
                "status": result.status.value,
                "message": result.message,
                "timestamp": result.timestamp.isoformat(),
                "details": result.details,
                "errors": result.errors,
                "warnings": result.warnings
            }
            report_data["results"].append(result_data)
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def format_markdown_report(self, results: List[ValidationResult], title: str = "Validation Report") -> str:
        """Format validation results as Markdown report"""
        lines = []
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"**Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary
        summary = self._get_summary(results)
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Validations:** {summary['total']}")
        lines.append(f"- **Passed:** {summary['passed']}")
        lines.append(f"- **Failed:** {summary['failed']}")
        lines.append(f"- **Warnings:** {summary['warnings']}")
        lines.append(f"- **Errors:** {summary['errors']}")
        lines.append(f"- **Skipped:** {summary['skipped']}")
        lines.append("")
        
        # Overall status
        overall_status = self._get_overall_status(results)
        status_emoji = "✅" if overall_status == "PASSED" else "⚠️" if "WARNING" in overall_status else "❌"
        lines.append(f"## Overall Status: {status_emoji} {overall_status}")
        lines.append("")
        
        # Detailed results
        lines.append("## Detailed Results")
        lines.append("")
        
        for i, result in enumerate(results, 1):
            status_emoji = self._get_status_emoji(result.status)
            lines.append(f"### {i}. {status_emoji} {result.message}")
            lines.append("")
            
            if result.errors:
                lines.append("**Errors:**")
                for error in result.errors:
                    lines.append(f"- {error}")
                lines.append("")
            
            if result.warnings:
                lines.append("**Warnings:**")
                for warning in result.warnings:
                    lines.append(f"- {warning}")
                lines.append("")
            
            if result.details:
                lines.append("**Details:**")
                lines.append("```json")
                lines.append(json.dumps(result.details, indent=2))
                lines.append("```")
                lines.append("")
        
        return "\n".join(lines)
    
    def save_report(self, results: List[ValidationResult], output_path: Path, 
                   format_type: str = "json", title: str = "Validation Report") -> bool:
        """Save validation report to file"""
        try:
            if format_type.lower() == "json":
                content = self.format_json_report(results, title)
                output_path = output_path.with_suffix('.json')
            elif format_type.lower() == "markdown" or format_type.lower() == "md":
                content = self.format_markdown_report(results, title)
                output_path = output_path.with_suffix('.md')
            elif format_type.lower() == "text" or format_type.lower() == "txt":
                content = self.format_text_report(results, title)
                output_path = output_path.with_suffix('.txt')
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error saving report: {e}")
            return False
    
    def _get_summary(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Get summary statistics"""
        return {
            "total": len(results),
            "passed": sum(1 for r in results if r.status == ValidationStatus.PASSED),
            "failed": sum(1 for r in results if r.status == ValidationStatus.FAILED),
            "warnings": sum(1 for r in results if r.status == ValidationStatus.WARNING),
            "errors": sum(1 for r in results if r.status == ValidationStatus.ERROR),
            "skipped": sum(1 for r in results if r.status == ValidationStatus.SKIPPED)
        }
    
    def _get_overall_status(self, results: List[ValidationResult]) -> str:
        """Get overall validation status"""
        summary = self._get_summary(results)
        
        if summary["failed"] > 0 or summary["errors"] > 0:
            return "FAILED"
        elif summary["warnings"] > 0:
            return "PASSED WITH WARNINGS"
        else:
            return "PASSED"
    
    def _get_status_symbol(self, status: ValidationStatus) -> str:
        """Get text symbol for status"""
        symbols = {
            ValidationStatus.PASSED: "✓",
            ValidationStatus.FAILED: "✗",
            ValidationStatus.WARNING: "⚠",
            ValidationStatus.ERROR: "💥",
            ValidationStatus.SKIPPED: "⏭"
        }
        return symbols.get(status, "?")
    
    def _get_status_emoji(self, status: ValidationStatus) -> str:
        """Get emoji for status"""
        emojis = {
            ValidationStatus.PASSED: "✅",
            ValidationStatus.FAILED: "❌",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.ERROR: "💥",
            ValidationStatus.SKIPPED: "⏭️"
        }
        return emojis.get(status, "❓")
    
    def _format_details(self, details: Dict[str, Any]) -> str:
        """Format details for text output"""
        if not details:
            return ""
        
        # Simplified formatting for text output
        formatted_items = []
        for key, value in details.items():
            if isinstance(value, (dict, list)):
                formatted_items.append(f"{key}={json.dumps(value)}")
            else:
                formatted_items.append(f"{key}={value}")
        
        return ", ".join(formatted_items)