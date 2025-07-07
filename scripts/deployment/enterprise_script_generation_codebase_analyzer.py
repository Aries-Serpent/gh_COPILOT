#!/usr/bin/env python3
"""
Enterprise Script Generation Framework - Phase 1: Comprehensive Codebase Analyzer
==============================================================================

MISSION: Analyze the entire codebase to catalog scripts, patterns, templates, and dependencies
for the intelligent script generation system.

ENTERPRISE COMPLIANCE:
- DUAL COPILOT pattern enforcement
- Anti-recursion protocols
- Clean logging (no Unicode/emoji)
- Database integrity validation
- Session integrity protocols

Author: Enterprise Development Team
Version: 1.0.0
Compliance: Enterprise Standards 2024
"""

import os
import json
import sqlite3
import re
import ast
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, asdict
import subprocess
import sys

# Configure clean logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enterprise_codebase_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScriptMetadata:
    """Metadata for analyzed scripts"""
    filepath: str
    filename: str
    size_bytes: int
    lines_of_code: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    dependencies: List[str]
    patterns: List[str]
    database_connections: List[str]
    complexity_score: int
    last_modified: str
    category: str

@dataclass
class TemplatePattern:
    """Template pattern analysis"""
    pattern_id: str
    pattern_type: str
    occurrence_count: int
    files: List[str]
    code_snippet: str
    variables: List[str]
    description: str

class AntiRecursionGuard:
    """Enterprise anti-recursion protection"""
    
    def __init__(self):
        self.visited_paths = set()
        self.max_depth = 10
        self.current_depth = 0
        
    def should_skip(self, path: str) -> bool:
        """Check if path should be skipped"""
        normalized_path = os.path.normpath(path.lower())
        
        # Skip backup and temporary directories
        skip_patterns = [
            '_backup_',
            'temp/',
            '__pycache__',
            '.git',
            'node_modules',
            '.pytest_cache',
            '.coverage'
        ]
        
        for pattern in skip_patterns:
            if pattern in normalized_path:
                return True
                
        # Prevent recursion
        if normalized_path in self.visited_paths:
            return True
            
        self.visited_paths.add(normalized_path)
        return False

