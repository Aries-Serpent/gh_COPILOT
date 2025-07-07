#!/usr/bin/env python3
"""
Production Database Codebase Analysis - Enterprise Framework
Analyze current script tracking and template capabilities in production.db
"""

import sqlite3
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib
import ast
import re
from tqdm import tqdm

# Enterprise logging setup - ASCII compliant
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_db_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ASCII visual indicators for enterprise compliance
ASCII_EMOJIS = {
    'success': '[OK]',
    'processing': '[>>]',
    'error': '[X]',
    'warning': '[!]',
    'info': '[i]',
    'database': '[DB]',
    'template': '[TPL]',
    'analysis': '[ANA]',
    'code': '[CODE]'
}

@dataclass
class CodebaseMetadata:
    """Metadata for codebase files"""
    filepath: str
    filename: str
    size_bytes: int
    hash_sha256: str
    last_modified: str
    category: str
    complexity_score: float
    dependencies: List[str]
    patterns: List[str]
    is_template_candidate: bool

@dataclass
class DatabaseAnalysisResult:
    """Results of database analysis"""
    total_scripts_in_db: int
    total_scripts_in_filesystem: int
    coverage_percentage: float
    missing_scripts: List[str]
    template_ready_scripts: List[str]
    schema_capabilities: Dict[str, Any]
    recommendations: List[str]

