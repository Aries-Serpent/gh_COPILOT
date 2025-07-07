#!/usr/bin/env python3
"""
Enterprise Script Generation Framework
DUAL COPILOT Pattern Implementation - Primary Executor
Anti-Recursion Protected Intelligent Code Generation System

This framework transforms the production.db file tracking system into an intelligent,
adaptive script generation platform with enterprise compliance and GitHub Copilot integration.

Features:
- Comprehensive codebase analysis and pattern extraction
- Environment-adaptive script generation
- Template management with effectiveness tracking
- GitHub Copilot integration layer
- Enterprise compliance validation
"""

import sqlite3
import json
import os
import sys
import ast
import hashlib
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
import concurrent.futures
from tqdm import tqdm
import logging
import time

@dataclass
class ScriptTemplate:
    """Enterprise script template with metadata and adaptation capabilities"""
    template_id: str
    template_name: str
    template_category: str
    template_content: str
    template_metadata: Dict[str, Any]
    environment_variants: Dict[str, str]
    success_patterns: List[str]
    complexity_score: float
    usage_frequency: int = 0
    effectiveness_score: float = 0.0

@dataclass
class CodebaseAnalysis:
    """Comprehensive analysis results of existing codebase"""
    total_scripts_analyzed: int
    patterns_extracted: List[str]
    template_candidates: List[ScriptTemplate]
    dependency_graph: Dict[str, List[str]]
    complexity_metrics: Dict[str, float]
    enterprise_compliance_score: float
    analysis_timestamp: str

@dataclass
class EnvironmentContext:
    """Environment-specific configuration and adaptation context"""
    environment_name: str
    environment_type: str
    python_version: str
    workspace_path: str
    database_paths: List[str]
    configuration_data: Dict[str, Any]
    deployment_patterns: List[str]
    validation_rules: List[str]

@dataclass
class GeneratedScript:
    """Generated script with metadata and validation results"""
    script_id: str
    template_id: str
    generated_content: str
    environment_context: EnvironmentContext
    generation_parameters: Dict[str, Any]
    validation_results: Dict[str, bool]
    estimated_success_rate: float
    generation_timestamp: str