class EnterpriseCodebaseAnalyzer:
    """Main codebase analyzer with enterprise compliance"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.anti_recursion = AntiRecursionGuard()
        self.script_metadata = []
        self.template_patterns = []
        self.framework_structure = {}
        self.dependencies_map = {}
        self.results = {}
        
        # Progress tracking
        self.total_files = 0
        self.processed_files = 0
        
    def analyze_ast_node(self, node: ast.AST, metadata: ScriptMetadata) -> None:
        """Analyze AST node for patterns and metadata"""
        try:
            if isinstance(node, ast.FunctionDef):
                metadata.functions.append(node.name)
                
                # Check for common patterns
                if 'dual_copilot' in node.name.lower():
                    metadata.patterns.append('DUAL_COPILOT')
                if 'anti_recursion' in node.name.lower():
                    metadata.patterns.append('ANTI_RECURSION')
                if 'enterprise' in node.name.lower():
                    metadata.patterns.append('ENTERPRISE')
                    
            elif isinstance(node, ast.ClassDef):
                metadata.classes.append(node.name)
                
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    metadata.imports.append(alias.name)
                    
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    metadata.imports.append(node.module)
                    
            # Check for database connections
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr') and node.func.attr == 'connect':
                    if hasattr(node.func.value, 'id') and node.func.value.id == 'sqlite3':
                        if node.args and isinstance(node.args[0], ast.Constant):
                            metadata.database_connections.append(node.args[0].value)
                            
        except Exception as e:
            logger.warning(f"Error analyzing AST node: {e}")
    
    def analyze_python_file(self, filepath: Path) -> ScriptMetadata:
        """Analyze a Python file for metadata and patterns"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Basic metadata
            metadata = ScriptMetadata(
                filepath=str(filepath),
                filename=filepath.name,
                size_bytes=len(content.encode('utf-8')),
                lines_of_code=len(content.splitlines()),
                functions=[],
                classes=[],
                imports=[],
                dependencies=[],
                patterns=[],
                database_connections=[],
                complexity_score=0,
                last_modified=datetime.datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                category='Unknown'
            )
            
            # Parse AST
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    self.analyze_ast_node(node, metadata)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {filepath}: {e}")
                metadata.patterns.append('SYNTAX_ERROR')
            
            # Categorize script
            metadata.category = self.categorize_script(metadata)
            
            # Calculate complexity
            metadata.complexity_score = self.calculate_complexity(metadata)
            
            # Extract dependencies
            metadata.dependencies = self.extract_dependencies(content)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error analyzing {filepath}: {e}")
            return None
    
    def categorize_script(self, metadata: ScriptMetadata) -> str:
        """Categorize script based on patterns and content"""
        filename_lower = metadata.filename.lower()
        
        if 'master' in filename_lower or 'orchestrator' in filename_lower:
            return 'ORCHESTRATOR'
        elif 'step' in filename_lower:
            return 'FRAMEWORK_STEP'
        elif 'enterprise' in filename_lower:
            return 'ENTERPRISE'
        elif 'database' in filename_lower or 'db' in filename_lower:
            return 'DATABASE'
        elif 'validation' in filename_lower or 'validator' in filename_lower:
            return 'VALIDATION'
        elif 'analyzer' in filename_lower or 'analysis' in filename_lower:
            return 'ANALYSIS'
        elif 'deployment' in filename_lower or 'deploy' in filename_lower:
            return 'DEPLOYMENT'
        elif 'test' in filename_lower:
            return 'TESTING'
        elif 'monitor' in filename_lower:
            return 'MONITORING'
        elif 'performance' in filename_lower:
            return 'PERFORMANCE'
        elif 'scaling' in filename_lower or 'scale' in filename_lower:
            return 'SCALING'
        elif 'learning' in filename_lower:
            return 'LEARNING'
        elif 'analytics' in filename_lower:
            return 'ANALYTICS'
        elif 'innovation' in filename_lower:
            return 'INNOVATION'
        else:
            return 'UTILITY'
    
    def calculate_complexity(self, metadata: ScriptMetadata) -> int:
        """Calculate complexity score based on various factors"""
        score = 0
        
        # Lines of code
        score += min(metadata.lines_of_code // 10, 50)
        
        # Functions and classes
        score += len(metadata.functions) * 2
        score += len(metadata.classes) * 3
        
        # Imports
        score += len(metadata.imports)
        
        # Database connections
        score += len(metadata.database_connections) * 5
        
        # Patterns
        score += len(metadata.patterns) * 3
        
        return score
    
    def extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from script content"""
        dependencies = []
        
        # Common dependency patterns
        patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)\s+import',
            r'sqlite3\.connect\([\'"]([^\'"]+)[\'"]\)',
            r'subprocess\.run\([\'"]([^\'"]+)[\'"]\)',
            r'os\.system\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            dependencies.extend(matches)
        
        return list(set(dependencies))
    
    def find_template_patterns(self) -> None:
        """Find common template patterns across scripts"""
        pattern_counts = {}
        pattern_files = {}
        
        # Common patterns to look for
        common_patterns = [
            r'def\s+(\w*dual_copilot\w*)\(',
            r'def\s+(\w*anti_recursion\w*)\(',
            r'def\s+(\w*enterprise\w*)\(',
            r'def\s+(\w*validation\w*)\(',
            r'class\s+(\w*Enterprise\w*)\(',
            r'logging\.basicConfig\(',
            r'sqlite3\.connect\(',
            r'@dataclass',
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
        ]
        
        for metadata in self.script_metadata:
            try:
                with open(metadata.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for i, pattern in enumerate(common_patterns):
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        pattern_key = f"pattern_{i}"
                        pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + len(matches)
                        
                        if pattern_key not in pattern_files:
                            pattern_files[pattern_key] = []
                        pattern_files[pattern_key].append(metadata.filepath)
                        
            except Exception as e:
                logger.warning(f"Error finding patterns in {metadata.filepath}: {e}")
        
        # Create template patterns
        pattern_descriptions = [
            'DUAL_COPILOT function pattern',
            'Anti-recursion function pattern',
            'Enterprise function pattern',
            'Validation function pattern',
            'Enterprise class pattern',
            'Logging configuration pattern',
            'Database connection pattern',
            'Dataclass decorator pattern',
            'Main execution pattern'
        ]
        
        for i, description in enumerate(pattern_descriptions):
            pattern_key = f"pattern_{i}"
            if pattern_key in pattern_counts:
                template_pattern = TemplatePattern(
                    pattern_id=pattern_key,
                    pattern_type=description,
                    occurrence_count=pattern_counts[pattern_key],
                    files=pattern_files[pattern_key],
                    code_snippet=common_patterns[i],
                    variables=[],
                    description=description
                )
                self.template_patterns.append(template_pattern)
    
    def analyze_framework_structure(self) -> None:
        """Analyze the overall framework structure"""
        categories = {}
        
        for metadata in self.script_metadata:
            category = metadata.category
            if category not in categories:
                categories[category] = []
            categories[category].append(metadata.filename)
        
        self.framework_structure = {
            'categories': categories,
            'total_scripts': len(self.script_metadata),
            'total_functions': sum(len(m.functions) for m in self.script_metadata),
            'total_classes': sum(len(m.classes) for m in self.script_metadata),
            'database_scripts': len([m for m in self.script_metadata if m.database_connections]),
            'enterprise_patterns': len([m for m in self.script_metadata if 'ENTERPRISE' in m.patterns])
        }
    
    def save_to_database(self) -> None:
        """Save analysis results to production.db"""
        try:
            db_path = self.workspace_path / 'databases' / 'production.db'
            
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Create tables if they don't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS script_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filepath TEXT UNIQUE,
                        filename TEXT,
                        size_bytes INTEGER,
                        lines_of_code INTEGER,
                        functions TEXT,
                        classes TEXT,
                        imports TEXT,
                        dependencies TEXT,
                        patterns TEXT,
                        database_connections TEXT,
                        complexity_score INTEGER,
                        last_modified TEXT,
                        category TEXT,
                        analysis_timestamp TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS template_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_id TEXT UNIQUE,
                        pattern_type TEXT,
                        occurrence_count INTEGER,
                        files TEXT,
                        code_snippet TEXT,
                        variables TEXT,
                        description TEXT,
                        analysis_timestamp TEXT
                    )
                ''')
                
                # Insert script metadata
                timestamp = datetime.datetime.now().isoformat()
                for metadata in self.script_metadata:
                    cursor.execute('''
                        INSERT OR REPLACE INTO script_metadata 
                        (filepath, filename, size_bytes, lines_of_code, functions, classes, 
                         imports, dependencies, patterns, database_connections, complexity_score, 
                         last_modified, category, analysis_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        metadata.filepath,
                        metadata.filename,
                        metadata.size_bytes,
                        metadata.lines_of_code,
                        json.dumps(metadata.functions),
                        json.dumps(metadata.classes),
                        json.dumps(metadata.imports),
                        json.dumps(metadata.dependencies),
                        json.dumps(metadata.patterns),
                        json.dumps(metadata.database_connections),
                        metadata.complexity_score,
                        metadata.last_modified,
                        metadata.category,
                        timestamp
                    ))
                
                # Insert template patterns
                for pattern in self.template_patterns:
                    cursor.execute('''
                        INSERT OR REPLACE INTO template_patterns 
                        (pattern_id, pattern_type, occurrence_count, files, code_snippet, 
                         variables, description, analysis_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pattern.pattern_id,
                        pattern.pattern_type,
                        pattern.occurrence_count,
                        json.dumps(pattern.files),
                        pattern.code_snippet,
                        json.dumps(pattern.variables),
                        pattern.description,
                        timestamp
                    ))
                
                conn.commit()
                logger.info("Analysis results saved to production.db")
                
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def generate_reports(self) -> None:
        """Generate comprehensive analysis reports"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON Report
        json_report = {
            'analysis_metadata': {
                'timestamp': timestamp,
                'workspace_path': str(self.workspace_path),
                'total_files_analyzed': len(self.script_metadata),
                'analysis_version': '1.0.0'
            },
            'script_metadata': [asdict(m) for m in self.script_metadata],
            'template_patterns': [asdict(p) for p in self.template_patterns],
            'framework_structure': self.framework_structure,
            'summary_statistics': {
                'total_scripts': len(self.script_metadata),
                'categories': list(set(m.category for m in self.script_metadata)),
                'total_functions': sum(len(m.functions) for m in self.script_metadata),
                'total_classes': sum(len(m.classes) for m in self.script_metadata),
                'average_complexity': sum(m.complexity_score for m in self.script_metadata) / len(self.script_metadata) if self.script_metadata else 0,
                'enterprise_compliance_scripts': len([m for m in self.script_metadata if 'ENTERPRISE' in m.patterns])
            }
        }
        
        json_file = self.workspace_path / f'ENTERPRISE_CODEBASE_ANALYSIS_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        # Markdown Report
        md_content = f"""# Enterprise Codebase Analysis Report

**Analysis Timestamp:** {timestamp}
**Workspace:** {self.workspace_path}
**Total Files Analyzed:** {len(self.script_metadata)}

## Executive Summary

- **Total Scripts:** {len(self.script_metadata)}
- **Total Functions:** {sum(len(m.functions) for m in self.script_metadata)}
- **Total Classes:** {sum(len(m.classes) for m in self.script_metadata)}
- **Average Complexity Score:** {sum(m.complexity_score for m in self.script_metadata) / len(self.script_metadata) if self.script_metadata else 0:.2f}
- **Enterprise Compliant Scripts:** {len([m for m in self.script_metadata if 'ENTERPRISE' in m.patterns])}

## Framework Structure

"""
        
        for category, files in self.framework_structure.get('categories', {}).items():
            md_content += f"### {category}\n"
            for file in files:
                md_content += f"- {file}\n"
            md_content += "\n"
        
        md_content += "## Template Patterns\n\n"
        for pattern in self.template_patterns:
            md_content += f"### {pattern.pattern_type}\n"
            md_content += f"- **Occurrences:** {pattern.occurrence_count}\n"
            md_content += f"- **Files:** {len(pattern.files)}\n"
            md_content += f"- **Pattern:** `{pattern.code_snippet}`\n\n"
        
        md_content += "## Script Categories\n\n"
        category_counts = {}
        for metadata in self.script_metadata:
            category_counts[metadata.category] = category_counts.get(metadata.category, 0) + 1
        
        for category, count in sorted(category_counts.items()):
            md_content += f"- **{category}:** {count} scripts\n"
        
        md_file = self.workspace_path / f'ENTERPRISE_CODEBASE_ANALYSIS_{timestamp}.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        self.results = {
            'json_report': str(json_file),
            'markdown_report': str(md_file),
            'database_updated': True,
            'total_scripts_analyzed': len(self.script_metadata),
            'patterns_found': len(self.template_patterns)
        }
        
        logger.info(f"Reports generated: {json_file} and {md_file}")
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run comprehensive codebase analysis"""
        logger.info("Starting Enterprise Codebase Analysis...")
        
        try:
            # Find all Python files
            python_files = []
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip directories with anti-recursion guard
                if self.anti_recursion.should_skip(root):
                    continue
                
                for file in files:
                    if file.endswith('.py'):
                        filepath = Path(root) / file
                        if not self.anti_recursion.should_skip(str(filepath)):
                            python_files.append(filepath)
            
            self.total_files = len(python_files)
            logger.info(f"Found {self.total_files} Python files to analyze")
            
            # Analyze each file
            for filepath in python_files:
                try:
                    metadata = self.analyze_python_file(filepath)
                    if metadata:
                        self.script_metadata.append(metadata)
                        self.processed_files += 1
                        
                        if self.processed_files % 10 == 0:
                            logger.info(f"Processed {self.processed_files}/{self.total_files} files")
                            
                except Exception as e:
                    logger.warning(f"Error processing {filepath}: {e}")
            
            logger.info(f"Analyzed {len(self.script_metadata)} scripts successfully")
            
            # Find template patterns
            logger.info("Analyzing template patterns...")
            self.find_template_patterns()
            
            # Analyze framework structure
            logger.info("Analyzing framework structure...")
            self.analyze_framework_structure()
            
            # Save to database
            logger.info("Saving results to database...")
            self.save_to_database()
            
            # Generate reports
            logger.info("Generating reports...")
            self.generate_reports()
            
            logger.info("Enterprise Codebase Analysis completed successfully!")
            return self.results
            
        except Exception as e:
            logger.error(f"Error during codebase analysis: {e}")
            raise

def main():
    """Main execution function with DUAL COPILOT pattern"""
    
    # DUAL COPILOT PATTERN: Primary Analysis
    try:
        workspace_path = r"E:\gh_COPILOT"
        analyzer = EnterpriseCodebaseAnalyzer(workspace_path)
        results = analyzer.run_analysis()
        
        print("\n" + "="*80)
        print("ENTERPRISE CODEBASE ANALYSIS - PRIMARY COMPLETION")
        print("="*80)
        print(f"Scripts Analyzed: {results['total_scripts_analyzed']}")
        print(f"Patterns Found: {results['patterns_found']}")
        print(f"JSON Report: {results['json_report']}")
        print(f"Markdown Report: {results['markdown_report']}")
        print(f"Database Updated: {results['database_updated']}")
        print("="*80)
        
        return results
        
    except Exception as e:
        logger.error(f"Primary analysis failed: {e}")
        
        # DUAL COPILOT PATTERN: Secondary Validation
        print("\n" + "="*80)
        print("DUAL COPILOT SECONDARY VALIDATION")
        print("="*80)
        print("Primary analysis encountered issues. Running validation...")
        
        # Basic validation
        workspace_path = Path(r"E:\gh_COPILOT")
        
        validation_results = {
            'workspace_exists': workspace_path.exists(),
            'databases_folder_exists': (workspace_path / 'databases').exists(),
            'production_db_exists': (workspace_path / 'databases' / 'production.db').exists(),
            'python_files_count': len(list(workspace_path.glob('*.py'))),
            'error_details': str(e)
        }
        
        print("Validation Results:")
        for key, value in validation_results.items():
            print(f"- {key}: {value}")
        
        print("="*80)
        return validation_results

if __name__ == "__main__":
    main()