class ProductionDatabaseAnalyzer:
    """Comprehensive production database and codebase analyzer"""
    
    def __init__(self, workspace_root: str = "E:/gh_COPILOT"):
        self.workspace_root = Path(workspace_root)
        self.db_path = self.workspace_root / "databases" / "production.db"
        self.session_id = f"PROD_DB_ANALYSIS_{int(datetime.now().timestamp())}"
        self.start_time = datetime.now()
        
        logger.info(f"{ASCII_EMOJIS['database']} Production Database Analyzer Initialized")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Database: {self.db_path}")
        logger.info(f"Workspace: {self.workspace_root}")
    
    def analyze_database_schema(self) -> Dict[str, Any]:
        """Analyze the current database schema and capabilities"""
        logger.info(f"{ASCII_EMOJIS['analysis']} Analyzing database schema")
        
        schema_info = {
            'tables': {},
            'template_capabilities': {},
            'script_tracking': {},
            'generation_features': {}
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                logger.info(f"{ASCII_EMOJIS['info']} Found {len(tables)} tables in database")
                
                for table in tables:
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    # Get record count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    schema_info['tables'][table] = {
                        'columns': [{'name': col[1], 'type': col[2], 'nullable': not col[3]} for col in columns],
                        'record_count': count
                    }
                
                # Check for template management capabilities
                template_tables = [t for t in tables if 'template' in t.lower()]
                schema_info['template_capabilities'] = {
                    'template_tables': template_tables,
                    'has_template_management': len(template_tables) > 0,
                    'template_storage_ready': 'script_templates' in tables
                }
                
                # Check for script tracking capabilities
                script_tables = [t for t in tables if any(keyword in t.lower() for keyword in ['script', 'generated', 'file'])]
                schema_info['script_tracking'] = {
                    'script_tables': script_tables,
                    'has_script_tracking': len(script_tables) > 0,
                    'file_tracking_ready': any('file' in t.lower() for t in tables)
                }
                
                # Check for generation features
                generation_tables = [t for t in tables if any(keyword in t.lower() for keyword in ['generation', 'session', 'log'])]
                schema_info['generation_features'] = {
                    'generation_tables': generation_tables,
                    'has_generation_tracking': len(generation_tables) > 0,
                    'session_management_ready': 'generation_sessions' in tables
                }
                
        except Exception as e:
            logger.error(f"{ASCII_EMOJIS['error']} Database schema analysis failed: {e}")
            raise
        
        return schema_info
    
    def analyze_filesystem_scripts(self) -> List[CodebaseMetadata]:
        """Analyze all Python scripts in the filesystem"""
        logger.info(f"{ASCII_EMOJIS['code']} Analyzing filesystem scripts")
        
        scripts = []
        python_files = list(self.workspace_root.glob("*.py"))
        
        logger.info(f"{ASCII_EMOJIS['info']} Found {len(python_files)} Python files")
        
        with tqdm(total=len(python_files), desc="Analyzing Scripts", unit="files") as pbar:
            for file_path in python_files:
                try:
                    metadata = self._analyze_script_file(file_path)
                    if metadata:
                        scripts.append(metadata)
                    pbar.update(1)
                except Exception as e:
                    logger.warning(f"{ASCII_EMOJIS['warning']} Failed to analyze {file_path}: {e}")
                    pbar.update(1)
        
        return scripts
    
    def _analyze_script_file(self, file_path: Path) -> Optional[CodebaseMetadata]:
        """Analyze a single script file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate hash
            hash_sha256 = hashlib.sha256(content.encode()).hexdigest()
            
            # Get file stats
            stat = file_path.stat()
            
            # Analyze content
            dependencies = self._extract_dependencies(content)
            patterns = self._extract_patterns(content)
            complexity = self._calculate_complexity(content)
            category = self._categorize_script(file_path.name, content)
            
            # Determine if it's a good template candidate
            is_template_candidate = self._is_template_candidate(content, patterns, complexity)
            
            return CodebaseMetadata(
                filepath=str(file_path),
                filename=file_path.name,
                size_bytes=stat.st_size,
                hash_sha256=hash_sha256,
                last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                category=category,
                complexity_score=complexity,
                dependencies=dependencies,
                patterns=patterns,
                is_template_candidate=is_template_candidate
            )
            
        except Exception as e:
            logger.warning(f"{ASCII_EMOJIS['warning']} Error analyzing {file_path}: {e}")
            return None
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract import dependencies from script content"""
        dependencies = []
        
        # Standard import patterns
        import_patterns = [
            r'^import\s+([^\s#]+)',
            r'^from\s+([^\s#]+)\s+import',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    dep = match.group(1).split('.')[0]
                    if dep not in dependencies:
                        dependencies.append(dep)
        
        return dependencies
    
    def _extract_patterns(self, content: str) -> List[str]:
        """Extract common coding patterns from script content"""
        patterns = []
        
        # Common patterns to look for
        pattern_checks = {
            'class_definition': r'^class\s+\w+',
            'function_definition': r'^def\s+\w+',
            'async_function': r'^async\s+def\s+\w+',
            'decorator': r'^@\w+',
            'context_manager': r'with\s+\w+',
            'exception_handling': r'try:|except\s+\w+:|finally:',
            'logging': r'logger\.|logging\.',
            'database_connection': r'sqlite3\.connect|\.connect\(',
            'json_handling': r'json\.',
            'file_operations': r'open\(|Path\(',
            'dataclass': r'@dataclass',
            'typing_hints': r'->\s*\w+:|:\s*\w+\s*=',
        }
        
        for pattern_name, pattern_regex in pattern_checks.items():
            if re.search(pattern_regex, content, re.MULTILINE):
                patterns.append(pattern_name)
        
        return patterns
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate a simple complexity score for the script"""
        try:
            # Parse AST to count complexity indicators
            tree = ast.parse(content)
            
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For)):
                    complexity += 1
                elif isinstance(node, ast.FunctionDef):
                    complexity += 2
                elif isinstance(node, ast.ClassDef):
                    complexity += 3
                elif isinstance(node, ast.Try):
                    complexity += 1
            
            # Normalize by lines of code
            lines = len([line for line in content.split('\n') if line.strip()])
            return min(100.0, (complexity / max(lines, 1)) * 1000)
            
        except:
            # Fallback: simple line-based complexity
            lines = len([line for line in content.split('\n') if line.strip()])
            return min(100.0, lines / 10)
    
    def _categorize_script(self, filename: str, content: str) -> str:
        """Categorize the script based on name and content"""
        filename_lower = filename.lower()
        
        # Category mapping based on patterns
        if any(keyword in filename_lower for keyword in ['step1', 'step2', 'step3', 'step4', 'step5', 'step6']):
            return 'FRAMEWORK_STEP'
        elif any(keyword in filename_lower for keyword in ['orchestrator', 'master']):
            return 'ORCHESTRATOR'
        elif any(keyword in filename_lower for keyword in ['enterprise', 'production']):
            return 'ENTERPRISE'
        elif any(keyword in filename_lower for keyword in ['database', 'db']):
            return 'DATABASE'
        elif any(keyword in filename_lower for keyword in ['deploy', 'deployment']):
            return 'DEPLOYMENT'
        elif any(keyword in filename_lower for keyword in ['test', 'validation', 'validator']):
            return 'VALIDATION'
        elif any(keyword in filename_lower for keyword in ['util', 'clean', 'fix']):
            return 'UTILITY'
        elif any(keyword in filename_lower for keyword in ['scaling', 'framework']):
            return 'SCALING'
        elif any(keyword in filename_lower for keyword in ['analysis', 'analyzer']):
            return 'ANALYSIS'
        else:
            return 'GENERAL'
    
    def _is_template_candidate(self, content: str, patterns: List[str], complexity: float) -> bool:
        """Determine if a script is a good template candidate"""
        # Good template candidates have:
        # 1. Reasonable complexity (not too simple, not too complex)
        # 2. Common patterns
        # 3. Good structure
        
        if complexity < 20 or complexity > 80:
            return False
        
        required_patterns = ['function_definition', 'logging', 'exception_handling']
        has_required = all(pattern in patterns for pattern in required_patterns)
        
        return has_required and len(patterns) >= 5
    
    def check_database_script_coverage(self, filesystem_scripts: List[CodebaseMetadata]) -> DatabaseAnalysisResult:
        """Check how many filesystem scripts are tracked in the database"""
        logger.info(f"{ASCII_EMOJIS['analysis']} Checking database coverage of filesystem scripts")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if we have script tracking tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%script%'")
                script_tables = [row[0] for row in cursor.fetchall()]
                
                tracked_scripts = set()
                if script_tables:
                    for table in script_tables:
                        try:
                            cursor.execute(f"SELECT DISTINCT filename FROM {table}")
                            for row in cursor.fetchall():
                                tracked_scripts.add(row[0])
                        except:
                            continue
                
                filesystem_filenames = {script.filename for script in filesystem_scripts}
                missing_scripts = list(filesystem_filenames - tracked_scripts)
                coverage_percentage = (len(tracked_scripts) / len(filesystem_filenames)) * 100 if filesystem_filenames else 0
                
                template_ready = [script.filename for script in filesystem_scripts if script.is_template_candidate]
                
                # Get schema capabilities
                schema_info = self.analyze_database_schema()
                
                recommendations = self._generate_recommendations(schema_info, coverage_percentage, len(template_ready))
                
                return DatabaseAnalysisResult(
                    total_scripts_in_db=len(tracked_scripts),
                    total_scripts_in_filesystem=len(filesystem_scripts),
                    coverage_percentage=coverage_percentage,
                    missing_scripts=missing_scripts,
                    template_ready_scripts=template_ready,
                    schema_capabilities=schema_info,
                    recommendations=recommendations
                )
                
        except Exception as e:
            logger.error(f"{ASCII_EMOJIS['error']} Database coverage check failed: {e}")
            raise
    
    def _generate_recommendations(self, schema_info: Dict, coverage: float, template_count: int) -> List[str]:
        """Generate recommendations for improving the system"""
        recommendations = []
        
        if coverage < 80:
            recommendations.append("Implement comprehensive script tracking to improve database coverage")
        
        if not schema_info['template_capabilities']['has_template_management']:
            recommendations.append("Add template management schema for script generation capabilities")
        
        if not schema_info['generation_features']['has_generation_tracking']:
            recommendations.append("Implement generation session tracking for audit and analytics")
        
        if template_count > 10:
            recommendations.append(f"Leverage {template_count} template-ready scripts for automated generation")
        
        recommendations.append("Implement environment-adaptive generation engine")
        recommendations.append("Create GitHub Copilot integration layer")
        recommendations.append("Develop comprehensive template infrastructure")
        
        return recommendations
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        logger.info(f"{ASCII_EMOJIS['processing']} Generating comprehensive analysis report")
        
        # Analyze database schema
        schema_info = self.analyze_database_schema()
        
        # Analyze filesystem scripts
        filesystem_scripts = self.analyze_filesystem_scripts()
        
        # Check coverage
        coverage_result = self.check_database_script_coverage(filesystem_scripts)
        
        # Generate report
        report = {
            'analysis_metadata': {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'workspace_root': str(self.workspace_root),
                'database_path': str(self.db_path),
                'analysis_duration_seconds': (datetime.now() - self.start_time).total_seconds()
            },
            'database_schema': schema_info,
            'filesystem_analysis': {
                'total_scripts': len(filesystem_scripts),
                'categories': self._categorize_scripts(filesystem_scripts),
                'template_candidates': len([s for s in filesystem_scripts if s.is_template_candidate]),
                'average_complexity': sum(s.complexity_score for s in filesystem_scripts) / len(filesystem_scripts) if filesystem_scripts else 0,
                'top_dependencies': self._get_top_dependencies(filesystem_scripts),
                'common_patterns': self._get_common_patterns(filesystem_scripts)
            },
            'coverage_analysis': {
                'database_coverage_percentage': coverage_result.coverage_percentage,
                'scripts_in_database': coverage_result.total_scripts_in_db,
                'scripts_in_filesystem': coverage_result.total_scripts_in_filesystem,
                'missing_scripts_count': len(coverage_result.missing_scripts),
                'template_ready_count': len(coverage_result.template_ready_scripts)
            },
            'recommendations': coverage_result.recommendations,
            'next_steps': [
                'Implement Enhanced Database Schema for template management',
                'Create Filesystem Analysis and Pattern Extraction Engine',
                'Build Template Infrastructure with environment adaptation',
                'Develop Script Generation Engine with GitHub Copilot integration',
                'Create comprehensive documentation and testing suite'
            ],
            'script_details': [
                {
                    'filename': script.filename,
                    'category': script.category,
                    'complexity_score': script.complexity_score,
                    'dependencies': script.dependencies,
                    'patterns': script.patterns,
                    'is_template_candidate': script.is_template_candidate,
                    'size_bytes': script.size_bytes
                }
                for script in filesystem_scripts
            ]
        }
        
        return report
    
    def _categorize_scripts(self, scripts: List[CodebaseMetadata]) -> Dict[str, int]:
        """Categorize scripts by type"""
        categories = {}
        for script in scripts:
            categories[script.category] = categories.get(script.category, 0) + 1
        return categories
    
    def _get_top_dependencies(self, scripts: List[CodebaseMetadata], top_n: int = 10) -> List[Dict[str, Any]]:
        """Get most common dependencies"""
        dep_counts = {}
        for script in scripts:
            for dep in script.dependencies:
                dep_counts[dep] = dep_counts.get(dep, 0) + 1
        
        return [{'dependency': dep, 'count': count} 
                for dep, count in sorted(dep_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]]
    
    def _get_common_patterns(self, scripts: List[CodebaseMetadata], top_n: int = 15) -> List[Dict[str, Any]]:
        """Get most common patterns"""
        pattern_counts = {}
        for script in scripts:
            for pattern in script.patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        return [{'pattern': pattern, 'count': count} 
                for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]]
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """Save the analysis report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        json_file = self.workspace_root / f"PRODUCTION_DB_CODEBASE_ANALYSIS_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Save markdown summary
        md_file = self.workspace_root / f"PRODUCTION_DB_CODEBASE_ANALYSIS_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_summary(report))
        
        logger.info(f"{ASCII_EMOJIS['success']} Analysis reports saved:")
        logger.info(f"  JSON: {json_file}")
        logger.info(f"  Markdown: {md_file}")
        
        return str(json_file)
    
    def _generate_markdown_summary(self, report: Dict[str, Any]) -> str:
        """Generate markdown summary of the analysis"""
        timestamp = report['analysis_metadata']['timestamp']
        
        md_content = f"""# Production Database Codebase Analysis Report

**Generated:** {timestamp}  
**Session ID:** {report['analysis_metadata']['session_id']}  
**Analysis Duration:** {report['analysis_metadata']['analysis_duration_seconds']:.2f} seconds

## Executive Summary

### Database Schema Analysis
- **Total Tables:** {len(report['database_schema']['tables'])}
- **Template Management Ready:** {report['database_schema']['template_capabilities']['has_template_management']}
- **Script Tracking Ready:** {report['database_schema']['script_tracking']['has_script_tracking']}
- **Generation Features:** {report['database_schema']['generation_features']['has_generation_tracking']}

### Filesystem Analysis  
- **Total Scripts:** {report['filesystem_analysis']['total_scripts']}
- **Template Candidates:** {report['filesystem_analysis']['template_candidates']}
- **Average Complexity:** {report['filesystem_analysis']['average_complexity']:.1f}

### Coverage Analysis
- **Database Coverage:** {report['coverage_analysis']['database_coverage_percentage']:.1f}%
- **Scripts in Database:** {report['coverage_analysis']['scripts_in_database']}
- **Scripts in Filesystem:** {report['coverage_analysis']['scripts_in_filesystem']}
- **Missing from Database:** {report['coverage_analysis']['missing_scripts_count']}

## Script Categories
"""
        
        for category, count in report['filesystem_analysis']['categories'].items():
            md_content += f"- **{category}:** {count} scripts\n"
        
        md_content += f"""
## Top Dependencies
"""
        for dep in report['filesystem_analysis']['top_dependencies']:
            md_content += f"- **{dep['dependency']}:** {dep['count']} scripts\n"
        
        md_content += f"""
## Common Patterns
"""
        for pattern in report['filesystem_analysis']['common_patterns']:
            md_content += f"- **{pattern['pattern']}:** {pattern['count']} occurrences\n"
        
        md_content += f"""
## Recommendations
"""
        for rec in report['recommendations']:
            md_content += f"- {rec}\n"
        
        md_content += f"""
## Next Steps
"""
        for step in report['next_steps']:
            md_content += f"1. {step}\n"
        
        return md_content

def main():
    """Main execution function"""
    logger.info(f"{ASCII_EMOJIS['processing']} Starting Production Database Codebase Analysis")
    
    try:
        # Initialize analyzer
        analyzer = ProductionDatabaseAnalyzer()
        
        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report()
        
        # Save report
        report_file = analyzer.save_report(report)
        
        # Print summary
        print("\n" + "="*80)
        print("PRODUCTION DATABASE CODEBASE ANALYSIS - COMPLETED")
        print("="*80)
        print(f"Database Coverage: {report['coverage_analysis']['database_coverage_percentage']:.1f}%")
        print(f"Template Candidates: {report['filesystem_analysis']['template_candidates']}")
        print(f"Total Scripts: {report['filesystem_analysis']['total_scripts']}")
        print(f"Report Saved: {report_file}")
        print("="*80)
        
        logger.info(f"{ASCII_EMOJIS['success']} Production Database Codebase Analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"{ASCII_EMOJIS['error']} Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
