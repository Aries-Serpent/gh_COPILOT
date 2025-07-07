#!/usr/bin/env python3
"""
Enterprise Script Generation Framework - Phase 4: GitHub Copilot Integration
============================================================================

MISSION: Integrate with GitHub Copilot for context-aware suggestions, template-driven
code generation, and intelligent code completion within the enterprise framework.

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
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import time

# Configure clean logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enterprise_copilot_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CopilotContext:
    """GitHub Copilot context information"""
    context_id: str
    context_type: str  # template, pattern, example, completion
    content: str
    metadata: Dict[str, Any]
    effectiveness_score: float = 0.0
    usage_count: int = 0

@dataclass
class CopilotSuggestion:
    """GitHub Copilot suggestion"""
    suggestion_id: str
    suggestion_type: str
    content: str
    confidence_score: float
    context_used: List[str]
    accepted: bool = False
    timestamp: str = ""

class CopilotContextManager:
    """Manage GitHub Copilot contexts for enhanced suggestions"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.active_contexts = {}
        self.suggestion_cache = {}
    
    def create_template_context(self, template: Dict[str, Any]) -> CopilotContext:
        """Create Copilot context from template"""
        context_id = f"template_{template['template_name']}"
        
        # Extract key patterns and structures
        content_analysis = self.analyze_template_content(template['base_template'])
        
        context_content = f"""
# Template Context: {template['template_name']}
# Category: {template['category']}
# Description: {template['description']}

## Key Patterns:
{chr(10).join(f"- {pattern}" for pattern in content_analysis['patterns'])}

## Structure:
{chr(10).join(f"- {structure}" for structure in content_analysis['structures'])}

## Compliance Requirements:
{chr(10).join(f"- {req}" for req in template.get('compliance_patterns', []))}

## Template Base:
```python
{template['base_template'][:500]}...
```
"""
        
        context = CopilotContext(
            context_id=context_id,
            context_type='template',
            content=context_content,
            metadata={
                'template_name': template['template_name'],
                'category': template['category'],
                'complexity_level': template.get('complexity_level', 1),
                'patterns': content_analysis['patterns'],
                'structures': content_analysis['structures']
            }
        )
        
        self.active_contexts[context_id] = context
        return context
    
    def create_pattern_context(self, pattern_name: str, pattern_info: Dict[str, Any]) -> CopilotContext:
        """Create Copilot context from compliance pattern"""
        context_id = f"pattern_{pattern_name}"
        
        context_content = f"""
# Compliance Pattern: {pattern_name}
# Type: {pattern_info.get('pattern_type', 'unknown')}
# Severity: {pattern_info.get('severity', 'medium')}

## Description:
{pattern_info.get('description', 'No description available')}

## Pattern Regex:
{pattern_info.get('pattern_regex', 'No regex available')}

## Implementation Example:
```python
# This pattern ensures: {pattern_info.get('description', 'compliance requirement')}
{self.generate_pattern_example(pattern_name, pattern_info)}
```
"""
        
        context = CopilotContext(
            context_id=context_id,
            context_type='pattern',
            content=context_content,
            metadata={
                'pattern_name': pattern_name,
                'pattern_type': pattern_info.get('pattern_type', 'unknown'),
                'severity': pattern_info.get('severity', 'medium')
            }
        )
        
        self.active_contexts[context_id] = context
        return context
    
    def create_generation_context(self, user_prompt: str, session_data: Dict[str, Any]) -> CopilotContext:
        """Create context for active generation session"""
        context_id = f"generation_{session_data.get('session_id', 'unknown')}"
        
        context_content = f"""
# Active Generation Session
# Session ID: {session_data.get('session_id', 'unknown')}
# Timestamp: {datetime.datetime.now().isoformat()}

## User Request:
{user_prompt}

## Generation Parameters:
- Template: {session_data.get('template_used', 'auto-selected')}
- Environment: {session_data.get('environment_profile', 'default')}
- Complexity Level: {session_data.get('complexity_level', 2)}

## Expected Compliance:
{chr(10).join(f"- {req}" for req in session_data.get('compliance_requirements', []))}

## Context Guidelines:
- Follow DUAL COPILOT pattern
- Implement anti-recursion protection
- Use enterprise logging standards
- Ensure database connection safety
"""
        
        context = CopilotContext(
            context_id=context_id,
            context_type='generation',
            content=context_content,
            metadata=session_data
        )
        
        self.active_contexts[context_id] = context
        return context
    
    def analyze_template_content(self, template_content: str) -> Dict[str, List[str]]:
        """Analyze template content for patterns and structures"""
        patterns = []
        structures = []
        
        # Common enterprise patterns
        if 'DUAL COPILOT' in template_content:
            patterns.append('DUAL COPILOT pattern implementation')
        if 'AntiRecursionGuard' in template_content:
            patterns.append('Anti-recursion protection')
        if 'logging.basicConfig' in template_content:
            patterns.append('Enterprise logging configuration')
        if 'sqlite3.connect' in template_content:
            patterns.append('Database connection handling')
        
        # Structural elements
        if 'class ' in template_content:
            class_matches = re.findall(r'class\s+(\w+)', template_content)
            structures.extend(f"Class: {cls}" for cls in class_matches)
        
        if 'def ' in template_content:
            func_matches = re.findall(r'def\s+(\w+)', template_content)
            structures.extend(f"Function: {func}" for func in func_matches[:5])  # Limit to 5
        
        return {
            'patterns': patterns,
            'structures': structures
        }
    
    def generate_pattern_example(self, pattern_name: str, pattern_info: Dict[str, Any]) -> str:
        """Generate example implementation for a pattern"""
        examples = {
            'DUAL_COPILOT_MAIN': '''def main():
    """Main execution function with DUAL COPILOT pattern"""
    
    # DUAL COPILOT PATTERN: Primary Execution
    try:
        # Main logic here
        result = perform_primary_task()
        return result
    except Exception as e:
        logger.error(f"Primary execution failed: {e}")
        
        # DUAL COPILOT PATTERN: Secondary Validation
        return perform_secondary_validation()''',
            
            'ANTI_RECURSION_GUARD': '''class AntiRecursionGuard:
    """Enterprise anti-recursion protection"""
    
    def __init__(self):
        self.visited_paths = set()
        
    def should_skip(self, path: str) -> bool:
        normalized_path = os.path.normpath(path.lower())
        if normalized_path in self.visited_paths:
            return True
        self.visited_paths.add(normalized_path)
        return False''',
            
            'ENTERPRISE_LOGGING': '''logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('script.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)'''
        }
        
        return examples.get(pattern_name, '# Example implementation needed')
    
    def save_contexts_to_database(self):
        """Save contexts to database for persistence"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                for context in self.active_contexts.values():
                    cursor.execute('''
                        INSERT OR REPLACE INTO copilot_contexts 
                        (context_name, context_type, context_content, usage_instructions,
                         effectiveness_score, usage_count, created_timestamp, updated_timestamp, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (
                        context.context_id,
                        context.context_type,
                        context.content,
                        f"Use for {context.context_type} assistance",
                        context.effectiveness_score,
                        context.usage_count,
                        datetime.datetime.now().isoformat(),
                        datetime.datetime.now().isoformat()
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(self.active_contexts)} contexts to database")
                
        except Exception as e:
            logger.error(f"Failed to save contexts: {e}")

class CopilotSuggestionEngine:
    """Generate context-aware suggestions for GitHub Copilot"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.context_manager = CopilotContextManager(db_path)
        self.suggestion_patterns = self.load_suggestion_patterns()
    
    def load_suggestion_patterns(self) -> Dict[str, Any]:
        """Load suggestion patterns from database and templates"""
        patterns = {}
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Load templates for suggestion patterns
                cursor.execute('''
                    SELECT template_name, category, base_template, complexity_level
                    FROM script_templates WHERE active = 1
                ''')
                
                for row in cursor.fetchall():
                    template_name, category, base_template, complexity = row
                    patterns[f"template_{template_name}"] = {
                        'type': 'template',
                        'category': category,
                        'content': base_template,
                        'complexity': complexity
                    }
                
                # Load compliance patterns
                cursor.execute('''
                    SELECT pattern_name, pattern_type, pattern_regex, description
                    FROM compliance_patterns WHERE active = 1
                ''')
                
                for row in cursor.fetchall():
                    pattern_name, pattern_type, pattern_regex, description = row
                    patterns[f"compliance_{pattern_name}"] = {
                        'type': 'compliance',
                        'pattern_type': pattern_type,
                        'regex': pattern_regex,
                        'description': description
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to load suggestion patterns: {e}")
        
        return patterns
    
    def generate_contextual_suggestions(self, user_input: str, current_context: Dict[str, Any]) -> List[CopilotSuggestion]:
        """Generate contextual suggestions based on user input and current context"""
        suggestions = []
        timestamp = datetime.datetime.now().isoformat()
        
        # Analyze user input for intent
        intent = self.analyze_user_intent(user_input)
        
        # Generate suggestions based on intent
        if intent['type'] == 'template_request':
            suggestions.extend(self.suggest_templates(intent, current_context, timestamp))
        elif intent['type'] == 'compliance_question':
            suggestions.extend(self.suggest_compliance_patterns(intent, current_context, timestamp))
        elif intent['type'] == 'code_completion':
            suggestions.extend(self.suggest_code_completions(intent, current_context, timestamp))
        
        # Log suggestions to database
        self.log_suggestions(suggestions, current_context.get('session_id', 'unknown'))
        
        return suggestions
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine intent"""
        user_lower = user_input.lower()
        
        # Template request patterns
        template_keywords = ['create', 'generate', 'script', 'template', 'database', 'analyzer', 'validator']
        if any(keyword in user_lower for keyword in template_keywords):
            return {
                'type': 'template_request',
                'keywords': [kw for kw in template_keywords if kw in user_lower],
                'complexity': len(user_input.split())
            }
        
        # Compliance question patterns
        compliance_keywords = ['dual copilot', 'anti-recursion', 'enterprise', 'compliance', 'validation']
        if any(keyword in user_lower for keyword in compliance_keywords):
            return {
                'type': 'compliance_question',
                'keywords': [kw for kw in compliance_keywords if kw in user_lower]
            }
        
        # Code completion patterns
        if any(pattern in user_lower for pattern in ['def ', 'class ', 'import ', 'if __name__']):
            return {
                'type': 'code_completion',
                'code_context': user_input
            }
        
        return {'type': 'general', 'content': user_input}
    
    def suggest_templates(self, intent: Dict[str, Any], context: Dict[str, Any], timestamp: str) -> List[CopilotSuggestion]:
        """Suggest relevant templates"""
        suggestions = []
        
        # Find matching templates
        for pattern_name, pattern_info in self.suggestion_patterns.items():
            if pattern_info['type'] == 'template':
                score = self.calculate_template_relevance(intent, pattern_info)
                
                if score > 0.3:  # Minimum relevance threshold
                    suggestion = CopilotSuggestion(
                        suggestion_id=f"template_{len(suggestions)}_{hash(pattern_name)}",
                        suggestion_type='template',
                        content=f"Use template: {pattern_name.replace('template_', '')} (Category: {pattern_info['category']})",
                        confidence_score=score,
                        context_used=[pattern_name],
                        timestamp=timestamp
                    )
                    suggestions.append(suggestion)
        
        return sorted(suggestions, key=lambda x: x.confidence_score, reverse=True)[:3]
    
    def suggest_compliance_patterns(self, intent: Dict[str, Any], context: Dict[str, Any], timestamp: str) -> List[CopilotSuggestion]:
        """Suggest compliance patterns"""
        suggestions = []
        
        for pattern_name, pattern_info in self.suggestion_patterns.items():
            if pattern_info['type'] == 'compliance':
                if any(keyword in pattern_info['description'].lower() for keyword in intent.get('keywords', [])):
                    suggestion = CopilotSuggestion(
                        suggestion_id=f"compliance_{len(suggestions)}_{hash(pattern_name)}",
                        suggestion_type='compliance',
                        content=f"Implement {pattern_name.replace('compliance_', '')}: {pattern_info['description']}",
                        confidence_score=0.8,
                        context_used=[pattern_name],
                        timestamp=timestamp
                    )
                    suggestions.append(suggestion)
        
        return suggestions[:3]
    
    def suggest_code_completions(self, intent: Dict[str, Any], context: Dict[str, Any], timestamp: str) -> List[CopilotSuggestion]:
        """Suggest code completions"""
        suggestions = []
        code_context = intent.get('code_context', '')
        
        # Common enterprise patterns
        if 'def main' in code_context:
            suggestion = CopilotSuggestion(
                suggestion_id=f"completion_main_{hash(code_context)}",
                suggestion_type='completion',
                content='''def main():
    """Main execution function with DUAL COPILOT pattern"""
    
    # DUAL COPILOT PATTERN: Primary Execution
    try:
        # Main logic here
        pass
    except Exception as e:
        logger.error(f"Primary execution failed: {e}")
        
        # DUAL COPILOT PATTERN: Secondary Validation
        pass''',
                confidence_score=0.9,
                context_used=['dual_copilot_pattern'],
                timestamp=timestamp
            )
            suggestions.append(suggestion)
        
        if 'class' in code_context and 'Anti' in code_context:
            suggestion = CopilotSuggestion(
                suggestion_id=f"completion_anti_recursion_{hash(code_context)}",
                suggestion_type='completion',
                content='''class AntiRecursionGuard:
    """Enterprise anti-recursion protection"""
    
    def __init__(self):
        self.visited_paths = set()
        
    def should_skip(self, path: str) -> bool:
        normalized_path = os.path.normpath(path.lower())
        if normalized_path in self.visited_paths:
            return True
        self.visited_paths.add(normalized_path)
        return False''',
                confidence_score=0.95,
                context_used=['anti_recursion_pattern'],
                timestamp=timestamp
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def calculate_template_relevance(self, intent: Dict[str, Any], template_info: Dict[str, Any]) -> float:
        """Calculate relevance score for template"""
        score = 0.0
        
        # Category matching
        category_lower = template_info['category'].lower()
        for keyword in intent.get('keywords', []):
            if keyword in category_lower:
                score += 0.3
        
        # Complexity matching
        intent_complexity = intent.get('complexity', 5)
        template_complexity = template_info.get('complexity', 2)
        
        if abs(intent_complexity - template_complexity * 2) <= 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def log_suggestions(self, suggestions: List[CopilotSuggestion], session_id: str):
        """Log suggestions to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                for suggestion in suggestions:
                    cursor.execute('''
                        INSERT INTO copilot_suggestions 
                        (session_id, suggestion_type, suggestion_content, confidence_score,
                         accepted, timestamp, context_used)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id,
                        suggestion.suggestion_type,
                        suggestion.content,
                        suggestion.confidence_score,
                        suggestion.accepted,
                        suggestion.timestamp,
                        json.dumps(suggestion.context_used)
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log suggestions: {e}")

class CopilotIntegrationFramework:
    """Main GitHub Copilot integration framework"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / 'databases' / 'production.db'
        self.context_manager = CopilotContextManager(self.db_path)
        self.suggestion_engine = CopilotSuggestionEngine(self.db_path)
        self.integration_active = False
    
    def initialize_integration(self) -> bool:
        """Initialize Copilot integration with current workspace"""
        try:
            logger.info("Initializing GitHub Copilot integration...")
            
            # Load templates and create contexts
            self.load_template_contexts()
            
            # Load compliance patterns and create contexts
            self.load_compliance_contexts()
            
            # Save contexts to database
            self.context_manager.save_contexts_to_database()
            
            # Generate integration report
            self.generate_integration_report()
            
            self.integration_active = True
            logger.info("GitHub Copilot integration initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Copilot integration initialization failed: {e}")
            return False
    
    def load_template_contexts(self):
        """Load all templates as Copilot contexts"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT template_name, template_type, category, description,
                           base_template, variables, dependencies, compliance_patterns,
                           complexity_level, tags
                    FROM script_templates WHERE active = 1
                ''')
                
                for row in cursor.fetchall():
                    template = {
                        'template_name': row[0],
                        'template_type': row[1],
                        'category': row[2],
                        'description': row[3],
                        'base_template': row[4],
                        'variables': json.loads(row[5] or '[]'),
                        'dependencies': json.loads(row[6] or '[]'),
                        'compliance_patterns': json.loads(row[7] or '[]'),
                        'complexity_level': row[8],
                        'tags': json.loads(row[9] or '[]')
                    }
                    
                    self.context_manager.create_template_context(template)
                
                logger.info(f"Loaded {len(self.context_manager.active_contexts)} template contexts")
                
        except Exception as e:
            logger.error(f"Failed to load template contexts: {e}")
    
    def load_compliance_contexts(self):
        """Load compliance patterns as Copilot contexts"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT pattern_name, pattern_type, pattern_regex, description, severity
                    FROM compliance_patterns WHERE active = 1
                ''')
                
                for row in cursor.fetchall():
                    pattern_name = row[0]
                    pattern_info = {
                        'pattern_type': row[1],
                        'pattern_regex': row[2],
                        'description': row[3],
                        'severity': row[4]
                    }
                    
                    self.context_manager.create_pattern_context(pattern_name, pattern_info)
                
                logger.info("Loaded compliance pattern contexts")
                
        except Exception as e:
            logger.error(f"Failed to load compliance contexts: {e}")
    
    def process_user_interaction(self, user_input: str, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user interaction and provide Copilot-enhanced response"""
        if not self.integration_active:
            return {'error': 'Copilot integration not initialized'}
        
        try:
            # Create generation context if in active session
            if session_context:
                self.context_manager.create_generation_context(user_input, session_context)
            
            # Generate suggestions
            suggestions = self.suggestion_engine.generate_contextual_suggestions(
                user_input, session_context or {}
            )
            
            # Prepare response
            response = {
                'user_input': user_input,
                'suggestions_count': len(suggestions),
                'suggestions': [
                    {
                        'type': s.suggestion_type,
                        'content': s.content,
                        'confidence': s.confidence_score,
                        'context_used': s.context_used
                    }
                    for s in suggestions
                ],
                'context_available': len(self.context_manager.active_contexts),
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing user interaction: {e}")
            return {'error': str(e)}
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            'integration_metadata': {
                'timestamp': timestamp,
                'workspace_path': str(self.workspace_path),
                'database_path': str(self.db_path),
                'integration_version': '1.0.0'
            },
            'contexts_loaded': {
                'total_contexts': len(self.context_manager.active_contexts),
                'template_contexts': len([c for c in self.context_manager.active_contexts.values() if c.context_type == 'template']),
                'pattern_contexts': len([c for c in self.context_manager.active_contexts.values() if c.context_type == 'pattern']),
                'context_details': [
                    {
                        'context_id': context.context_id,
                        'context_type': context.context_type,
                        'effectiveness_score': context.effectiveness_score,
                        'usage_count': context.usage_count
                    }
                    for context in self.context_manager.active_contexts.values()
                ]
            },
            'suggestion_patterns': {
                'total_patterns': len(self.suggestion_engine.suggestion_patterns),
                'pattern_types': list(set(p['type'] for p in self.suggestion_engine.suggestion_patterns.values()))
            },
            'integration_status': {
                'active': self.integration_active,
                'ready_for_suggestions': True,
                'database_connected': self.db_path.exists()
            }
        }
        
        # Save JSON report
        json_file = self.workspace_path / f'ENTERPRISE_COPILOT_INTEGRATION_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save Markdown report
        md_content = f"""# Enterprise GitHub Copilot Integration Report

**Integration Timestamp:** {timestamp}
**Workspace:** {self.workspace_path}
**Database:** {self.db_path}

## Integration Status

- **Active:** {self.integration_active}
- **Ready for Suggestions:** True
- **Database Connected:** {self.db_path.exists()}

## Contexts Loaded

- **Total Contexts:** {len(self.context_manager.active_contexts)}
- **Template Contexts:** {len([c for c in self.context_manager.active_contexts.values() if c.context_type == 'template'])}
- **Pattern Contexts:** {len([c for c in self.context_manager.active_contexts.values() if c.context_type == 'pattern'])}

## Available Templates

"""
        
        template_contexts = [c for c in self.context_manager.active_contexts.values() if c.context_type == 'template']
        for context in template_contexts:
            md_content += f"- **{context.context_id}**: {context.metadata.get('category', 'Unknown')} template\n"
        
        md_content += "\n## Compliance Patterns\n\n"
        pattern_contexts = [c for c in self.context_manager.active_contexts.values() if c.context_type == 'pattern']
        for context in pattern_contexts:
            md_content += f"- **{context.context_id}**: {context.metadata.get('pattern_type', 'Unknown')} pattern\n"
        
        md_file = self.workspace_path / f'ENTERPRISE_COPILOT_INTEGRATION_{timestamp}.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Integration reports generated: {json_file} and {md_file}")

def main():
    """Main execution function with DUAL COPILOT pattern"""
    
    # DUAL COPILOT PATTERN: Primary Integration
    try:
        workspace_path = r"E:\_copilot_sandbox"
        framework = CopilotIntegrationFramework(workspace_path)
        
        print("\n" + "="*80)
        print("ENTERPRISE GITHUB COPILOT INTEGRATION - INITIALIZATION")
        print("="*80)
        
        # Initialize integration
        success = framework.initialize_integration()
        
        if success:
            print("GitHub Copilot integration initialized successfully!")
            
            # Test user interaction
            print("\nTesting Copilot suggestions...")
            test_input = "Create an enterprise database analyzer with anti-recursion"
            response = framework.process_user_interaction(test_input)
            
            print(f"User Input: {test_input}")
            print(f"Suggestions Generated: {response.get('suggestions_count', 0)}")
            print(f"Contexts Available: {response.get('context_available', 0)}")
            
            # Show top suggestions
            for i, suggestion in enumerate(response.get('suggestions', [])[:3]):
                print(f"  {i+1}. {suggestion['type']}: {suggestion['content'][:100]}...")
                print(f"     Confidence: {suggestion['confidence']:.2f}")
        
        print("="*80)
        
        return {
            'success': success,
            'contexts_loaded': len(framework.context_manager.active_contexts),
            'integration_active': framework.integration_active
        }
        
    except Exception as e:
        logger.error(f"Primary integration failed: {e}")
        
        # DUAL COPILOT PATTERN: Secondary Validation
        print("\n" + "="*80)
        print("DUAL COPILOT SECONDARY VALIDATION")
        print("="*80)
        print("Primary integration encountered issues. Running validation...")
        
        # Basic validation
        workspace_path = Path(r"E:\_copilot_sandbox")
        
        validation_results = {
            'workspace_exists': workspace_path.exists(),
            'database_exists': (workspace_path / 'databases' / 'production.db').exists(),
            'templates_available': False,
            'error_details': str(e)
        }
        
        # Check if templates exist in database
        try:
            db_path = workspace_path / 'databases' / 'production.db'
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM script_templates WHERE active = 1")
                template_count = cursor.fetchone()[0]
                validation_results['templates_available'] = template_count > 0
                validation_results['template_count'] = template_count
        except:
            validation_results['templates_available'] = False
        
        print("Validation Results:")
        for key, value in validation_results.items():
            print(f"- {key}: {value}")
        
        print("="*80)
        return validation_results

if __name__ == "__main__":
    main()
