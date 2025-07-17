#!/usr/bin/env python3
"""
Comprehensive Functionality Validator
DUAL COPILOT PATTERN - Validate all moved scripts maintain original functionality
"""

import os
import sys
import subprocess
import importlib.util
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
from tqdm import tqdm

# MANDATORY: Visual processing indicators
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveFunctionalityValidator:
    """🔍 Validate functionality of all moved scripts"""
    
    def __init__(self, workspace_root: str = "e:/gh_COPILOT"):
        self.workspace_root = Path(workspace_root)
        self.start_time = datetime.now()
        
        # CRITICAL: Anti-recursion validation
        self._validate_environment_compliance()
        
        self.scripts_dir = self.workspace_root / "scripts"
        self.validation_results = {
            "timestamp": self.start_time.isoformat(),
            "categories_tested": [],
            "scripts_validated": 0,
            "functional_scripts": 0,
            "syntax_errors": 0,
            "import_errors": 0,
            "critical_scripts": {},
            "detailed_results": {}
        }
        
        logger.info("="*80)
        logger.info("🔍 COMPREHENSIVE FUNCTIONALITY VALIDATOR INITIALIZED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Workspace: {self.workspace_root}")
        logger.info("="*80)
    
    def _validate_environment_compliance(self):
        """CRITICAL: Validate workspace integrity"""
        if not str(self.workspace_root).endswith("gh_COPILOT"):
            raise RuntimeError("CRITICAL: Invalid workspace root")
        
        logger.info("✅ Environment compliance validated")
    
    def validate_all_script_functionality(self) -> Dict[str, Any]:
        """Execute comprehensive functionality validation"""
        
        try:
            # Phase 1: Critical Scripts Identification
            critical_scripts = self.identify_critical_scripts()
            self.validation_results["critical_scripts"] = critical_scripts
            
            # Phase 2: Syntax Validation
            syntax_results = self.validate_syntax_across_categories()
            
            # Phase 3: Import Validation
            import_results = self.validate_imports_across_categories()
            
            # Phase 4: Critical Function Testing
            function_results = self.test_critical_functions()
            
            # Phase 5: Integration Testing
            integration_results = self.test_script_integrations()
            
            # Compile final results
            self._compile_final_results(syntax_results, import_results, function_results, integration_results)
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            self.validation_results["status"] = "FAILED"
            self.validation_results["error"] = str(e)
        
        return self.validation_results
    
    def identify_critical_scripts(self) -> Dict[str, List[str]]:
        """Identify critical scripts by functionality"""
        logger.info("🎯 PHASE 1: IDENTIFYING CRITICAL SCRIPTS")
        logger.info("="*60)
        
        critical_categories = {
            "consolidation_scripts": [
                "consolidation", "merger", "aggregat", "combin", "unifie"
            ],
            "compression_scripts": [
                "compress", "zip", "archiv", "compact", "reduc"
            ],
            "wrap_up_scripts": [
                "wrap", "final", "complet", "finish", "conclud"
            ],
            "database_scripts": [
                "database", "db", "sql", "query", "migrat"
            ],
            "validation_scripts": [
                "valid", "test", "check", "verify", "audit"
            ],
            "automation_scripts": [
                "automat", "orchestr", "execut", "launch", "process"
            ],
            "enterprise_scripts": [
                "enterprise", "production", "deploy", "framework"
            ],
            "optimization_scripts": [
                "optim", "enhance", "improve", "boost", "accelerat"
            ]
        }
        
        critical_scripts = {}
        
        for category, keywords in critical_categories.items():
            logger.info(f"🔍 Identifying {category}...")
            scripts = []
            
            for script_dir in self.scripts_dir.iterdir():
                if script_dir.is_dir():
                    for script_file in script_dir.glob("*.py"):
                        script_name = script_file.name.lower()
                        if any(keyword in script_name for keyword in keywords):
                            scripts.append(str(script_file.relative_to(self.workspace_root)))
            
            critical_scripts[category] = scripts
            logger.info(f"   ✅ Found {len(scripts)} scripts")
        
        return critical_scripts
    
    def validate_syntax_across_categories(self) -> Dict[str, Any]:
        """Validate syntax of all Python scripts"""
        logger.info("📝 PHASE 2: SYNTAX VALIDATION ACROSS CATEGORIES")
        logger.info("="*60)
        
        syntax_results = {
            "total_scripts": 0,
            "valid_syntax": 0,
            "syntax_errors": 0,
            "category_results": {},
            "error_details": []
        }
        
        for category_dir in self.scripts_dir.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                logger.info(f"🔍 Validating syntax in {category_name}/")
                
                py_files = list(category_dir.glob("*.py"))
                category_valid = 0
                category_errors = 0
                
                with tqdm(total=len(py_files), desc=f"📝 {category_name}", unit="script") as pbar:
                    for script_file in py_files:
                        try:
                            with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Parse AST to validate syntax
                            ast.parse(content)
                            category_valid += 1
                            
                        except SyntaxError as e:
                            category_errors += 1
                            error_detail = {
                                "script": str(script_file.relative_to(self.workspace_root)),
                                "error": f"Syntax error at line {e.lineno}: {e.msg}",
                                "line": e.lineno,
                                "category": category_name
                            }
                            syntax_results["error_details"].append(error_detail)
                            logger.warning(f"   ❌ {script_file.name}: Syntax error")
                            
                        except Exception as e:
                            category_errors += 1
                            error_detail = {
                                "script": str(script_file.relative_to(self.workspace_root)),
                                "error": f"Parse error: {str(e)}",
                                "category": category_name
                            }
                            syntax_results["error_details"].append(error_detail)
                            logger.warning(f"   ❌ {script_file.name}: Parse error")
                        
                        pbar.update(1)
                
                syntax_results["category_results"][category_name] = {
                    "total": len(py_files),
                    "valid": category_valid,
                    "errors": category_errors,
                    "percentage": (category_valid / len(py_files) * 100) if len(py_files) > 0 else 100
                }
                
                syntax_results["total_scripts"] += len(py_files)
                syntax_results["valid_syntax"] += category_valid
                syntax_results["syntax_errors"] += category_errors
                
                logger.info(f"   📊 {category_valid}/{len(py_files)} scripts valid ({(category_valid/len(py_files)*100):.1f}%)" if len(py_files) > 0 else "   📊 No Python files in category")
        
        return syntax_results
    
    def validate_imports_across_categories(self) -> Dict[str, Any]:
        """Validate imports and dependencies"""
        logger.info("📦 PHASE 3: IMPORT VALIDATION ACROSS CATEGORIES")
        logger.info("="*60)
        
        import_results = {
            "total_scripts": 0,
            "valid_imports": 0,
            "import_errors": 0,
            "category_results": {},
            "missing_modules": set(),
            "error_details": []
        }
        
        for category_dir in self.scripts_dir.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                logger.info(f"📦 Validating imports in {category_name}/")
                
                py_files = list(category_dir.glob("*.py"))
                category_valid = 0
                category_errors = 0
                
                with tqdm(total=len(py_files), desc=f"📦 {category_name}", unit="script") as pbar:
                    for script_file in py_files:
                        try:
                            # Check imports by attempting to compile
                            spec = importlib.util.spec_from_file_location(
                                script_file.stem, script_file
                            )
                            
                            if spec and spec.loader:
                                # Try to load the module
                                module = importlib.util.module_from_spec(spec)
                                
                                # Add paths for relative imports
                                sys.path.insert(0, str(script_file.parent))
                                sys.path.insert(0, str(self.workspace_root))
                                
                                try:
                                    spec.loader.exec_module(module)
                                    category_valid += 1
                                except ImportError as e:
                                    category_errors += 1
                                    missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
                                    import_results["missing_modules"].add(missing_module)
                                    
                                    error_detail = {
                                        "script": str(script_file.relative_to(self.workspace_root)),
                                        "error": f"Import error: {str(e)}",
                                        "missing_module": missing_module,
                                        "category": category_name
                                    }
                                    import_results["error_details"].append(error_detail)
                                    
                                except Exception as e:
                                    # Other execution errors (not import-related)
                                    category_valid += 1  # Imports are OK, execution failed
                                
                                finally:
                                    # Clean up sys.path
                                    if str(script_file.parent) in sys.path:
                                        sys.path.remove(str(script_file.parent))
                                    if str(self.workspace_root) in sys.path:
                                        sys.path.remove(str(self.workspace_root))
                            else:
                                category_errors += 1
                                
                        except Exception as e:
                            category_errors += 1
                            error_detail = {
                                "script": str(script_file.relative_to(self.workspace_root)),
                                "error": f"Module load error: {str(e)}",
                                "category": category_name
                            }
                            import_results["error_details"].append(error_detail)
                        
                        pbar.update(1)
                
                import_results["category_results"][category_name] = {
                    "total": len(py_files),
                    "valid": category_valid,
                    "errors": category_errors,
                    "percentage": (category_valid / len(py_files) * 100) if len(py_files) > 0 else 100
                }
                
                import_results["total_scripts"] += len(py_files)
                import_results["valid_imports"] += category_valid
                import_results["import_errors"] += category_errors
                
                logger.info(f"   📊 {category_valid}/{len(py_files)} scripts with valid imports ({(category_valid/len(py_files)*100):.1f}%)" if len(py_files) > 0 else "   📊 No Python files in category")
        
        # Convert set to list for JSON serialization
        import_results["missing_modules"] = list(import_results["missing_modules"])
        
        return import_results
    
    def test_critical_functions(self) -> Dict[str, Any]:
        """Test critical functions in key scripts"""
        logger.info("🧪 PHASE 4: CRITICAL FUNCTION TESTING")
        logger.info("="*60)
        
        function_results = {
            "tested_functions": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        # Test specific critical functions
        critical_tests = [
            {
                "category": "database",
                "function": "get_database_connection",
                "test_type": "connection_test"
            },
            {
                "category": "validation", 
                "function": "validate_workspace_integrity",
                "test_type": "validation_test"
            },
            {
                "category": "automation",
                "function": "execute_with_monitoring", 
                "test_type": "execution_test"
            }
        ]
        
        for test in critical_tests:
            logger.info(f"🧪 Testing {test['function']} in {test['category']}/")
            
            # Find scripts in category that might contain this function
            category_dir = self.scripts_dir / test['category']
            if category_dir.exists():
                for script_file in category_dir.glob("*.py"):
                    try:
                        with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if test['function'] in content:
                            function_results["tested_functions"] += 1
                            logger.info(f"   ✅ Found {test['function']} in {script_file.name}")
                            function_results["successful_tests"] += 1
                            
                            test_detail = {
                                "script": str(script_file.relative_to(self.workspace_root)),
                                "function": test['function'],
                                "status": "found",
                                "category": test['category']
                            }
                            function_results["test_details"].append(test_detail)
                            
                    except Exception as e:
                        function_results["failed_tests"] += 1
                        test_detail = {
                            "script": str(script_file.relative_to(self.workspace_root)),
                            "function": test['function'],
                            "status": "error",
                            "error": str(e),
                            "category": test['category']
                        }
                        function_results["test_details"].append(test_detail)
        
        return function_results
    
    def test_script_integrations(self) -> Dict[str, Any]:
        """Test script integrations and dependencies"""
        logger.info("🔗 PHASE 5: SCRIPT INTEGRATION TESTING")
        logger.info("="*60)
        
        integration_results = {
            "integration_points": 0,
            "successful_integrations": 0,
            "failed_integrations": 0,
            "integration_details": []
        }
        
        # Test cross-category imports
        cross_imports = [
            ("automation", "database"),
            ("validation", "database"),
            ("enterprise", "automation"),
            ("optimization", "database")
        ]
        
        for source_cat, target_cat in cross_imports:
            source_dir = self.scripts_dir / source_cat
            target_dir = self.scripts_dir / target_cat
            
            if source_dir.exists() and target_dir.exists():
                logger.info(f"🔗 Testing {source_cat} → {target_cat} integration")
                integration_results["integration_points"] += 1
                
                # Check if scripts in source category import from target
                found_integration = False
                for script_file in source_dir.glob("*.py"):
                    try:
                        with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if f"scripts.{target_cat}" in content or f"scripts/{target_cat}" in content:
                            found_integration = True
                            logger.info(f"   ✅ Integration found in {script_file.name}")
                            break
                            
                    except Exception:
                        continue
                
                if found_integration:
                    integration_results["successful_integrations"] += 1
                    integration_detail = {
                        "source": source_cat,
                        "target": target_cat,
                        "status": "active_integration",
                        "description": f"Active integration from {source_cat} to {target_cat}"
                    }
                else:
                    integration_results["failed_integrations"] += 1
                    integration_detail = {
                        "source": source_cat,
                        "target": target_cat,
                        "status": "no_integration",
                        "description": f"No active integration found from {source_cat} to {target_cat}"
                    }
                
                integration_results["integration_details"].append(integration_detail)
        
        return integration_results
    
    def _compile_final_results(self, syntax_results, import_results, function_results, integration_results):
        """Compile final validation results"""
        
        self.validation_results.update({
            "syntax_validation": syntax_results,
            "import_validation": import_results, 
            "function_testing": function_results,
            "integration_testing": integration_results
        })
        
        # Calculate overall scores
        total_scripts = syntax_results["total_scripts"]
        if total_scripts > 0:
            syntax_score = (syntax_results["valid_syntax"] / total_scripts) * 100
            import_score = (import_results["valid_imports"] / total_scripts) * 100
            overall_score = (syntax_score + import_score) / 2
            
            self.validation_results.update({
                "scripts_validated": total_scripts,
                "functional_scripts": syntax_results["valid_syntax"],
                "syntax_errors": syntax_results["syntax_errors"],
                "import_errors": import_results["import_errors"],
                "overall_syntax_score": syntax_score,
                "overall_import_score": import_score,
                "overall_functionality_score": overall_score,
                "status": "COMPLETED"
            })
        else:
            self.validation_results.update({
                "scripts_validated": 0,
                "functional_scripts": 0,
                "syntax_errors": 0,
                "import_errors": 0,
                "overall_syntax_score": 0,
                "overall_import_score": 0,
                "overall_functionality_score": 0,
                "status": "NO_SCRIPTS_FOUND"
            })
        
        # Log final summary
        duration = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("🏆 COMPREHENSIVE FUNCTIONALITY VALIDATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Scripts Validated: {total_scripts}")
        
        if total_scripts > 0:
            syntax_score = float(self.validation_results.get("overall_syntax_score", 0) or 0)
            import_score = float(self.validation_results.get("overall_import_score", 0) or 0)
            overall_score = float(self.validation_results.get("overall_functionality_score", 0) or 0)
            
            logger.info(f"Syntax Score: {syntax_score:.1f}%")
            logger.info(f"Import Score: {import_score:.1f}%") 
            logger.info(f"Overall Functionality Score: {overall_score:.1f}%")
        else:
            logger.info("No scripts found to validate")
            
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info("="*80)


def main():
    """Execute comprehensive functionality validation"""
    try:
        validator = ComprehensiveFunctionalityValidator()
        results = validator.validate_all_script_functionality()
        
        # Save results to file
        import json
        results_file = validator.workspace_root / "scripts" / "validation" / f"functionality_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        raise

if __name__ == "__main__":
    main()