class EnterpriseScriptGenerator:
    """
    Primary Executor: Intelligent script generation with environment adaptation
    MANDATORY: Visual processing indicators and anti-recursion validation
    """
    
    def __init__(self, production_db_path: str = "databases/production.db"):
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.session_id = f"SCRIPT_GEN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Setup logging with ASCII-safe output
        self.setup_enterprise_logging()
        
        self.logger.info("[LAUNCH] ENTERPRISE SCRIPT GENERATION FRAMEWORK STARTING")
        self.logger.info(f"Session ID: {self.session_id}")
        self.logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Process ID: {self.process_id}")
        
        # CRITICAL: Anti-recursion validation at startup
        self.validate_enterprise_environment()
        
        # Initialize core components
        self.production_db_path = Path(production_db_path)
        self.workspace_path = Path("E:/gh_COPILOT")
        self.template_cache = {}
        self.analysis_cache = {}
        
        # Initialize database connections
        self.setup_database_connections()
        
        # Initialize framework components
        self.template_manager = TemplateManager(self.production_db_path)
        self.environment_adapter = EnvironmentAdapter()
        self.compliance_validator = EnterpriseComplianceValidator()
        
        self.logger.info("[SUCCESS] Enterprise Script Generation Framework initialized successfully")

    def setup_enterprise_logging(self):
        """Setup enterprise-compliant logging with visual indicators"""
        log_file = f"enterprise_script_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='ascii', errors='ignore'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate_enterprise_environment(self):
        """Enhanced anti-recursion validation with enterprise compliance"""
        self.logger.info("[SEARCH] CRITICAL: Validating enterprise environment integrity")
        
        # Anti-recursion patterns validation
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups']
        violations = []
        
        # Allowed enterprise directories
        allowed_dirs = {
            'databases', 'database_backups', 'database_test_results', 
            'migration_sync_test_results', 'temp', 'logs', 'config', 
            'scripts', 'src', 'validation'
        }
        
        # ENTERPRISE EXCEPTION: Allow specific backup directories created by validation tools
        enterprise_backup_exceptions = [
            '_backup_deployed_fixes_',
            '_backup_database_organization_',
            '_backup_unicode_cleanup_',
            'database_backups',
            'database_test_results',
            'migration_sync_test_results'
        ]
        
        workspace_root = Path("E:/gh_COPILOT")
        
        # Check for forbidden backup patterns
        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    # Check if this is an enterprise backup directory (exception)
                    is_enterprise_backup = any(
                        exception in folder.name 
                        for exception in enterprise_backup_exceptions
                    )
                    
                    # Also allow if it's in our allowed directories set
                    is_allowed_dir = folder.name.lower() in allowed_dirs
                    
                    if not (is_enterprise_backup or is_allowed_dir):
                        violations.append(str(folder))
        
        # Validate proper environment root usage
        if not str(workspace_root).replace("\\", "/").endswith("gh_COPILOT"):
            violations.append(f"Invalid workspace root: {workspace_root}")
        
        if violations:
            self.logger.error("[ERROR] CRITICAL: Environment violations detected!")
            for violation in violations:
                self.logger.error(f"   - {violation}")
            raise RuntimeError("CRITICAL: Environment violations prevent framework initialization")
        
        self.logger.info("[SUCCESS] Enterprise environment validation passed")

    def setup_database_connections(self):
        """Initialize database connections with validation"""
        try:
            if not self.production_db_path.exists():
                self.logger.error(f"[ERROR] Production database not found: {self.production_db_path}")
                raise FileNotFoundError(f"Production database not found: {self.production_db_path}")
            
            # Test database connection
            with sqlite3.connect(self.production_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                self.logger.info(f"[SUCCESS] Connected to production.db with {len(tables)} tables")
            
            # Ensure enhanced schema exists
            self.ensure_enhanced_schema()
            
        except Exception as e:
            self.logger.error(f"[ERROR] Database connection failed: {e}")
            raise

    def ensure_enhanced_schema(self):
        """Create enhanced database schema for template management"""
        self.logger.info("[WRENCH] Ensuring enhanced database schema exists...")
        
        schema_sql = """
        -- Script Template Storage
        CREATE TABLE IF NOT EXISTS script_templates (
            template_id TEXT PRIMARY KEY,
            template_name TEXT NOT NULL,
            template_category TEXT NOT NULL,
            template_content TEXT NOT NULL,
            template_metadata TEXT,
            environment_variants TEXT,
            success_patterns TEXT,
            complexity_score REAL DEFAULT 0.0,
            usage_frequency INTEGER DEFAULT 0,
            effectiveness_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Environment Configuration Management
        CREATE TABLE IF NOT EXISTS environment_configs (
            config_id TEXT PRIMARY KEY,
            environment_name TEXT NOT NULL,
            environment_type TEXT NOT NULL,
            configuration_data TEXT NOT NULL,
            deployment_patterns TEXT,
            validation_rules TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Template Effectiveness Tracking
        CREATE TABLE IF NOT EXISTS template_effectiveness (
            effectiveness_id TEXT PRIMARY KEY,
            template_id TEXT,
            usage_context TEXT,
            success_rate REAL DEFAULT 0.0,
            performance_metrics TEXT,
            user_feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES script_templates (template_id)
        );
        
        -- Script Generation History
        CREATE TABLE IF NOT EXISTS generation_history (
            generation_id TEXT PRIMARY KEY,
            template_id TEXT,
            environment_id TEXT,
            generated_content TEXT,
            generation_parameters TEXT,
            success_status TEXT,
            execution_results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES script_templates (template_id)
        );
        
        -- Codebase Analysis Results
        CREATE TABLE IF NOT EXISTS codebase_analysis (
            analysis_id TEXT PRIMARY KEY,
            analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_scripts_analyzed INTEGER,
            patterns_extracted TEXT,
            dependency_graph TEXT,
            complexity_metrics TEXT,
            enterprise_compliance_score REAL,
            analysis_metadata TEXT
        );
        """
        
        try:
            with sqlite3.connect(self.production_db_path) as conn:
                cursor = conn.cursor()
                cursor.executescript(schema_sql)
                conn.commit()
            
            self.logger.info("[SUCCESS] Enhanced database schema created successfully")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Schema creation failed: {e}")
            raise

    def analyze_existing_codebase(self, exclude_backup_dirs: bool = True) -> CodebaseAnalysis:
        """
        Comprehensive analysis of existing scripts for template extraction
        MANDATORY: Include timeout controls and progress monitoring
        """
        self.logger.info("[BAR_CHART] Starting comprehensive codebase analysis...")
        
        analysis_start_time = time.time()
        timeout_seconds = 300  # 5 minute timeout
        
        # Discover Python scripts with anti-recursion protection
        python_scripts = self.discover_python_scripts(exclude_backup_dirs)
        
        if not python_scripts:
            self.logger.warning("[WARNING] No Python scripts found for analysis")
            return CodebaseAnalysis(
                total_scripts_analyzed=0,
                patterns_extracted=[],
                template_candidates=[],
                dependency_graph={},
                complexity_metrics={},
                enterprise_compliance_score=0.0,
                analysis_timestamp=datetime.now().isoformat()
            )
        
        self.logger.info(f"[FOLDER] Discovered {len(python_scripts)} Python scripts for analysis")
        
        # Initialize analysis containers
        all_patterns = []
        template_candidates = []
        dependency_graph = {}
        complexity_metrics = {}
        total_compliance_score = 0.0
        
        # Analyze scripts with progress monitoring
        with tqdm(total=len(python_scripts), desc="[SEARCH] Analyzing scripts", unit="script") as pbar:
            for script_path in python_scripts:
                # Check timeout
                if time.time() - analysis_start_time > timeout_seconds:
                    self.logger.warning(f"[TIME] Analysis timeout reached after {timeout_seconds}s")
                    break
                
                try:
                    # Analyze individual script
                    script_analysis = self.analyze_individual_script(script_path)
                    
                    if script_analysis:
                        # Extract patterns
                        patterns = script_analysis.get('patterns', [])
                        all_patterns.extend(patterns)
                        
                        # Create template candidate
                        template = self.create_template_from_script(script_path, script_analysis)
                        if template:
                            template_candidates.append(template)
                        
                        # Build dependency graph
                        dependencies = script_analysis.get('dependencies', [])
                        dependency_graph[str(script_path)] = dependencies
                        
                        # Record complexity metrics
                        complexity = script_analysis.get('complexity_score', 0.0)
                        complexity_metrics[str(script_path)] = complexity
                        
                        # Add to compliance score
                        compliance = script_analysis.get('compliance_score', 0.0)
                        total_compliance_score += compliance
                        
                except Exception as e:
                    self.logger.warning(f"[WARNING] Error analyzing {script_path}: {e}")
                
                pbar.update(1)
        
        # Calculate final metrics
        avg_compliance_score = total_compliance_score / max(len(python_scripts), 1)
        
        analysis_result = CodebaseAnalysis(
            total_scripts_analyzed=len(python_scripts),
            patterns_extracted=list(set(all_patterns)),  # Remove duplicates
            template_candidates=template_candidates,
            dependency_graph=dependency_graph,
            complexity_metrics=complexity_metrics,
            enterprise_compliance_score=avg_compliance_score,
            analysis_timestamp=datetime.now().isoformat()
        )
        
        # Store analysis results in database
        self.store_analysis_results(analysis_result)
        
        analysis_time = time.time() - analysis_start_time
        self.logger.info(f"[SUCCESS] Codebase analysis completed in {analysis_time:.2f}s")
        self.logger.info(f"[BAR_CHART] Extracted {len(all_patterns)} patterns from {len(template_candidates)} templates")
        
        return analysis_result

    def discover_python_scripts(self, exclude_backup_dirs: bool = True) -> List[Path]:
        """Discover Python scripts with anti-recursion protection"""
        python_scripts = []
        
        # Forbidden directory patterns (anti-recursion)
        forbidden_patterns = [
            "*backup*", "*_backup_*", "*test*", "*temp*", "*cache*",
            "__pycache__", ".git", "node_modules", "venv", "virtualenv"
        ]
        
        # Allowed directories for enterprise operations
        allowed_dirs = {
            "databases", "database_backups", "database_test_results",
            "migration_sync_test_results", "scripts", "src"
        }
        
        try:
            for py_file in self.workspace_path.rglob("*.py"):
                # Skip if in forbidden directory pattern
                if exclude_backup_dirs:
                    path_parts = py_file.parts
                    skip_file = False
                    
                    for part in path_parts:
                        part_lower = part.lower()
                        # Check forbidden patterns
                        for pattern in forbidden_patterns:
                            pattern_clean = pattern.replace("*", "")
                            if pattern_clean in part_lower:
                                # Check if it's an allowed directory
                                if not any(allowed_dir in part_lower for allowed_dir in allowed_dirs):
                                    skip_file = True
                                    break
                        if skip_file:
                            break
                    
                    if skip_file:
                        continue
                
                # Validate file accessibility
                if py_file.exists() and py_file.is_file():
                    try:
                        # Test file readability
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            f.read(100)  # Test read
                        python_scripts.append(py_file)
                    except Exception:
                        continue
        
        except Exception as e:
            self.logger.error(f"[ERROR] Error discovering Python scripts: {e}")
        
        return python_scripts

    def analyze_individual_script(self, script_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze individual Python script for patterns and complexity"""
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
            except SyntaxError:
                self.logger.warning(f"[WARNING] Syntax error in {script_path}, skipping AST analysis")
                tree = None
            
            analysis = {
                'file_path': str(script_path),
                'file_size': len(content),
                'line_count': len(content.split('\n')),
                'patterns': [],
                'dependencies': [],
                'functions': [],
                'classes': [],
                'complexity_score': 0.0,
                'compliance_score': 0.0,
                'enterprise_patterns': []
            }
            
            # Extract imports and dependencies
            dependencies = self.extract_dependencies(content)
            analysis['dependencies'] = dependencies
            
            # Extract structural patterns
            if tree:
                patterns = self.extract_patterns_from_ast(tree)
                analysis['patterns'] = patterns
                
                # Extract functions and classes
                functions, classes = self.extract_functions_and_classes(tree)
                analysis['functions'] = functions
                analysis['classes'] = classes
                
                # Calculate complexity score
                complexity = self.calculate_complexity_score(tree, content)
                analysis['complexity_score'] = complexity
            
            # Check enterprise compliance patterns
            compliance_score = self.check_enterprise_compliance(content)
            analysis['compliance_score'] = compliance_score
            
            # Detect enterprise patterns
            enterprise_patterns = self.detect_enterprise_patterns(content)
            analysis['enterprise_patterns'] = enterprise_patterns
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"[WARNING] Error analyzing {script_path}: {e}")
            return None

    def extract_dependencies(self, content: str) -> List[str]:
        """Extract import dependencies from script content"""
        dependencies = []
        
        # Common import patterns
        import_patterns = [
            r'^import\s+([^\s#]+)',
            r'^from\s+([^\s#]+)\s+import',
        ]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    dependency = match.group(1).split('.')[0]  # Get base module
                    if dependency not in dependencies:
                        dependencies.append(dependency)
        
        return dependencies

    def extract_patterns_from_ast(self, tree: ast.AST) -> List[str]:
        """Extract structural patterns from AST"""
        patterns = []
        
        for node in ast.walk(tree):
            # Class patterns
            if isinstance(node, ast.ClassDef):
                patterns.append(f"class:{node.name}")
                
                # Check for inheritance
                if node.bases:
                    patterns.append("class:inheritance")
                
                # Check for decorators
                if node.decorator_list:
                    patterns.append("class:decorated")
            
            # Function patterns
            elif isinstance(node, ast.FunctionDef):
                patterns.append(f"function:{node.name}")
                
                # Check for decorators
                if node.decorator_list:
                    patterns.append("function:decorated")
                
                # Check for async functions
                if isinstance(node, ast.AsyncFunctionDef):
                    patterns.append("function:async")
            
            # Exception handling
            elif isinstance(node, ast.Try):
                patterns.append("error_handling:try_except")
            
            # Context managers
            elif isinstance(node, ast.With):
                patterns.append("context_manager:with_statement")
            
            # Comprehensions
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                patterns.append("comprehension:list_dict_set")
        
        return list(set(patterns))  # Remove duplicates

    def extract_functions_and_classes(self, tree: ast.AST) -> Tuple[List[str], List[str]]:
        """Extract function and class names from AST"""
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return functions, classes

    def calculate_complexity_score(self, tree: ast.AST, content: str) -> float:
        """Calculate complexity score based on various metrics"""
        complexity_factors = {
            'line_count': len(content.split('\n')),
            'function_count': 0,
            'class_count': 0,
            'nested_level': 0,
            'exception_handling': 0,
            'import_count': 0
        }
        
        max_nested_level = 0
        current_level = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity_factors['function_count'] += 1
            elif isinstance(node, ast.ClassDef):
                complexity_factors['class_count'] += 1
            elif isinstance(node, ast.Try):
                complexity_factors['exception_handling'] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                complexity_factors['import_count'] += 1
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
                current_level += 1
                max_nested_level = max(max_nested_level, current_level)
        
        complexity_factors['nested_level'] = max_nested_level
        
        # Calculate weighted complexity score (0-100 scale)
        score = min(100, (
            complexity_factors['line_count'] * 0.1 +
            complexity_factors['function_count'] * 2 +
            complexity_factors['class_count'] * 3 +
            complexity_factors['nested_level'] * 5 +
            complexity_factors['exception_handling'] * 2 +
            complexity_factors['import_count'] * 1
        ))
        
        return round(score, 2)

    def check_enterprise_compliance(self, content: str) -> float:
        """Check enterprise compliance patterns in script content"""
        compliance_score = 0.0
        total_checks = 10
        
        # Check for logging
        if re.search(r'import\s+logging|from\s+\w+\s+import.*logging', content):
            compliance_score += 10
        
        # Check for error handling
        if 'try:' in content and 'except' in content:
            compliance_score += 10
        
        # Check for docstrings
        if '"""' in content or "'''" in content:
            compliance_score += 10
        
        # Check for type hints
        if re.search(r':\s*\w+\s*=|def\s+\w+\([^)]*:\s*\w+', content):
            compliance_score += 10
        
        # Check for main guard
        if "if __name__ == '__main__':" in content:
            compliance_score += 10
        
        # Check for proper imports organization
        if content.startswith('#!/usr/bin/env python3') or content.startswith('#!/usr/bin/env python'):
            compliance_score += 10
        
        # Check for configuration management
        if any(pattern in content for pattern in ['config', 'Config', 'settings', 'Settings']):
            compliance_score += 5
        
        # Check for database usage
        if any(pattern in content for pattern in ['sqlite3', 'database', 'db']):
            compliance_score += 5
        
        # Check for progress indicators
        if any(pattern in content for pattern in ['tqdm', 'progress', 'logger.info']):
            compliance_score += 10
        
        # Check for path handling
        if any(pattern in content for pattern in ['Path', 'os.path', 'pathlib']):
            compliance_score += 10
        
        return min(100.0, compliance_score)

    def detect_enterprise_patterns(self, content: str) -> List[str]:
        """Detect specific enterprise patterns in script content"""
        patterns = []
        
        # DUAL COPILOT pattern
        if 'DUAL COPILOT' in content or 'dual_copilot' in content:
            patterns.append('DUAL_COPILOT_PATTERN')
        
        # Anti-recursion protection
        if any(term in content for term in ['anti_recursion', 'recursion', 'forbidden_patterns']):
            patterns.append('ANTI_RECURSION_PROTECTION')
        
        # Visual processing indicators
        if any(term in content for term in ['tqdm', 'progress', 'visual', 'indicator']):
            patterns.append('VISUAL_PROCESSING_INDICATORS')
        
        # Database integration
        if any(term in content for term in ['sqlite3', 'database', 'production.db']):
            patterns.append('DATABASE_INTEGRATION')
        
        # Enterprise compliance
        if any(term in content for term in ['enterprise', 'compliance', 'validation']):
            patterns.append('ENTERPRISE_COMPLIANCE')
        
        # Framework integration
        if any(term in content for term in ['framework', 'orchestrator', 'step1', 'step2']):
            patterns.append('FRAMEWORK_INTEGRATION')
        
        # Session management
        if any(term in content for term in ['session', 'Session', 'session_id']):
            patterns.append('SESSION_MANAGEMENT')
        
        # Performance monitoring
        if any(term in content for term in ['performance', 'metrics', 'monitoring']):
            patterns.append('PERFORMANCE_MONITORING')
        
        return patterns

    def create_template_from_script(self, script_path: Path, analysis: Dict[str, Any]) -> Optional[ScriptTemplate]:
        """Create a reusable template from analyzed script"""
        try:
            # Read script content
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Determine template category based on patterns and file name
            category = self.determine_template_category(script_path, analysis)
            
            # Generate template ID
            template_id = f"TPL_{hashlib.md5(str(script_path).encode()).hexdigest()[:8]}"
            
            # Extract metadata
            metadata = {
                'source_file': str(script_path),
                'file_size': analysis.get('file_size', 0),
                'line_count': analysis.get('line_count', 0),
                'functions': analysis.get('functions', []),
                'classes': analysis.get('classes', []),
                'dependencies': analysis.get('dependencies', []),
                'enterprise_patterns': analysis.get('enterprise_patterns', [])
            }
            
            # Create environment variants (placeholder for now)
            environment_variants = {
                'production': content,
                'development': content,
                'testing': content
            }
            
            # Extract success patterns
            success_patterns = analysis.get('patterns', [])
            
            template = ScriptTemplate(
                template_id=template_id,
                template_name=script_path.stem,
                template_category=category,
                template_content=content,
                template_metadata=metadata,
                environment_variants=environment_variants,
                success_patterns=success_patterns,
                complexity_score=analysis.get('complexity_score', 0.0),
                usage_frequency=0,
                effectiveness_score=analysis.get('compliance_score', 0.0)
            )
            
            return template
            
        except Exception as e:
            self.logger.warning(f"[WARNING] Error creating template from {script_path}: {e}")
            return None

    def determine_template_category(self, script_path: Path, analysis: Dict[str, Any]) -> str:
        """Determine template category based on script analysis"""
        filename = script_path.name.lower()
        patterns = analysis.get('enterprise_patterns', [])
        functions = analysis.get('functions', [])
        
        # Framework components
        if filename.startswith('step') and any(char.isdigit() for char in filename):
            return 'framework_step'
        elif 'orchestrator' in filename or 'master' in filename:
            return 'framework_orchestrator'
        elif 'scaling' in filename or 'innovation' in filename:
            return 'scaling_framework'
        
        # Database operations
        elif any(term in filename for term in ['db', 'database', 'migration', 'query']):
            return 'database_operations'
        
        # Validation and testing
        elif any(term in filename for term in ['validate', 'test', 'check', 'verify']):
            return 'validation_testing'
        
        # Analysis and reporting
        elif any(term in filename for term in ['analyze', 'analysis', 'report', 'metrics']):
            return 'analysis_reporting'
        
        # Deployment and setup
        elif any(term in filename for term in ['deploy', 'setup', 'install', 'config']):
            return 'deployment_setup'
        
        # Utility scripts
        elif any(term in filename for term in ['util', 'helper', 'tool', 'clean']):
            return 'utility_scripts'
        
        # Web and API
        elif any(term in filename for term in ['web', 'api', 'server', 'http']):
            return 'web_api'
        
        # Enterprise patterns
        elif 'ENTERPRISE_COMPLIANCE' in patterns:
            return 'enterprise_compliance'
        elif 'DUAL_COPILOT_PATTERN' in patterns:
            return 'dual_copilot'
        
        # Default category
        return 'general_purpose'

    def store_analysis_results(self, analysis: CodebaseAnalysis):
        """Store analysis results in database"""
        try:
            analysis_id = f"ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.production_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO codebase_analysis (
                        analysis_id, analysis_timestamp, total_scripts_analyzed,
                        patterns_extracted, dependency_graph, complexity_metrics,
                        enterprise_compliance_score, analysis_metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    analysis.analysis_timestamp,
                    analysis.total_scripts_analyzed,
                    json.dumps(analysis.patterns_extracted),
                    json.dumps(analysis.dependency_graph),
                    json.dumps(analysis.complexity_metrics),
                    analysis.enterprise_compliance_score,
                    json.dumps({
                        'template_count': len(analysis.template_candidates),
                        'session_id': self.session_id
                    })
                ))
                
                conn.commit()
            
            self.logger.info(f"[SUCCESS] Analysis results stored with ID: {analysis_id}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to store analysis results: {e}")

    def extract_proven_patterns(self, analysis: CodebaseAnalysis) -> List[ScriptTemplate]:
        """
        Extract successful patterns and create reusable templates
        MANDATORY: Validate patterns meet enterprise compliance standards
        """
        self.logger.info("[TARGET] Extracting proven patterns for template creation...")
        
        proven_templates = []
        
        # Filter templates by effectiveness and compliance
        for template in analysis.template_candidates:
            # Enterprise compliance threshold
            if template.effectiveness_score >= 70.0:  # 70% compliance minimum
                # Validate enterprise patterns
                if self.validate_template_compliance(template):
                    proven_templates.append(template)
                    self.logger.info(f"[SUCCESS] Proven template: {template.template_name} (Category: {template.template_category})")
        
        # Store proven templates in database
        self.store_proven_templates(proven_templates)
        
        self.logger.info(f"[TARGET] Extracted {len(proven_templates)} proven templates")
        return proven_templates

    def validate_template_compliance(self, template: ScriptTemplate) -> bool:
        """Validate template meets enterprise compliance standards"""
        compliance_checks = {
            'has_error_handling': 'try:' in template.template_content and 'except' in template.template_content,
            'has_logging': any(term in template.template_content for term in ['logging', 'logger', 'log']),
            'has_docstrings': '"""' in template.template_content or "'''" in template.template_content,
            'no_hardcoded_paths': not re.search(r'[C-Z]:\\', template.template_content),
            'proper_imports': template.template_content.strip().startswith(('#!/usr/bin/env python', 'import', 'from')),
            'enterprise_patterns': len(template.template_metadata.get('enterprise_patterns', [])) > 0
        }
        
        # Must pass at least 4 out of 6 compliance checks
        passed_checks = sum(compliance_checks.values())
        return passed_checks >= 4

    def store_proven_templates(self, templates: List[ScriptTemplate]):
        """Store proven templates in database"""
        self.logger.info(f"[STORAGE] Storing {len(templates)} proven templates...")
        
        with tqdm(total=len(templates), desc="[NOTES] Storing templates", unit="template") as pbar:
            try:
                with sqlite3.connect(self.production_db_path) as conn:
                    cursor = conn.cursor()
                    
                    for template in templates:
                        cursor.execute("""
                            INSERT OR REPLACE INTO script_templates (
                                template_id, template_name, template_category,
                                template_content, template_metadata, environment_variants,
                                success_patterns, complexity_score, usage_frequency,
                                effectiveness_score, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            template.template_id,
                            template.template_name,
                            template.template_category,
                            template.template_content,
                            json.dumps(template.template_metadata),
                            json.dumps(template.environment_variants),
                            json.dumps(template.success_patterns),
                            template.complexity_score,
                            template.usage_frequency,
                            template.effectiveness_score,
                            datetime.now().isoformat(),
                            datetime.now().isoformat()
                        ))
                        
                        pbar.update(1)
                    
                    conn.commit()
                
                self.logger.info("[SUCCESS] All proven templates stored successfully")
                
            except Exception as e:
                self.logger.error(f"[ERROR] Failed to store templates: {e}")
                raise

    def generate_framework_analysis_report(self, analysis: CodebaseAnalysis) -> str:
        """Generate comprehensive analysis report"""
        self.logger.info("[CLIPBOARD] Generating comprehensive framework analysis report...")
        
        report_content = f"""# Enterprise Script Generation Framework - Codebase Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Session ID:** {self.session_id}  
**Analysis Timestamp:** {analysis.analysis_timestamp}

## Executive Summary

### Analysis Metrics
- **Total Scripts Analyzed:** {analysis.total_scripts_analyzed}
- **Patterns Extracted:** {len(analysis.patterns_extracted)}
- **Template Candidates:** {len(analysis.template_candidates)}
- **Enterprise Compliance Score:** {analysis.enterprise_compliance_score:.1f}%

### Template Categories Distribution
"""
        
        # Count templates by category
        category_counts = {}
        for template in analysis.template_candidates:
            category = template.template_category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in sorted(category_counts.items()):
            report_content += f"- **{category.replace('_', ' ').title()}:** {count} templates\n"
        
        report_content += f"""
### Top Patterns Identified
"""
        
        # List top patterns
        pattern_counts = {}
        for template in analysis.template_candidates:
            for pattern in template.success_patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for pattern, count in top_patterns:
            report_content += f"- **{pattern}:** {count} occurrences\n"
        
        report_content += f"""
### Dependency Analysis
**Most Common Dependencies:**
"""
        
        # Analyze dependencies
        all_deps = []
        for deps in analysis.dependency_graph.values():
            all_deps.extend(deps)
        
        dep_counts = {}
        for dep in all_deps:
            dep_counts[dep] = dep_counts.get(dep, 0) + 1
        
        top_deps = sorted(dep_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for dep, count in top_deps:
            report_content += f"- **{dep}:** {count} scripts\n"
        
        report_content += f"""
### Complexity Analysis
- **Average Complexity Score:** {sum(analysis.complexity_metrics.values()) / max(len(analysis.complexity_metrics), 1):.1f}
- **Highest Complexity:** {max(analysis.complexity_metrics.values()) if analysis.complexity_metrics else 0:.1f}
- **Lowest Complexity:** {min(analysis.complexity_metrics.values()) if analysis.complexity_metrics else 0:.1f}

### Enterprise Compliance Assessment
- **Compliance Threshold Met:** {analysis.enterprise_compliance_score >= 70.0}
- **Templates Meeting Standards:** {len([t for t in analysis.template_candidates if t.effectiveness_score >= 70.0])}
- **Templates Requiring Improvement:** {len([t for t in analysis.template_candidates if t.effectiveness_score < 70.0])}

### Recommendations
1. **Template Standardization:** Focus on high-compliance templates for production use
2. **Pattern Replication:** Replicate successful patterns across new development
3. **Dependency Management:** Standardize common dependencies for consistency
4. **Complexity Reduction:** Refactor high-complexity scripts for maintainability

---

*Analysis completed by Enterprise Script Generation Framework*  
*DUAL COPILOT Pattern Implementation*
"""
        
        # Save report to file
        report_filename = f"ENTERPRISE_SCRIPT_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"[SUCCESS] Analysis report saved: {report_filename}")
        return report_filename

class TemplateManager:
    """
    Complete template lifecycle management
    MANDATORY: Include DUAL COPILOT validation for all operations
    """
    
    def __init__(self, production_db_path: Path):
        self.db_path = production_db_path
        self.logger = logging.getLogger(__name__)

    def store_template(self, template: ScriptTemplate) -> str:
        """Store template with metadata and validation"""
        # Implementation will be in Phase 2
        return "placeholder_template_id"

    def retrieve_template(self, template_id: str, environment_context: EnvironmentContext) -> Optional[ScriptTemplate]:
        """Retrieve and adapt template for specific environment"""
        # Implementation will be in Phase 2
        return None

    def validate_template_effectiveness(self, template_id: str) -> Dict[str, Any]:
        """Analyze template usage and success patterns"""
        # Implementation will be in Phase 2
        return {"placeholder": True}

class EnvironmentAdapter:
    """
    Environment-specific script adaptation
    MANDATORY: Prevent recursive backup creation and E:\gh_COPILOT	emp violations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def adapt_script_for_environment(self, script_content: str, target_environment: EnvironmentContext) -> str:
        """Adapt script content for specific deployment environment"""
        # Implementation will be in Phase 3
        pass

    def validate_environment_compatibility(self, script: str, environment: EnvironmentContext) -> bool:
        """Validate script compatibility with target environment"""
        # Implementation will be in Phase 3
        pass

class EnterpriseComplianceValidator:
    """
    Validate generated scripts meet enterprise standards
    MANDATORY: Include comprehensive validation with visual indicators
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_enterprise_compliance(self, script: str) -> Dict[str, bool]:
        """
        Comprehensive validation against enterprise standards
        MANDATORY: Check for recursive patterns, proper imports, error handling
        """
        # Implementation will be in Phase 4
        pass

def main():
    """Main execution function with enterprise safety protocols"""
    print("\n" + "="*80)
    print("ENTERPRISE SCRIPT GENERATION FRAMEWORK")
    print("Phase 1: Comprehensive Codebase Analysis")
    print("DUAL COPILOT Pattern Implementation")
    print("="*80)
    
    try:
        # Initialize framework
        generator = EnterpriseScriptGenerator()
        
        # Perform comprehensive codebase analysis
        print("\n[SEARCH] Starting comprehensive codebase analysis...")
        analysis_result = generator.analyze_existing_codebase()
        
        # Extract proven patterns
        print("\n[TARGET] Extracting proven patterns...")
        proven_templates = generator.extract_proven_patterns(analysis_result)
        
        # Generate analysis report
        print("\n[CLIPBOARD] Generating analysis report...")
        report_file = generator.generate_framework_analysis_report(analysis_result)
        
        # Display summary
        print("\n" + "="*80)
        print("PHASE 1 ANALYSIS COMPLETE")
        print("="*80)
        print(f"[SUCCESS] Scripts Analyzed: {analysis_result.total_scripts_analyzed}")
        print(f"[SUCCESS] Patterns Extracted: {len(analysis_result.patterns_extracted)}")
        print(f"[SUCCESS] Templates Created: {len(analysis_result.template_candidates)}")
        print(f"[SUCCESS] Proven Templates: {len(proven_templates)}")
        print(f"[SUCCESS] Enterprise Compliance: {analysis_result.enterprise_compliance_score:.1f}%")
        print(f"[CLIPBOARD] Analysis Report: {report_file}")
        print("\n[LAUNCH] Ready for Phase 2: Enhanced Database Schema and Template Management")
        
    except Exception as e:
        print(f"\n[ERROR] Framework initialization failed: {e}")
        logging.error(f"Framework error: {e}")
        raise

if __name__ == "__main__":
    main()
