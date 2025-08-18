#!/usr/bin/env python3
"""
COMPREHENSIVE MODULAR ANALYSIS ENGINE
=====================================

MISSION: Analyze all root-level scripts to identify common functionalities
that can be modularized for reuse across similar scripts, reducing monolithic
code and improving maintainability.

Based on: Completed Phase 1-3 modularization achievements
Target: Identify and consolidate similar functionalities across all scripts
"""

import ast
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import os
import sys
from dataclasses import dataclass, field

# Visual processing indicators
from tqdm import tqdm


@dataclass
class FunctionPattern:
    """Represents a function pattern for analysis"""

    name: str
    signature: str
    ast_hash: str
    file_path: str
    complexity_score: int = 0
    imports_used: List[str] = field(default_factory=list)
    functionality_category: str = ""
    similar_functions: List[str] = field(default_factory=list)


@dataclass
class ModularizationOpportunity:
    """Represents an opportunity for modularization"""

    pattern_type: str
    affected_scripts: List[str]
    common_functionality: str
    estimated_savings: int
    consolidation_strategy: str
    complexity_level: str
    recommended_module: str


class ComprehensiveModularAnalysisEngine:
    """🔧 Advanced script analysis for modularization opportunities"""

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.start_time = datetime.now()

        # Setup logging with visual indicators
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Initialize analysis structures
        self.function_patterns = {}
        self.import_patterns = defaultdict(list)
        self.class_patterns = {}
        self.modularization_opportunities = []

        # Database connection for intelligence
        self.db_path = self.workspace_path / "production.db"

        self.logger.info("🔧 COMPREHENSIVE MODULAR ANALYSIS ENGINE INITIALIZED")
        self.logger.info(f"⏰ Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"📁 Workspace: {self.workspace_path}")

    def analyze_all_root_scripts(self) -> Dict[str, Any]:
        """📊 Analyze all Python scripts in the root directory"""

        self.logger.info("🚀 STARTING COMPREHENSIVE SCRIPT ANALYSIS")

        # Get all Python files in root
        python_files = [f for f in self.workspace_path.glob("*.py") if f.is_file() and not f.name.startswith(".")]

        total_files = len(python_files)
        self.logger.info(f"📁 Found {total_files} Python scripts to analyze")

        analysis_results = {
            "total_scripts_analyzed": 0,
            "function_patterns_identified": 0,
            "import_patterns_found": 0,
            "class_patterns_discovered": 0,
            "modularization_opportunities": 0,
            "estimated_total_savings": 0,
            "analysis_timestamp": self.start_time.isoformat(),
            "detailed_patterns": {},
            "consolidation_recommendations": [],
        }

        # Analyze each script with progress tracking
        with tqdm(total=100, desc="🔧 Script Analysis", unit="%") as pbar:
            for i, script_path in enumerate(python_files):
                try:
                    pbar.set_description(f"🔍 Analyzing {script_path.name}")

                    script_analysis = self.analyze_single_script(script_path)
                    analysis_results["detailed_patterns"][str(script_path)] = script_analysis

                    # Update progress
                    progress = ((i + 1) / total_files) * 80  # 80% for script analysis
                    pbar.update(progress - pbar.n)

                except (OSError, SyntaxError):
                    logging.exception("analysis script error")
                    raise

            pbar.set_description("🧠 Identifying modularization opportunities")
            self.identify_modularization_opportunities()
            pbar.update(10)  # 90% total

            pbar.set_description("📋 Generating recommendations")
            self.generate_consolidation_recommendations()
            pbar.update(10)  # 100% total

        # Update final results
        analysis_results.update(
            {
                "total_scripts_analyzed": len(analysis_results["detailed_patterns"]),
                "function_patterns_identified": len(self.function_patterns),
                "import_patterns_found": len(self.import_patterns),
                "class_patterns_discovered": len(self.class_patterns),
                "modularization_opportunities": len(self.modularization_opportunities),
                "estimated_total_savings": sum(op.estimated_savings for op in self.modularization_opportunities),
                "consolidation_recommendations": [
                    {
                        "pattern_type": op.pattern_type,
                        "affected_scripts": op.affected_scripts,
                        "common_functionality": op.common_functionality,
                        "estimated_savings": op.estimated_savings,
                        "consolidation_strategy": op.consolidation_strategy,
                        "recommended_module": op.recommended_module,
                    }
                    for op in self.modularization_opportunities
                ],
            }
        )

        # Log comprehensive results
        self.logger.info("=" * 80)
        self.logger.info("📊 COMPREHENSIVE MODULAR ANALYSIS COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"✅ Scripts Analyzed: {analysis_results['total_scripts_analyzed']}")
        self.logger.info(f"🔧 Function Patterns: {analysis_results['function_patterns_identified']}")
        self.logger.info(f"📦 Import Patterns: {analysis_results['import_patterns_found']}")
        self.logger.info(f"🏗️ Class Patterns: {analysis_results['class_patterns_discovered']}")
        self.logger.info(f"💡 Modularization Opportunities: {analysis_results['modularization_opportunities']}")
        self.logger.info(f"💾 Estimated Total Savings: {analysis_results['estimated_total_savings']} lines")

        return analysis_results

    def analyze_single_script(self, script_path: Path) -> Dict[str, Any]:
        """🔍 Analyze a single script for patterns"""

        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Extract patterns
            functions = self.extract_function_patterns(tree, script_path)
            classes = self.extract_class_patterns(tree, script_path)
            imports = self.extract_import_patterns(tree, script_path)

            # Calculate complexity
            complexity = self.calculate_script_complexity(tree)

            return {
                "file_size_lines": len(content.splitlines()),
                "functions_found": len(functions),
                "classes_found": len(classes),
                "imports_found": len(imports),
                "complexity_score": complexity,
                "function_patterns": functions,
                "class_patterns": classes,
                "import_patterns": imports,
            }

        except (OSError, SyntaxError):
            logging.exception("analysis script error")
            raise

    def extract_function_patterns(self, tree: ast.AST, script_path: Path) -> List[Dict[str, Any]]:
        """🔧 Extract function patterns from AST"""

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Generate function signature
                args = [arg.arg for arg in node.args.args]
                signature = f"{node.name}({', '.join(args)})"

                # Generate AST hash for similarity comparison
                ast_dump = ast.dump(node)
                ast_hash = hashlib.md5(ast_dump.encode()).hexdigest()[:16]

                # Categorize function
                category = self.categorize_function(node.name, args)

                function_pattern = {
                    "name": node.name,
                    "signature": signature,
                    "ast_hash": ast_hash,
                    "line_count": getattr(node, "end_lineno", 0) - getattr(node, "lineno", 0),
                    "category": category,
                    "has_docstring": ast.get_docstring(node) is not None,
                    "argument_count": len(args),
                }

                functions.append(function_pattern)

                # Store in global patterns
                pattern_key = f"{category}_{node.name}"
                if pattern_key not in self.function_patterns:
                    self.function_patterns[pattern_key] = []
                self.function_patterns[pattern_key].append({"script": str(script_path), "pattern": function_pattern})

        return functions

    def extract_class_patterns(self, tree: ast.AST, script_path: Path) -> List[Dict[str, Any]]:
        """🏗️ Extract class patterns from AST"""

        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get methods
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

                # Get base classes
                bases = [ast.unparse(base) if hasattr(ast, "unparse") else "Unknown" for base in node.bases]

                class_pattern = {
                    "name": node.name,
                    "methods": methods,
                    "method_count": len(methods),
                    "base_classes": bases,
                    "has_docstring": ast.get_docstring(node) is not None,
                    "complexity": len(node.body),
                }

                classes.append(class_pattern)

                # Store in global patterns
                if node.name not in self.class_patterns:
                    self.class_patterns[node.name] = []
                self.class_patterns[node.name].append({"script": str(script_path), "pattern": class_pattern})

        return classes

    def extract_import_patterns(self, tree: ast.AST, script_path: Path) -> List[str]:
        """📦 Extract import patterns from AST"""

        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
                    self.import_patterns[alias.name].append(str(script_path))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        import_name = f"{node.module}.{alias.name}"
                        imports.append(import_name)
                        self.import_patterns[import_name].append(str(script_path))

        return imports

    def categorize_function(self, function_name: str, args: List[str]) -> str:
        """📋 Categorize function based on name and signature"""

        name_lower = function_name.lower()

        # Database operations
        if any(pattern in name_lower for pattern in ["database", "db", "sql", "query", "connection"]):
            return "database_operations"

        # File operations
        elif any(pattern in name_lower for pattern in ["file", "read", "write", "save", "load", "path"]):
            return "file_operations"

        # Validation operations
        elif any(pattern in name_lower for pattern in ["validate", "verify", "check", "ensure", "confirm"]):
            return "validation_operations"

        # Analysis operations
        elif any(pattern in name_lower for pattern in ["analyze", "process", "parse", "extract", "transform"]):
            return "analysis_operations"

        # Optimization operations
        elif any(pattern in name_lower for pattern in ["optimize", "enhance", "improve", "performance"]):
            return "optimization_operations"

        # Monitoring operations
        elif any(pattern in name_lower for pattern in ["monitor", "track", "log", "watch", "observe"]):
            return "monitoring_operations"

        # Configuration operations
        elif any(pattern in name_lower for pattern in ["config", "setup", "init", "configure"]):
            return "configuration_operations"

        # Reporting operations
        elif any(pattern in name_lower for pattern in ["report", "generate", "create", "build"]):
            return "reporting_operations"

        # Utility operations
        elif any(pattern in name_lower for pattern in ["util", "helper", "common", "shared"]):
            return "utility_operations"

        # Error handling
        elif any(pattern in name_lower for pattern in ["error", "exception", "handle", "catch"]):
            return "error_handling"

        else:
            return "general_operations"

    def calculate_script_complexity(self, tree: ast.AST) -> int:
        """📊 Calculate script complexity score"""

        node_count = len(list(ast.walk(tree)))
        function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

        # Complexity formula
        complexity = node_count + (function_count * 2) + (class_count * 3)
        return complexity

    def identify_modularization_opportunities(self):
        """💡 Identify opportunities for modularization"""

        self.logger.info("🧠 Analyzing patterns for modularization opportunities...")

        # Analyze function patterns
        for pattern_key, occurrences in self.function_patterns.items():
            if len(occurrences) >= 2:  # Function appears in multiple scripts
                category, function_name = pattern_key.split("_", 1)

                affected_scripts = [occ["script"] for occ in occurrences]
                estimated_savings = sum(occ["pattern"]["line_count"] for occ in occurrences) - 20

                opportunity = ModularizationOpportunity(
                    pattern_type="function_consolidation",
                    affected_scripts=affected_scripts,
                    common_functionality=f"{function_name} ({category})",
                    estimated_savings=max(estimated_savings, 0),
                    consolidation_strategy="extract_to_module",
                    complexity_level="LOW" if len(occurrences) <= 3 else "MEDIUM",
                    recommended_module=f"{category}_utils",
                )

                self.modularization_opportunities.append(opportunity)

        # Analyze class patterns
        for class_name, occurrences in self.class_patterns.items():
            if len(occurrences) >= 2:  # Class appears in multiple scripts
                affected_scripts = [occ["script"] for occ in occurrences]
                estimated_savings = sum(occ["pattern"]["complexity"] for occ in occurrences) * 5

                opportunity = ModularizationOpportunity(
                    pattern_type="class_consolidation",
                    affected_scripts=affected_scripts,
                    common_functionality=f"{class_name} class definition",
                    estimated_savings=estimated_savings,
                    consolidation_strategy="extract_to_base_module",
                    complexity_level="MEDIUM",
                    recommended_module="shared_classes",
                )

                self.modularization_opportunities.append(opportunity)

        # Analyze import patterns
        common_imports = {imp: scripts for imp, scripts in self.import_patterns.items() if len(scripts) >= 3}

        if common_imports:
            opportunity = ModularizationOpportunity(
                pattern_type="import_consolidation",
                affected_scripts=list(set(script for scripts in common_imports.values() for script in scripts)),
                common_functionality="Common import dependencies",
                estimated_savings=len(common_imports) * 5,
                consolidation_strategy="create_import_module",
                complexity_level="LOW",
                recommended_module="common_imports",
            )

            self.modularization_opportunities.append(opportunity)

    def generate_consolidation_recommendations(self):
        """📋 Generate specific consolidation recommendations"""

        self.logger.info("📋 Generating consolidation recommendations...")

        # Sort opportunities by estimated savings
        self.modularization_opportunities.sort(key=lambda x: x.estimated_savings, reverse=True)

        # Log top opportunities
        for i, opportunity in enumerate(self.modularization_opportunities[:10], 1):
            self.logger.info(f"💡 Opportunity {i}: {opportunity.common_functionality}")
            self.logger.info(f"   📁 Affects {len(opportunity.affected_scripts)} scripts")
            self.logger.info(f"   💾 Estimated savings: {opportunity.estimated_savings} lines")
            self.logger.info(f"   📦 Recommended module: {opportunity.recommended_module}")

    def save_analysis_results(self, results: Dict[str, Any]) -> str:
        """💾 Save analysis results to JSON file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.workspace_path / f"modular_analysis_results_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        self.logger.info(f"💾 Analysis results saved to: {output_file}")
        return str(output_file)


def main():
    """🎯 Main execution function"""

    # MANDATORY: Visual processing indicators
    start_time = datetime.now()
    print("=" * 80)
    print("🔧 COMPREHENSIVE MODULAR ANALYSIS ENGINE")
    print("=" * 80)
    print(f"🚀 Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Target: Root-level script modularization analysis")
    print("=" * 80)

    # Initialize analyzer
    analyzer = ComprehensiveModularAnalysisEngine()

    # Perform comprehensive analysis
    results = analyzer.analyze_all_root_scripts()

    # Save results
    output_file = analyzer.save_analysis_results(results)

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    print("=" * 80)
    print("✅ COMPREHENSIVE MODULAR ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"⏰ Total Duration: {duration:.2f} seconds")
    print(f"📊 Scripts Analyzed: {results['total_scripts_analyzed']}")
    print(f"💡 Modularization Opportunities: {results['modularization_opportunities']}")
    print(f"💾 Estimated Total Savings: {results['estimated_total_savings']} lines")
    print(f"📄 Results File: {output_file}")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
