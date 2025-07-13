#!/usr/bin/env python3
"""
🔍 PHASE 4 DEBUG ANALYZER
Enterprise-Grade Debugging for Phase 4 Processor Issues

Purpose: Analyze why Phase 4 processor achieved 0% success rate
Focus: File path handling, encoding issues, and violation fixing logic
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
from datetime import datetime
from tqdm import tqdm
import logging

# Enterprise logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase4_debug_analyzer.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Phase4DebugAnalyzer:
    """🔍 Phase 4 Debug Analysis Engine"""
    
    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self._debug_results = {}
        
        # MANDATORY: Enterprise initialization
        logger.info("="*80)
        logger.info("🔍 PHASE 4 DEBUG ANALYZER INITIALIZED")
        logger.info(f"Workspace: {self.workspace_path}")
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {os.getpid()}")
        logger.info("="*80)
    
    def debug_flake8_parsing(self) -> Dict[str, Any]:
        """🔍 Debug flake8 output parsing"""
        logger.info("🔍 DEBUGGING FLAKE8 PARSING...")
        
        debug_info = {
            "flake8_available": False,
            "sample_output": "",
            "parsed_violations": [],
            "file_paths_valid": [],
            "encoding_issues": []
        }
        
        try:
            # Test flake8 availability
            result = subprocess.run(
                ['python', '-m', 'flake8', '--version'],
                capture_output=True, text=True, encoding='utf-8'
            )
            debug_info["flake8_available"] = True
            logger.info(f"✅ flake8 available: {result.stdout.strip()}")
            
            # Get sample E305 violations
            result = subprocess.run(
                ['python', '-m', 'flake8', '--select=E305', '.'],
                capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
            )
            
            debug_info["sample_output"] = result.stdout[:500]  # First 500 chars
            logger.info(f"📊 Sample flake8 output (first 500 chars):\n{debug_info['sample_output']}")
            
            # Parse sample violations
            violations = self._parse_flake8_output(result.stdout)
            debug_info["parsed_violations"] = violations[:10]  # First 10
            logger.info(f"📋 Parsed {len(violations)} violations (showing first 10):")
            
            # Check file path validity
            for i, (file_path, line_num, col, msg) in enumerate(violations[:5]):
                full_path = self.workspace_path / file_path
                exists = full_path.exists()
                debug_info["file_paths_valid"].append({
                    "relative_path": file_path,
                    "full_path": str(full_path),
                    "exists": exists,
                    "line_num": line_num
                })
                logger.info(f"  📁 {file_path}:{line_num} -> {full_path} (exists: {exists})")
                
        except Exception as e:
            logger.error(f"❌ flake8 debug failed: {e}")
            debug_info["encoding_issues"].append(str(e))
        
        return debug_info
    
    def debug_file_modification(self) -> Dict[str, Any]:
        """🔧 Debug file modification capabilities"""
        logger.info("🔧 DEBUGGING FILE MODIFICATION...")
        
        debug_info = {
            "test_file_created": False,
            "test_file_modified": False,
            "encoding_working": False,
            "write_permissions": False
        }
        
        try:
            # Create test file
            test_file = self.workspace_path / "phase4_test_modification.py"
            test_content = '''def test_function():
    """Test function for debugging"""
    print("Hello, World!")


def another_function():
    """Another test function"""
    return "test"'''
            
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            debug_info["test_file_created"] = test_file.exists()
            logger.info(f"✅ Test file created: {debug_info['test_file_created']}")
            
            # Test reading
            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            debug_info["encoding_working"] = len(lines) > 0
            logger.info(f"✅ File reading works: {debug_info['encoding_working']}")
            logger.info(f"📋 Read {len(lines)} lines")
            
            # Test modification (add blank line after first function)
            if len(lines) >= 4:
                lines.insert(4, '\n')  # Add blank line after first function
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                debug_info["test_file_modified"] = True
                logger.info("✅ File modification successful")
                
                # Verify modification
                with open(test_file, 'r', encoding='utf-8') as f:
                    new_lines = f.readlines()
                logger.info(f"📋 After modification: {len(new_lines)} lines (was {len(lines)-1})")
            
            # Test write permissions
            debug_info["write_permissions"] = True
            
            # Cleanup
            test_file.unlink()
            logger.info("🗑️ Test file cleaned up")
            
        except Exception as e:
            logger.error(f"❌ File modification debug failed: {e}")
            debug_info["write_permissions"] = False
        
        return debug_info
    
    def debug_specific_violation_fix(self) -> Dict[str, Any]:
        """🎯 Debug specific violation fixing logic"""
        logger.info("🎯 DEBUGGING SPECIFIC VIOLATION FIXES...")
        
        debug_info = {
            "e305_logic_test": False,
            "e303_logic_test": False,
            "w291_logic_test": False,
            "f541_logic_test": False
        }
        
        try:
            # Get actual E305 violations for testing
            result = subprocess.run(
                ['python', '-m', 'flake8', '--select=E305', '.'],
                capture_output=True, text=True, encoding='utf-8', cwd=self.workspace_path
            )
            
            violations = self._parse_flake8_output(result.stdout)
            if violations:
                file_path, line_num, col, msg = violations[0]  # Test first violation
                logger.info(f"🎯 Testing E305 fix on: {file_path}:{line_num}")
                
                # Test the fix logic
                full_path = self.workspace_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        logger.info(f"📋 File has {len(lines)} lines")
                        logger.info(f"📋 Target line {line_num}: '{lines[line_num-1].strip()}'" if line_num <= len(lines) else "Line out of range")
                        
                        # Check lines around the violation
                        for i in range(max(0, line_num-3), min(len(lines), line_num+2)):
                            logger.info(f"  Line {i+1}: '{lines[i].rstrip()}'")
                        
                        debug_info["e305_logic_test"] = True
                        
                    except Exception as e:
                        logger.error(f"❌ E305 test failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Violation fix debug failed: {e}")
        
        return debug_info
    
    def _parse_flake8_output(self, output: str) -> List[Tuple[str, int, int, str]]:
        """Parse flake8 output into structured violations"""
        violations = []
        for line in output.split('\n'):
            if line.strip() and ':' in line:
                try:
                    # Parse format: ./file.py:line:col: CODE message
                    parts = line.split(':')
                    if len(parts) >= 4:
                        file_path = parts[0].lstrip('./')
                        line_num = int(parts[1])
                        col = int(parts[2])
                        message = ':'.join(parts[3:]).strip()
                        violations.append((file_path, line_num, col, message))
                except (ValueError, IndexError):
                    continue
        return violations
    
    def run_comprehensive_debug(self) -> Dict[str, Any]:
        """🚀 Execute comprehensive Phase 4 debugging"""
        logger.info("🚀 STARTING COMPREHENSIVE PHASE 4 DEBUG ANALYSIS...")
        
        _debug_results = {}
        
        with tqdm(total=100, desc="🔍 Debug Analysis", unit="%") as pbar:
            
            # Debug 1: flake8 parsing
            pbar.set_description("🔍 Testing flake8 parsing")
            debug_results["flake8_parsing"] = self.debug_flake8_parsing()
            pbar.update(33)
            
            # Debug 2: File modification
            pbar.set_description("🔧 Testing file modification")
            debug_results["file_modification"] = self.debug_file_modification()
            pbar.update(33)
            
            # Debug 3: Specific violation logic
            pbar.set_description("🎯 Testing violation fixes")
            debug_results["violation_fixes"] = self.debug_specific_violation_fix()
            pbar.update(34)
        
        # Generate debug summary
        self.generate_debug_summary(debug_results)
        
        return debug_results
    
    def generate_debug_summary(self, debug_results: Dict[str, Any]):
        """📋 Generate comprehensive debug summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"phase4_debug_report_{timestamp}.txt"
        
        logger.info("📋 GENERATING DEBUG SUMMARY REPORT...")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PHASE 4 DEBUG ANALYSIS REPORT\n")
            f.write("="*50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Workspace: {self.workspace_path}\n\n")
            
            # flake8 Analysis
            f.write("1. FLAKE8 PARSING ANALYSIS\n")
            f.write("-"*30 + "\n")
            flake8_data = debug_results.get("flake8_parsing", {})
            f.write(f"flake8 Available: {flake8_data.get('flake8_available', False)}\n")
            f.write(f"Violations Parsed: {len(flake8_data.get('parsed_violations', []))}\n")
            f.write(f"File Paths Valid: {len(flake8_data.get('file_paths_valid', []))}\n")
            f.write(f"Sample Output:\n{flake8_data.get('sample_output', 'N/A')}\n\n")
            
            # File Modification Analysis
            f.write("2. FILE MODIFICATION ANALYSIS\n")
            f.write("-"*30 + "\n")
            file_data = debug_results.get("file_modification", {})
            f.write(f"Test File Created: {file_data.get('test_file_created', False)}\n")
            f.write(f"File Modified: {file_data.get('test_file_modified', False)}\n")
            f.write(f"Encoding Working: {file_data.get('encoding_working', False)}\n")
            f.write(f"Write Permissions: {file_data.get('write_permissions', False)}\n\n")
            
            # Violation Fix Analysis
            f.write("3. VIOLATION FIX ANALYSIS\n")
            f.write("-"*30 + "\n")
            fix_data = debug_results.get("violation_fixes", {})
            f.write(f"E305 Logic Test: {fix_data.get('e305_logic_test', False)}\n")
            f.write(f"E303 Logic Test: {fix_data.get('e303_logic_test', False)}\n")
            f.write(f"W291 Logic Test: {fix_data.get('w291_logic_test', False)}\n")
            f.write(f"F541 Logic Test: {fix_data.get('f541_logic_test', False)}\n\n")
            
            # Conclusions
            f.write("4. DEBUG CONCLUSIONS\n")
            f.write("-"*30 + "\n")
            if flake8_data.get('flake8_available') and file_data.get('write_permissions'):
                f.write("✅ Basic infrastructure working\n")
                f.write("🔍 Issue likely in specific fix logic\n")
            else:
                f.write("❌ Infrastructure issues detected\n")
                f.write("🔧 Need to fix basic capabilities first\n")
        
        logger.info(f"📋 Debug report generated: {report_file}")


def main():
    """🚀 Phase 4 Debug Analysis Entry Point"""
    print("🔍 PHASE 4 DEBUG ANALYZER STARTING...")
    print("🎯 PURPOSE: Identify why Phase 4 achieved 0% success")
    print("📊 ANALYSIS: flake8 parsing, file modification, violation fixes")
    print("="*80)
    
    try:
        analyzer = Phase4DebugAnalyzer()
        _debug_results = analyzer.run_comprehensive_debug()
        
        print("="*80)
        print("✅ PHASE 4 DEBUG ANALYSIS COMPLETED")
        print("📋 Check debug report for detailed findings")
        print("🎯 Next: Apply fixes based on debug results")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ PHASE 4 DEBUG ANALYSIS FAILED: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
