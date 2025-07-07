#!/usr/bin/env python3
"""
Enterprise Script Generation Framework - Phase 3: Intelligent Generation Engine
==============================================================================

MISSION: Develop the core intelligent script generation engine with environment
adaptation, visual processing indicators, and context-aware template processing.

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
import datetime
import logging
import re
import ast
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import uuid

# Configure clean logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enterprise_script_generation_engine.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class GenerationRequest:
    """Script generation request"""
    user_prompt: str
    template_preference: Optional[str] = None
    environment_profile: Optional[str] = None
    output_filename: Optional[str] = None
    complexity_level: int = 2
    compliance_requirements: List[str] = None
    custom_variables: Dict[str, Any] = None

@dataclass
class GenerationResult:
    """Script generation result"""
    success: bool
    session_id: str
    generated_script: Optional[str] = None
    output_file_path: Optional[str] = None
    template_used: Optional[str] = None
    environment_used: Optional[str] = None
    generation_time: float = 0.0
    validation_results: Dict[str, Any] = None
    compliance_status: Dict[str, Any] = None
    suggestions: List[str] = None
    warnings: List[str] = None
    errors: List[str] = None

class VisualProcessingIndicator:
    """Visual processing indicator for generation progress"""
    
    def __init__(self):
        self.indicators = [
            "[Analysis]", "[Template Selection]", "[Environment Config]",
            "[Code Generation]", "[Validation]", "[Compliance Check]",
            "[Optimization]", "[Finalization]"
        ]
        self.current_step = 0
        
    def next_step(self, custom_message: Optional[str] = None) -> str:
        """Advance to next processing step"""
        if self.current_step < len(self.indicators):
            indicator = self.indicators[self.current_step]
            self.current_step += 1
            
            if custom_message:
                return f"{indicator} {custom_message}"
            return indicator
        return "[Complete]"
    
    def reset(self):
        """Reset indicator to beginning"""
        self.current_step = 0

class AntiRecursionGuard:
    """Enhanced anti-recursion protection for generation engine"""
    
    def __init__(self):
        self.active_sessions = set()
        self.generation_paths = set()
        self.max_concurrent_sessions = 5
        self.max_generation_depth = 3
        
    def register_session(self, session_id: str) -> bool:
        """Register new generation session"""
        if len(self.active_sessions) >= self.max_concurrent_sessions:
            return False
        
        if session_id in self.active_sessions:
            return False
            
        self.active_sessions.add(session_id)
        return True
    
    def unregister_session(self, session_id: str):
        """Unregister completed session"""
        self.active_sessions.discard(session_id)
    
    def check_generation_path(self, template_path: str) -> bool:
        """Check if generation path is safe"""
        normalized_path = os.path.normpath(template_path.lower())
        
        # Prevent recursive template generation
        if normalized_path in self.generation_paths:
            return False
            
        self.generation_paths.add(normalized_path)
        return True
    
    def clear_generation_path(self, template_path: str):
        """Clear generation path"""
        normalized_path = os.path.normpath(template_path.lower())
        self.generation_paths.discard(normalized_path)

class TemplateEngine:
    """Advanced template processing engine"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.variable_patterns = {
            'string': r'\{\{(\w+)\}\}',
            'function': r'\{\{func:(\w+)\}\}',
            'class': r'\{\{class:(\w+)\}\}',
            'import': r'\{\{import:(\w+)\}\}',
            'datetime': r'\{\{datetime:([^}]+)\}\}',
            'uuid': r'\{\{uuid\}\}',
            'database': r'\{\{db:(\w+)\}\}'
        }
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template from database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT template_name, template_type, category, description, 
                           base_template, variables, dependencies, compliance_patterns,
                           complexity_level, version, tags
                    FROM script_templates 
                    WHERE template_name = ? AND active = 1
                ''', (template_name,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'template_name': result[0],
                        'template_type': result[1],
                        'category': result[2],
                        'description': result[3],
                        'base_template': result[4],
                        'variables': json.loads(result[5] or '[]'),
                        'dependencies': json.loads(result[6] or '[]'),
                        'compliance_patterns': json.loads(result[7] or '[]'),
                        'complexity_level': result[8],
                        'version': result[9],
                        'tags': json.loads(result[10] or '[]')
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting template {template_name}: {e}")
            return None
    
    def find_best_template(self, user_prompt: str, category_preference: Optional[str] = None) -> Optional[str]:
        """Find best matching template based on user prompt"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Score templates based on prompt keywords
                query = '''
                    SELECT template_name, description, category, tags, complexity_level
                    FROM script_templates 
                    WHERE active = 1
                '''
                
                if category_preference:
                    query += f" AND category = '{category_preference}'"
                
                cursor.execute(query)
                templates = cursor.fetchall()
                
                if not templates:
                    return None
                
                # Simple keyword matching scoring
                prompt_lower = user_prompt.lower()
                prompt_keywords = re.findall(r'\w+', prompt_lower)
                
                best_template = None
                best_score = 0
                
                for template_name, description, category, tags, complexity in templates:
                    score = 0
                    
                    # Category matching
                    if category.lower() in prompt_lower:
                        score += 10
                    
                    # Tag matching
                    tag_list = json.loads(tags or '[]')
                    for tag in tag_list:
                        if tag.lower() in prompt_lower:
                            score += 5
                    
                    # Description keyword matching
                    if description:
                        desc_words = re.findall(r'\w+', description.lower())
                        for keyword in prompt_keywords:
                            if keyword in desc_words:
                                score += 2
                    
                    # Prefer lower complexity for simple requests
                    if len(prompt_keywords) < 5:
                        score += max(0, 5 - complexity)
                    
                    if score > best_score:
                        best_score = score
                        best_template = template_name
                
                return best_template
                
        except Exception as e:
            logger.error(f"Error finding best template: {e}")
            return None
    
    def process_template(self, template: Dict[str, Any], variables: Dict[str, Any]) -> str:
        """Process template with provided variables"""
        try:
            content = template['base_template']
            
            # Process different variable types
            for pattern_type, pattern in self.variable_patterns.items():
                matches = re.findall(pattern, content)
                
                for match in matches:
                    if pattern_type == 'datetime':
                        # Process datetime formatting
                        format_str = match if match else '%Y-%m-%d %H:%M:%S'
                        replacement = datetime.datetime.now().strftime(format_str)
                        content = content.replace(f'{{{{datetime:{match}}}}}', replacement)
                        
                    elif pattern_type == 'uuid':
                        # Generate UUID
                        replacement = str(uuid.uuid4())
                        content = content.replace('{{uuid}}', replacement)
                        
                    elif pattern_type in variables:
                        # Use provided variable
                        replacement = str(variables[pattern_type].get(match, f'PLACEHOLDER_{match}'))
                        if pattern_type == 'string':
                            content = content.replace(f'{{{{{match}}}}}', replacement)
                        else:
                            content = content.replace(f'{{{{' + pattern_type + f':{match}}}}}', replacement)
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing template: {e}")
            return template['base_template']

class EnvironmentAdapter:
    """Environment-specific adaptation engine"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def get_environment_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get environment profile from database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT profile_name, description, target_platform, python_version,
                           enterprise_level, compliance_requirements, default_packages, security_level
                    FROM environment_profiles 
                    WHERE profile_name = ? AND active = 1
                ''', (profile_name,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'profile_name': result[0],
                        'description': result[1],
                        'target_platform': result[2],
                        'python_version': result[3],
                        'enterprise_level': result[4],
                        'compliance_requirements': json.loads(result[5] or '[]'),
                        'default_packages': json.loads(result[6] or '[]'),
                        'security_level': result[7]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting environment profile {profile_name}: {e}")
            return None
    
    def adapt_script_for_environment(self, script_content: str, environment: Dict[str, Any]) -> str:
        """Adapt script content for specific environment"""
        try:
            adapted_content = script_content
            
            # Add required imports based on environment
            imports_section = ""
            for package in environment.get('default_packages', []):
                if f'import {package}' not in adapted_content:
                    imports_section += f"import {package}\n"
            
            # Add environment-specific configurations
            config_section = f"""
# Environment Configuration: {environment['profile_name']}
# Target Platform: {environment['target_platform']}
# Python Version: {environment['python_version']}
# Enterprise Level: {environment['enterprise_level']}
# Security Level: {environment['security_level']}

"""
            
            # Add compliance requirements
            compliance_section = ""
            for requirement in environment.get('compliance_requirements', []):
                if requirement == 'DUAL_COPILOT':
                    compliance_section += "# DUAL COPILOT pattern enforcement required\n"
                elif requirement == 'ANTI_RECURSION':
                    compliance_section += "# Anti-recursion protection required\n"
                elif requirement == 'ENTERPRISE_LOGGING':
                    compliance_section += "# Enterprise logging configuration required\n"
            
            # Combine sections
            if imports_section or config_section or compliance_section:
                header = '#!/usr/bin/env python3\n"""Generated Script"""\n\n'
                header += imports_section + config_section + compliance_section + "\n"
                
                # Insert after shebang and docstring if they exist
                if adapted_content.startswith('#!'):
                    lines = adapted_content.split('\n')
                    insert_index = 1
                    
                    # Skip docstring
                    if len(lines) > 1 and (lines[1].startswith('"""') or lines[1].startswith("'''")):
                        quote_char = lines[1][:3]
                        for i in range(2, len(lines)):
                            if quote_char in lines[i]:
                                insert_index = i + 1
                                break
                    
                    lines.insert(insert_index, header)
                    adapted_content = '\n'.join(lines)
                else:
                    adapted_content = header + adapted_content
            
            return adapted_content
            
        except Exception as e:
            logger.error(f"Error adapting script for environment: {e}")
            return script_content

class ComplianceValidator:
    """Enterprise compliance validation engine"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.compliance_patterns = self.load_compliance_patterns()
    
    def load_compliance_patterns(self) -> Dict[str, Any]:
        """Load compliance patterns from database"""
        patterns = {}
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT pattern_name, pattern_type, pattern_regex, description, severity
                    FROM compliance_patterns 
                    WHERE active = 1
                ''')
                
                for row in cursor.fetchall():
                    patterns[row[0]] = {
                        'pattern_type': row[1],
                        'pattern_regex': row[2],
                        'description': row[3],
                        'severity': row[4]
                    }
                    
        except Exception as e:
            logger.error(f"Error loading compliance patterns: {e}")
            
        return patterns
    
    def validate_script(self, script_content: str, session_id: str) -> Dict[str, Any]:
        """Validate script against compliance patterns"""
        results = {
            'overall_compliance': True,
            'passed_checks': [],
            'failed_checks': [],
            'warnings': [],
            'severity_breakdown': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        }
        
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                for pattern_name, pattern_info in self.compliance_patterns.items():
                    try:
                        if re.search(pattern_info['pattern_regex'], script_content, re.IGNORECASE | re.MULTILINE):
                            results['passed_checks'].append({
                                'pattern': pattern_name,
                                'description': pattern_info['description'],
                                'severity': pattern_info['severity']
                            })
                            
                            # Log compliance check
                            cursor.execute('''
                                INSERT INTO compliance_checks 
                                (check_name, check_type, target_type, target_id, check_result, 
                                 details, timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                pattern_name, pattern_info['pattern_type'], 'generated_script',
                                session_id, 'passed', pattern_info['description'], timestamp
                            ))
                            
                        else:
                            results['failed_checks'].append({
                                'pattern': pattern_name,
                                'description': pattern_info['description'],
                                'severity': pattern_info['severity']
                            })
                            
                            results['severity_breakdown'][pattern_info['severity']] += 1
                            
                            # Critical and high severity failures affect overall compliance
                            if pattern_info['severity'] in ['critical', 'high']:
                                results['overall_compliance'] = False
                            else:
                                results['warnings'].append(f"Missing {pattern_name}: {pattern_info['description']}")
                            
                            # Log compliance check
                            cursor.execute('''
                                INSERT INTO compliance_checks 
                                (check_name, check_type, target_type, target_id, check_result, 
                                 details, timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                pattern_name, pattern_info['pattern_type'], 'generated_script',
                                session_id, 'failed', pattern_info['description'], timestamp
                            ))
                            
                    except re.error as e:
                        logger.warning(f"Invalid regex pattern {pattern_name}: {e}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error validating script compliance: {e}")
            results['overall_compliance'] = False
        
        return results

class IntelligentScriptGenerator:
    """Main intelligent script generation engine"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / 'databases' / 'production.db'
        self.output_dir = self.workspace_path / 'generated_scripts'
        self.output_dir.mkdir(exist_ok=True)
        
        self.template_engine = TemplateEngine(self.db_path)
        self.environment_adapter = EnvironmentAdapter(self.db_path)
        self.compliance_validator = ComplianceValidator(self.db_path)
        self.anti_recursion = AntiRecursionGuard()
        self.visual_indicator = VisualProcessingIndicator()
        
    def generate_script(self, request: GenerationRequest) -> GenerationResult:
        """Generate script based on request"""
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Initialize result
        result = GenerationResult(
            success=False,
            session_id=session_id,
            warnings=[],
            errors=[],
            suggestions=[]
        )
        
        try:
            # Anti-recursion protection
            if not self.anti_recursion.register_session(session_id):
                result.errors.append("Maximum concurrent sessions reached")
                return result
            
            logger.info(f"Starting script generation session: {session_id}")
            self.log_generation_session(session_id, request, start_time)
            
            # Step 1: Analysis
            print(f"\n{self.visual_indicator.next_step('User prompt analysis...')}")
            
            # Step 2: Template Selection
            print(f"{self.visual_indicator.next_step('Finding optimal template...')}")
            template_name = self.select_template(request)
            if not template_name:
                result.errors.append("No suitable template found")
                return result
            
            template = self.template_engine.get_template(template_name)
            if not template:
                result.errors.append(f"Template {template_name} not found")
                return result
            
            result.template_used = template_name
            
            # Step 3: Environment Configuration
            print(f"{self.visual_indicator.next_step('Configuring environment...')}")
            environment = self.select_environment(request)
            if environment:
                result.environment_used = environment['profile_name']
            
            # Step 4: Code Generation
            print(f"{self.visual_indicator.next_step('Generating code...')}")
            generated_content = self.generate_content(template, request, environment)
            
            # Step 5: Validation
            print(f"{self.visual_indicator.next_step('Validating generated code...')}")
            validation_results = self.validate_generated_content(generated_content)
            result.validation_results = validation_results
            
            # Step 6: Compliance Check
            print(f"{self.visual_indicator.next_step('Compliance verification...')}")
            compliance_results = self.compliance_validator.validate_script(generated_content, session_id)
            result.compliance_status = compliance_results
            
            # Step 7: Optimization
            print(f"{self.visual_indicator.next_step('Optimizing output...')}")
            optimized_content = self.optimize_content(generated_content, compliance_results)
            
            # Step 8: Finalization
            print(f"{self.visual_indicator.next_step('Finalizing script...')}")
            output_path = self.save_generated_script(optimized_content, request, session_id)
            
            result.success = True
            result.generated_script = optimized_content
            result.output_file_path = str(output_path)
            result.generation_time = time.time() - start_time
            
            # Add suggestions
            result.suggestions = self.generate_suggestions(template, environment, compliance_results)
            
            print(f"{self.visual_indicator.next_step('Generation complete!')}")
            
            # Log successful completion
            self.log_generation_completion(session_id, result)
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            result.errors.append(f"Generation failed: {str(e)}")
            
        finally:
            self.anti_recursion.unregister_session(session_id)
            self.visual_indicator.reset()
        
        return result
    
    def select_template(self, request: GenerationRequest) -> Optional[str]:
        """Select optimal template for request"""
        if request.template_preference:
            return request.template_preference
        
        # Use AI-like template selection based on prompt analysis
        return self.template_engine.find_best_template(request.user_prompt)
    
    def select_environment(self, request: GenerationRequest) -> Optional[Dict[str, Any]]:
        """Select optimal environment for request"""
        if request.environment_profile:
            return self.environment_adapter.get_environment_profile(request.environment_profile)
        
        # Default to Enterprise Development environment
        return self.environment_adapter.get_environment_profile('Enterprise Development')
    
    def generate_content(self, template: Dict[str, Any], request: GenerationRequest, 
                        environment: Optional[Dict[str, Any]]) -> str:
        """Generate script content"""
        # Prepare variables
        variables = {
            'string': request.custom_variables or {},
            'function': {},
            'class': {},
            'import': {}
        }
        
        # Generate base content
        content = self.template_engine.process_template(template, variables)
        
        # Adapt for environment
        if environment:
            content = self.environment_adapter.adapt_script_for_environment(content, environment)
        
        return content
    
    def validate_generated_content(self, content: str) -> Dict[str, Any]:
        """Validate generated content"""
        results = {
            'syntax_valid': True,
            'line_count': len(content.splitlines()),
            'estimated_complexity': 0,
            'issues': []
        }
        
        try:
            # Basic syntax validation
            ast.parse(content)
            results['syntax_valid'] = True
        except SyntaxError as e:
            results['syntax_valid'] = False
            results['issues'].append(f"Syntax error: {e}")
        
        # Estimate complexity
        results['estimated_complexity'] = min(len(content) // 100, 10)
        
        return results
    
    def optimize_content(self, content: str, compliance_results: Dict[str, Any]) -> str:
        """Optimize generated content"""
        optimized = content
        
        # Add missing compliance elements
        if not compliance_results.get('overall_compliance', True):
            for failed_check in compliance_results.get('failed_checks', []):
                if failed_check['pattern'] == 'DUAL_COPILOT_MAIN':
                    # Add DUAL COPILOT pattern to main function
                    if 'def main():' in optimized and '# DUAL COPILOT PATTERN' not in optimized:
                        optimized = optimized.replace(
                            'def main():',
                            'def main():\n    """Main execution function with DUAL COPILOT pattern"""\n    \n    # DUAL COPILOT PATTERN: Primary Execution'
                        )
        
        return optimized
    
    def save_generated_script(self, content: str, request: GenerationRequest, session_id: str) -> Path:
        """Save generated script to file"""
        if request.output_filename:
            filename = request.output_filename
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_script_{timestamp}.py"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Log to database
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                
                cursor.execute('''
                    INSERT INTO generated_scripts 
                    (session_id, script_name, script_content, content_hash, 
                     lines_of_code, file_size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, filename, content, content_hash,
                    len(content.splitlines()), len(content.encode('utf-8'))
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log generated script: {e}")
        
        return output_path
    
    def generate_suggestions(self, template: Dict[str, Any], environment: Optional[Dict[str, Any]], 
                           compliance_results: Dict[str, Any]) -> List[str]:
        """Generate helpful suggestions"""
        suggestions = []
        
        if template:
            suggestions.append(f"Consider exploring other {template['category']} templates")
        
        if environment and environment['security_level'] < 3:
            suggestions.append("Consider using a higher security environment profile for production")
        
        if not compliance_results.get('overall_compliance', True):
            suggestions.append("Review compliance failures and consider updating the script")
        
        return suggestions
    
    def log_generation_session(self, session_id: str, request: GenerationRequest, start_time: float):
        """Log generation session to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO generation_sessions 
                    (session_id, user_prompt, template_used_id, environment_profile_id,
                     generation_mode, generation_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, request.user_prompt, None, None,
                    'assisted', datetime.datetime.fromtimestamp(start_time).isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log generation session: {e}")
    
    def log_generation_completion(self, session_id: str, result: GenerationResult):
        """Log generation completion to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE generation_sessions 
                    SET success = ?, output_file_path = ?, completion_timestamp = ?, 
                        duration_seconds = ?
                    WHERE session_id = ?
                ''', (
                    result.success, result.output_file_path, 
                    datetime.datetime.now().isoformat(), result.generation_time,
                    session_id
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log generation completion: {e}")

def main():
    """Main execution function with DUAL COPILOT pattern"""
    
    # DUAL COPILOT PATTERN: Primary Generation Engine Test
    try:
        workspace_path = r"E:\gh_COPILOT"
        generator = IntelligentScriptGenerator(workspace_path)
        
        # Test generation request
        test_request = GenerationRequest(
            user_prompt="Create an enterprise database analysis script with anti-recursion protection",
            template_preference=None,
            environment_profile="Enterprise Development",
            output_filename="test_generated_enterprise_analyzer.py",
            complexity_level=3,
            compliance_requirements=['DUAL_COPILOT', 'ANTI_RECURSION', 'ENTERPRISE_LOGGING'],
            custom_variables={'database_name': 'production.db', 'analysis_type': 'comprehensive'}
        )
        
        print("\n" + "="*80)
        print("ENTERPRISE SCRIPT GENERATION ENGINE - TEST EXECUTION")
        print("="*80)
        
        result = generator.generate_script(test_request)
        
        print("\n" + "="*80)
        print("GENERATION RESULTS")
        print("="*80)
        print(f"Success: {result.success}")
        print(f"Session ID: {result.session_id}")
        print(f"Template Used: {result.template_used}")
        print(f"Environment Used: {result.environment_used}")
        print(f"Output File: {result.output_file_path}")
        print(f"Generation Time: {result.generation_time:.2f} seconds")
        print(f"Compliance Status: {result.compliance_status.get('overall_compliance', 'Unknown') if result.compliance_status else 'Not checked'}")
        
        if result.suggestions:
            print(f"Suggestions: {len(result.suggestions)}")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")
        
        if result.warnings:
            print(f"Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.errors:
            print(f"Errors: {len(result.errors)}")
            for error in result.errors:
                print(f"  - {error}")
        
        print("="*80)
        
        return result
        
    except Exception as e:
        logger.error(f"Primary generation engine test failed: {e}")
        
        # DUAL COPILOT PATTERN: Secondary Validation
        print("\n" + "="*80)
        print("DUAL COPILOT SECONDARY VALIDATION")
        print("="*80)
        print("Primary test encountered issues. Running validation...")
        
        # Basic validation
        workspace_path = Path(r"E:\gh_COPILOT")
        
        validation_results = {
            'workspace_exists': workspace_path.exists(),
            'database_exists': (workspace_path / 'databases' / 'production.db').exists(),
            'output_dir_exists': (workspace_path / 'generated_scripts').exists(),
            'generator_created': False,
            'error_details': str(e)
        }
        
        try:
            generator = IntelligentScriptGenerator(str(workspace_path))
            validation_results['generator_created'] = True
        except:
            validation_results['generator_created'] = False
        
        print("Validation Results:")
        for key, value in validation_results.items():
            print(f"- {key}: {value}")
        
        print("="*80)
        return validation_results

if __name__ == "__main__":
    main()
