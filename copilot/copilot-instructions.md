# Copilot Instructions for gh_COPILOT Toolkit v4.0
## Database-First Enterprise Development Guide

### System Overview

**gh_COPILOT Toolkit v4.0** is an enterprise-grade, database-first documentation and build management system. This codebase emphasizes:

- **Database-First Architecture**: All operations query SQLite databases before filesystem exploration
- **Template Intelligence Platform**: 1604+ templates across 40+ databases for systematic code generation
- **Enterprise Compliance**: DUAL COPILOT pattern, visual processing indicators, anti-recursion protection
- **Multi-Database Coordination**: Cross-database synchronization and template sharing

### Critical Architecture Principles

#### 1. Database-First Process
```python
# ALWAYS query database before filesystem operations
with sqlite3.connect('databases/production.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM enhanced_script_tracking WHERE status = 'active'")
    existing_solutions = cursor.fetchall()
    
# THEN adapt to current environment
adapted_solution = adapt_database_solution(existing_solutions, current_requirements)
```

#### 2. Visual Processing Indicators (MANDATORY)
```python
# ALL operations MUST include visual processing
from tqdm import tqdm
import datetime

start_time = datetime.datetime.now()
logger.info(f"🚀 PROCESS STARTED: {process_name}")
logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

with tqdm(total=100, desc="Processing", unit="%") as pbar:
    for step in process_steps:
        pbar.set_description(f"🔄 {step.name}")
        execute_step(step)
        pbar.update(step.weight)
```

#### 3. Enterprise Logging Standards
```python
import logging

# Required logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/operation.log'),
        logging.StreamHandler()
    ]
)
```

### Database Schema Understanding

#### Core Databases
- **production.db**: Main operational data, enhanced_script_tracking table with 16,500+ entries
- **documentation.db**: Documentation metadata and content storage
- **template_documentation.db**: Template definitions and usage patterns
- **template_compliance.db**: Enterprise compliance tracking and scoring
- **enterprise_builds.db**: Build process metadata and deployment tracking

#### Template Intelligence Tables
```sql
-- Common pattern across template databases
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT UNIQUE NOT NULL,
    template_content TEXT NOT NULL,
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE shared_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id TEXT NOT NULL,
    source_database TEXT NOT NULL,
    template_content TEXT NOT NULL,
    placeholder_mapping TEXT, -- JSON
    sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sync_status TEXT DEFAULT 'active'
);
```

### Template-Driven Development

#### Template Discovery Pattern
```python
def discover_templates(category: str) -> List[TemplateMetadata]:
    """Query multiple databases for relevant templates"""
    databases = ['development.db', 'staging.db', 'production.db', 'template_documentation.db']
    templates = []
    
    for db_path in databases:
        with sqlite3.connect(f'databases/{db_path}') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT template_name, template_content, source_database 
                FROM templates 
                WHERE template_name LIKE ? AND is_active = 1
            """, (f"%{category}%",))
            
            for row in cursor.fetchall():
                templates.append(TemplateMetadata(
                    name=row[0],
                    content=row[1],
                    source_db=row[2]
                ))
    
    return templates
```

#### Template Generation with Jinja2
```python
from jinja2 import Template

def generate_from_template(template_content: str, context: Dict[str, Any]) -> str:
    """Generate content using Jinja2 templates"""
    template = Template(template_content)
    return template.render(**context)
```

### Enterprise Compliance Requirements

#### DUAL COPILOT Pattern
```python
class PrimaryCopilotExecutor:
    """Primary execution with monitoring"""
    def execute_with_monitoring(self, task):
        monitor = ProcessMonitor()
        monitor.start_process(task)
        
        try:
            result = self._execute_with_progress(task)
            validation = SecondaryValidator().validate_execution(result)
            if not validation.passed:
                raise ValidationError(f"Secondary validation failed: {validation.errors}")
            return result
        finally:
            monitor.end_process()
```

#### Anti-Recursion Protection
```python
def validate_workspace_integrity():
    """CRITICAL: Validate no recursive folder structures"""
    workspace_root = Path(os.getcwd())
    forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
    
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                logger.error(f"🚨 RECURSIVE VIOLATION: {folder}")
                raise RuntimeError("CRITICAL: Recursive violations prevent execution")
    
    return True
```

### Common Development Patterns

#### 1. Database-First Documentation Generation
```python
class EnterpriseDocumentationManager:
    def generate_documentation(self, doc_type: str):
        # Query existing documentation patterns
        existing_docs = self.query_documentation_database(doc_type)
        
        # Find relevant templates
        templates = self.discover_templates(doc_type)
        
        # Generate using template intelligence
        content = self.apply_template_intelligence(templates, existing_docs)
        
        # Store in database with compliance tracking
        self.store_documentation(content, compliance_score=self.calculate_compliance())
```

#### 2. Cross-Database Template Synchronization
```python
def synchronize_templates():
    """Sync templates across multiple databases"""
    source_dbs = ['development.db', 'staging.db', 'production.db']
    
    for source_db in source_dbs:
        templates = extract_templates(source_db)
        for template in templates:
            sync_template_across_databases(template, source_db)
```

#### 3. Enterprise Build Management
```python
class EnterpriseBuilds:
    def execute_build(self, build_config):
        # Database-first build validation
        existing_builds = self.query_build_history(build_config.type)
        
        # Template-driven build generation
        build_script = self.generate_build_script(build_config, existing_builds)
        
        # Execute with visual indicators
        result = self.execute_with_monitoring(build_script)
        
        # Store results in enterprise_builds.db
        self.record_build_results(result)
```

### Key Management Scripts

#### Core Enterprise Scripts
- **enterprise_database_driven_documentation_manager.py**: Main documentation management
- **enterprise_template_driven_documentation_system.py**: Template intelligence engine
- **enterprise_template_compliance_enhancer.py**: Compliance scoring and enhancement
- **enterprise_database_driven_build_orchestrator.py**: Build process management
- **comprehensive_pis_framework.py**: Plan Issued Statement framework

#### Database Management Scripts
- **database_consolidation_migration.py**: Database synchronization and migration
- **database_first_synchronization_engine.py**: Cross-database template synchronization
- **database_file_system_synchronization_validator.py**: Filesystem-database consistency

### Development Workflow

#### 1. Start with Database Query
```python
# ALWAYS start development by querying existing solutions
def start_development_task(objective: str):
    existing_solutions = query_production_database(objective)
    if existing_solutions:
        return adapt_existing_solution(existing_solutions[0], objective)
    else:
        return create_new_solution_with_templates(objective)
```

#### 2. Apply Template Intelligence
```python
# Use template system for consistent code generation
def generate_solution(requirements: Dict[str, Any]):
    relevant_templates = discover_templates(requirements['category'])
    best_template = select_optimal_template(relevant_templates, requirements)
    return generate_from_template(best_template.content, requirements)
```

#### 3. Validate Enterprise Compliance
```python
# ALWAYS validate against enterprise standards
def validate_solution(solution_code: str):
    compliance_checks = [
        check_visual_processing_indicators(solution_code),
        check_anti_recursion_compliance(solution_code),
        check_database_first_pattern(solution_code),
        check_dual_copilot_pattern(solution_code)
    ]
    return all(compliance_checks)
```

### Testing and Validation

#### Enterprise Testing Pattern
```python
def test_enterprise_solution(solution):
    """Comprehensive testing following enterprise standards"""
    test_results = {
        'functionality': test_functionality(solution),
        'compliance': test_enterprise_compliance(solution),
        'database_integration': test_database_integration(solution),
        'template_compatibility': test_template_compatibility(solution),
        'visual_indicators': test_visual_processing(solution)
    }
    
    overall_score = calculate_enterprise_score(test_results)
    return overall_score >= 0.90  # 90% enterprise compliance required
```

### Important Notes

#### Avoid These Patterns
- **Filesystem-first operations**: Always query databases before filesystem
- **Manual template creation**: Use template intelligence system
- **Missing visual indicators**: All operations require progress tracking
- **Recursive folder structures**: Strictly forbidden in workspace
- **Direct file operations**: Use database-mediated operations

#### Required Dependencies
```python
# Core dependencies for enterprise development
import sqlite3      # Database operations
import jinja2       # Template engine
import tqdm         # Visual processing indicators
import logging      # Enterprise logging
import pathlib      # Path management
import datetime     # Timestamp management
import hashlib      # Content hashing
```

#### Environment Variables
```bash
# Recommended environment setup
export GH_COPILOT_WORKSPACE="e:/gh_COPILOT"
export GH_COPILOT_DATABASE_PATH="e:/gh_COPILOT/databases"
export GH_COPILOT_LOG_LEVEL="INFO"
```

### Quick Reference

#### Database Query Pattern
```python
with sqlite3.connect('databases/production.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM enhanced_script_tracking WHERE functionality_category = ?", (category,))
    results = cursor.fetchall()
```

#### Template Application Pattern
```python
from jinja2 import Template
template = Template(template_content)
result = template.render(context_variables)
```

#### Visual Processing Pattern
```python
with tqdm(total=steps, desc="Operation") as pbar:
    for step in operation_steps:
        pbar.set_description(f"🔄 {step}")
        execute_step(step)
        pbar.update(1)
```

This guide provides the foundational understanding needed to develop effectively within the gh_COPILOT Toolkit v4.0 enterprise architecture. Always prioritize database-first approaches, template intelligence, and enterprise compliance in your development process.
