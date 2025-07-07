#!/usr/bin/env python3
"""
GitHub Copilot Enterprise Integration Framework
Advanced integration system for seamless GitHub Copilot enhancement

Features:
- Web-to-VSCode Copilot communication bridge
- Context-aware prompt generation
- Intelligent prompt templating
- Session persistence and conversation history
- Real-time integration monitoring
- Enterprise security and compliance

Version: 1.0.0
Created: 2025-07-06
"""

import os
import sys
import json
import asyncio
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import requests
import uuid
import time

# Try to import websockets, fallback if not available
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("⚠️ websockets module not available - WebSocket functionality disabled")

# Professional logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_copilot_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CopilotPrompt:
    """Copilot prompt structure"""
    id: str
    session_id: str
    prompt_type: str
    context: str
    content: str
    created_at: datetime
    status: str = "PENDING"
    response: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CopilotSession:
    """Copilot session structure"""
    session_id: str
    user_id: str
    workspace_path: str
    created_at: datetime
    last_activity: datetime
    prompt_count: int = 0
    active: bool = True

class GitHubCopilotIntegrationFramework:
    """Enterprise GitHub Copilot integration framework"""
    
    def __init__(self, deployment_path: str = "e:/gh_COPILOT"):
        self.deployment_path = Path(deployment_path)
        self.integration_db_path = self.deployment_path / "github_integration" / "copilot_integration.db"
        self.websocket_server = None
        self.websocket_port = 8765
        self.active_sessions: Dict[str, CopilotSession] = {}
        self.prompt_templates: Dict[str, str] = {}
        
        # Integration configuration
        self.integration_config = {
            "websocket_port": 8765,
            "max_sessions": 100,
            "session_timeout": 3600,  # 1 hour
            "prompt_timeout": 300,    # 5 minutes
            "context_max_length": 10000,
            "response_max_length": 50000,
            "supported_prompt_types": [
                "code_generation",
                "code_review",
                "documentation",
                "debugging",
                "optimization",
                "testing",
                "refactoring",
                "explanation"
            ]
        }
        
        # Initialize integration system
        self.init_integration_database()
        self.load_prompt_templates()
    
    def init_integration_database(self):
        """Initialize GitHub Copilot integration database"""
        try:
            # Create database directory
            self.integration_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS copilot_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    workspace_path TEXT,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    prompt_count INTEGER DEFAULT 0,
                    active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create prompts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS copilot_prompts (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    prompt_type TEXT NOT NULL,
                    context TEXT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',
                    response TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES copilot_sessions (session_id)
                )
            """)
            
            # Create prompt templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT UNIQUE NOT NULL,
                    template_type TEXT NOT NULL,
                    template_content TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create integration metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS integration_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    session_id TEXT,
                    additional_data TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ GitHub Copilot integration database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing integration database: {e}")
    
    def load_prompt_templates(self):
        """Load prompt templates from database and files"""
        try:
            # Load from database
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT template_name, template_content FROM prompt_templates")
            db_templates = cursor.fetchall()
            
            for template_name, template_content in db_templates:
                self.prompt_templates[template_name] = template_content
            
            conn.close()
            
            # Load default templates if none exist
            if not self.prompt_templates:
                self.create_default_templates()
            
            logger.info(f"✅ Loaded {len(self.prompt_templates)} prompt templates")
            
        except Exception as e:
            logger.error(f"❌ Error loading prompt templates: {e}")
    
    def create_default_templates(self):
        """Create default prompt templates"""
        default_templates = {
            "code_generation": """@GitHub Copilot - Code Generation Request

**Context**: {context}
**Task**: Generate code for the following requirement:

{content}

**Requirements**:
- Follow best practices and enterprise standards
- Include proper error handling
- Add comprehensive documentation
- Ensure code is production-ready
- Apply DUAL COPILOT validation pattern

**Output Format**: Complete, functional code with comments""",

            "code_review": """@GitHub Copilot - Code Review Request

**Context**: {context}
**Code to Review**:
```
{content}
```

**Review Focus**:
- Code quality and best practices
- Security vulnerabilities
- Performance optimization opportunities
- Documentation completeness
- Enterprise compliance

**Output Format**: Detailed review with specific recommendations""",

            "documentation": """@GitHub Copilot - Documentation Generation

**Context**: {context}
**Subject**: {content}

**Documentation Requirements**:
- Comprehensive technical documentation
- User-friendly explanations
- API reference if applicable
- Usage examples
- Troubleshooting guide
- Enterprise standards compliance

**Output Format**: Well-structured markdown documentation""",

            "debugging": """@GitHub Copilot - Debugging Assistant

**Context**: {context}
**Issue Description**: {content}

**Debug Analysis Needed**:
- Root cause identification
- Step-by-step debugging approach
- Potential fixes and solutions
- Prevention strategies
- Testing recommendations

**Output Format**: Structured debugging plan with actionable steps""",

            "optimization": """@GitHub Copilot - Performance Optimization

**Context**: {context}
**Target**: {content}

**Optimization Goals**:
- Performance improvements
- Resource efficiency
- Scalability enhancements
- Best practice implementation
- Enterprise-grade optimization

**Output Format**: Detailed optimization recommendations with implementation steps""",

            "testing": """@GitHub Copilot - Test Generation

**Context**: {context}
**Code/Feature to Test**:
```
{content}
```

**Testing Requirements**:
- Unit tests with high coverage
- Integration tests
- Edge case handling
- Error condition testing
- Performance testing considerations

**Output Format**: Comprehensive test suite with multiple test scenarios""",

            "refactoring": """@GitHub Copilot - Code Refactoring

**Context**: {context}
**Code to Refactor**:
```
{content}
```

**Refactoring Goals**:
- Improve code maintainability
- Enhance readability
- Apply design patterns
- Reduce complexity
- Enterprise architecture compliance

**Output Format**: Refactored code with explanation of changes""",

            "explanation": """@GitHub Copilot - Code Explanation

**Context**: {context}
**Code to Explain**:
```
{content}
```

**Explanation Requirements**:
- Clear, step-by-step breakdown
- Explain design patterns used
- Highlight key concepts
- Identify potential improvements
- Educational focus

**Output Format**: Detailed explanation suitable for learning"""
        }
        
        # Save default templates to database
        try:
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            for template_name, template_content in default_templates.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO prompt_templates 
                    (template_name, template_type, template_content, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    template_name,
                    template_name.replace('_', ' ').title(),
                    template_content,
                    f"Default template for {template_name.replace('_', ' ')}",
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
            self.prompt_templates = default_templates
            
            logger.info("✅ Created default prompt templates")
            
        except Exception as e:
            logger.error(f"❌ Error creating default templates: {e}")
    
    def create_session(self, user_id: str, workspace_path: str = None) -> str:
        """Create new Copilot session"""
        try:
            session_id = str(uuid.uuid4())
            session = CopilotSession(
                session_id=session_id,
                user_id=user_id,
                workspace_path=workspace_path or str(self.deployment_path),
                created_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            # Store in memory
            self.active_sessions[session_id] = session
            
            # Store in database
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO copilot_sessions 
                (session_id, user_id, workspace_path, created_at, last_activity, prompt_count, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.workspace_path,
                session.created_at.isoformat(),
                session.last_activity.isoformat(),
                session.prompt_count,
                session.active
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created Copilot session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}")
            return None
    
    def update_session_activity(self, session_id: str):
        """Update session last activity"""
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].last_activity = datetime.now()
                
                # Update database
                conn = sqlite3.connect(self.integration_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE copilot_sessions 
                    SET last_activity = ? 
                    WHERE session_id = ?
                """, (datetime.now().isoformat(), session_id))
                
                conn.commit()
                conn.close()
        
        except Exception as e:
            logger.error(f"❌ Error updating session activity: {e}")
    
    def generate_context_aware_prompt(self, session_id: str, prompt_type: str, content: str, 
                                    current_file: str = None, workspace_context: Dict = None) -> str:
        """Generate context-aware prompt for GitHub Copilot"""
        try:
            # Get session info
            session = self.active_sessions.get(session_id)
            if not session:
                logger.error(f"❌ Session not found: {session_id}")
                return content
            
            # Build context
            context_parts = []
            
            # Workspace context
            if workspace_context:
                context_parts.append(f"Workspace: {workspace_context.get('workspace_name', 'Unknown')}")
                if workspace_context.get('project_type'):
                    context_parts.append(f"Project Type: {workspace_context['project_type']}")
            
            # Current file context
            if current_file:
                context_parts.append(f"Current File: {current_file}")
                
                # Try to get file info
                try:
                    file_path = Path(current_file)
                    if file_path.exists():
                        file_ext = file_path.suffix
                        context_parts.append(f"File Type: {file_ext}")
                        
                        # Add file size if reasonable
                        file_size = file_path.stat().st_size
                        if file_size < 100000:  # Less than 100KB
                            context_parts.append(f"File Size: {file_size} bytes")
                except:
                    pass
            
            # Session context
            context_parts.append(f"Session: {session_id[:8]}...")
            context_parts.append(f"User: {session.user_id}")
            
            # Build complete context
            context = " | ".join(context_parts)
            
            # Get template
            template = self.prompt_templates.get(prompt_type, "{content}")
            
            # Generate prompt
            formatted_prompt = template.format(
                context=context,
                content=content
            )
            
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"❌ Error generating context-aware prompt: {e}")
            return content
    
    def create_prompt(self, session_id: str, prompt_type: str, content: str, 
                     context: str = None, metadata: Dict = None) -> str:
        """Create new Copilot prompt"""
        try:
            prompt_id = str(uuid.uuid4())
            
            # Generate context-aware prompt if context not provided
            if not context and session_id in self.active_sessions:
                context = f"Session: {session_id}, Workspace: {self.active_sessions[session_id].workspace_path}"
            
            prompt = CopilotPrompt(
                id=prompt_id,
                session_id=session_id,
                prompt_type=prompt_type,
                context=context or "",
                content=content,
                created_at=datetime.now(),
                metadata=metadata
            )
            
            # Store in database
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO copilot_prompts 
                (id, session_id, prompt_type, context, content, created_at, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt.id,
                prompt.session_id,
                prompt.prompt_type,
                prompt.context,
                prompt.content,
                prompt.created_at.isoformat(),
                prompt.status,
                json.dumps(prompt.metadata) if prompt.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
            # Update session activity and prompt count
            if session_id in self.active_sessions:
                self.active_sessions[session_id].prompt_count += 1
                self.update_session_activity(session_id)
            
            logger.info(f"✅ Created Copilot prompt: {prompt_id}")
            return prompt_id
            
        except Exception as e:
            logger.error(f"❌ Error creating prompt: {e}")
            return None
    
    def update_prompt_response(self, prompt_id: str, response: str, status: str = "COMPLETED"):
        """Update prompt with response"""
        try:
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE copilot_prompts 
                SET response = ?, status = ? 
                WHERE id = ?
            """, (response, status, prompt_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Updated prompt response: {prompt_id}")
            
        except Exception as e:
            logger.error(f"❌ Error updating prompt response: {e}")
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get session prompt history"""
        try:
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, prompt_type, content, response, created_at, status 
                FROM copilot_prompts 
                WHERE session_id = ? 
                ORDER BY created_at DESC
            """, (session_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "prompt_type": row[1],
                    "content": row[2],
                    "response": row[3],
                    "created_at": row[4],
                    "status": row[5]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Error getting session history: {e}")
            return []
    
    def suggest_prompts(self, context: str, file_type: str = None) -> List[Dict]:
        """Suggest relevant prompts based on context"""
        try:
            suggestions = []
            
            # Analyze context for suggestions
            context_lower = context.lower()
            
            if any(word in context_lower for word in ['bug', 'error', 'issue', 'problem']):
                suggestions.append({
                    "type": "debugging",
                    "title": "Debug Issue",
                    "description": "Get help debugging the current issue"
                })
            
            if any(word in context_lower for word in ['optimize', 'performance', 'slow']):
                suggestions.append({
                    "type": "optimization",
                    "title": "Optimize Code",
                    "description": "Get optimization recommendations"
                })
            
            if any(word in context_lower for word in ['test', 'testing', 'unit test']):
                suggestions.append({
                    "type": "testing",
                    "title": "Generate Tests",
                    "description": "Create comprehensive test suite"
                })
            
            if any(word in context_lower for word in ['refactor', 'clean', 'improve']):
                suggestions.append({
                    "type": "refactoring",
                    "title": "Refactor Code",
                    "description": "Improve code structure and maintainability"
                })
            
            if any(word in context_lower for word in ['document', 'docs', 'readme']):
                suggestions.append({
                    "type": "documentation",
                    "title": "Generate Documentation",
                    "description": "Create comprehensive documentation"
                })
            
            # File type specific suggestions
            if file_type:
                if file_type.lower() in ['.py', '.js', '.ts', '.java', '.cpp']:
                    suggestions.append({
                        "type": "code_review",
                        "title": "Code Review",
                        "description": "Get detailed code review and recommendations"
                    })
            
            # Always include explanation option
            suggestions.append({
                "type": "explanation",
                "title": "Explain Code",
                "description": "Get detailed explanation of the code"
            })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error generating prompt suggestions: {e}")
            return []
    
    def collect_integration_metrics(self, metric_type: str, metric_value: float, 
                                  session_id: str = None, additional_data: Dict = None):
        """Collect integration metrics"""
        try:
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO integration_metrics 
                (metric_type, metric_value, timestamp, session_id, additional_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metric_type,
                metric_value,
                datetime.now().isoformat(),
                session_id,
                json.dumps(additional_data) if additional_data else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error collecting integration metrics: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.now()
            timeout_threshold = current_time.timestamp() - self.integration_config["session_timeout"]
            
            expired_sessions = []
            for session_id, session in self.active_sessions.items():
                if session.last_activity.timestamp() < timeout_threshold:
                    expired_sessions.append(session_id)
            
            # Remove expired sessions
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                
                # Update database
                conn = sqlite3.connect(self.integration_db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE copilot_sessions 
                    SET active = 0 
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
                conn.close()
            
            if expired_sessions:
                logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate integration usage and performance report"""
        try:
            conn = sqlite3.connect(self.integration_db_path)
            cursor = conn.cursor()
            
            # Session statistics
            cursor.execute("SELECT COUNT(*) FROM copilot_sessions")
            total_sessions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM copilot_sessions WHERE active = 1")
            active_sessions = cursor.fetchone()[0]
            
            # Prompt statistics
            cursor.execute("SELECT COUNT(*) FROM copilot_prompts")
            total_prompts = cursor.fetchone()[0]
            
            cursor.execute("SELECT prompt_type, COUNT(*) FROM copilot_prompts GROUP BY prompt_type")
            prompt_types = dict(cursor.fetchall())
            
            cursor.execute("SELECT status, COUNT(*) FROM copilot_prompts GROUP BY status")
            prompt_statuses = dict(cursor.fetchall())
            
            # Recent activity
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) 
                FROM copilot_prompts 
                WHERE created_at >= date('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            daily_activity = dict(cursor.fetchall())
            
            # Performance metrics
            cursor.execute("""
                SELECT metric_type, AVG(metric_value), MIN(metric_value), MAX(metric_value), COUNT(*)
                FROM integration_metrics 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY metric_type
            """)
            metrics_summary = {}
            for row in cursor.fetchall():
                metrics_summary[row[0]] = {
                    "average": row[1],
                    "minimum": row[2],
                    "maximum": row[3],
                    "count": row[4]
                }
            
            conn.close()
            
            report = {
                "report_generated": datetime.now().isoformat(),
                "session_statistics": {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "inactive_sessions": total_sessions - active_sessions
                },
                "prompt_statistics": {
                    "total_prompts": total_prompts,
                    "by_type": prompt_types,
                    "by_status": prompt_statuses
                },
                "activity_trends": {
                    "daily_activity_last_7_days": daily_activity
                },
                "performance_metrics": metrics_summary,
                "system_health": {
                    "database_accessible": True,
                    "integration_active": True,
                    "websocket_status": "running" if self.websocket_server else "stopped"
                }
            }
            
            # Save report
            report_file = self.deployment_path / "github_integration" / "integration_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Generate markdown report
            self.generate_integration_markdown_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating integration report: {e}")
            return {}
    
    def generate_integration_markdown_report(self, report: Dict[str, Any]):
        """Generate markdown integration report"""
        try:
            report_file = self.deployment_path / "github_integration" / "INTEGRATION_REPORT.md"
            
            markdown = f"""# GitHub Copilot Integration Report

Generated: {report['report_generated']}

## Session Statistics

- **Total Sessions**: {report['session_statistics']['total_sessions']}
- **Active Sessions**: {report['session_statistics']['active_sessions']}
- **Inactive Sessions**: {report['session_statistics']['inactive_sessions']}

## Prompt Statistics

- **Total Prompts**: {report['prompt_statistics']['total_prompts']}

### By Type
{chr(10).join(f"- **{ptype.replace('_', ' ').title()}**: {count}" for ptype, count in report['prompt_statistics']['by_type'].items())}

### By Status
{chr(10).join(f"- **{status}**: {count}" for status, count in report['prompt_statistics']['by_status'].items())}

## Activity Trends

### Daily Activity (Last 7 Days)
{chr(10).join(f"- **{date}**: {count} prompts" for date, count in report['activity_trends']['daily_activity_last_7_days'].items())}

## Performance Metrics

{chr(10).join(f"### {metric.replace('_', ' ').title()}" + chr(10) + f"- Average: {data['average']:.2f}" + chr(10) + f"- Min: {data['minimum']:.2f}" + chr(10) + f"- Max: {data['maximum']:.2f}" + chr(10) + f"- Count: {data['count']}" + chr(10) for metric, data in report['performance_metrics'].items())}

## System Health

- **Database**: {'✅ Accessible' if report['system_health']['database_accessible'] else '❌ Not accessible'}
- **Integration**: {'✅ Active' if report['system_health']['integration_active'] else '❌ Inactive'}
- **WebSocket**: {report['system_health']['websocket_status'].title()}

## Usage Recommendations

1. **Most Popular Prompt Types**: Focus on enhancing templates for frequently used types
2. **Session Management**: Monitor active sessions to optimize resource usage
3. **Performance**: Review metrics for optimization opportunities
4. **User Experience**: Analyze successful vs failed prompts for improvements

## Next Steps

1. Review prompt templates for optimization
2. Monitor performance metrics trends
3. Enhance context-aware prompt generation
4. Expand integration capabilities

---

*Report generated by GitHub Copilot Integration Framework*
"""
            
            with open(report_file, 'w') as f:
                f.write(markdown)
            
            logger.info(f"📄 Integration markdown report generated: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Error generating markdown report: {e}")
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections for real-time integration"""
        try:
            logger.info("🔌 New WebSocket connection established")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    command = data.get('command')
                    
                    if command == 'create_session':
                        session_id = self.create_session(
                            user_id=data.get('user_id', 'anonymous'),
                            workspace_path=data.get('workspace_path')
                        )
                        await websocket.send(json.dumps({
                            'type': 'session_created',
                            'session_id': session_id
                        }))
                    
                    elif command == 'generate_prompt':
                        prompt_id = self.create_prompt(
                            session_id=data.get('session_id'),
                            prompt_type=data.get('prompt_type'),
                            content=data.get('content'),
                            context=data.get('context'),
                            metadata=data.get('metadata')
                        )
                        
                        # Generate context-aware prompt
                        enhanced_prompt = self.generate_context_aware_prompt(
                            session_id=data.get('session_id'),
                            prompt_type=data.get('prompt_type'),
                            content=data.get('content'),
                            current_file=data.get('current_file'),
                            workspace_context=data.get('workspace_context')
                        )
                        
                        await websocket.send(json.dumps({
                            'type': 'prompt_generated',
                            'prompt_id': prompt_id,
                            'enhanced_prompt': enhanced_prompt
                        }))
                    
                    elif command == 'get_suggestions':
                        suggestions = self.suggest_prompts(
                            context=data.get('context', ''),
                            file_type=data.get('file_type')
                        )
                        await websocket.send(json.dumps({
                            'type': 'suggestions',
                            'suggestions': suggestions
                        }))
                    
                    elif command == 'get_history':
                        history = self.get_session_history(data.get('session_id'))
                        await websocket.send(json.dumps({
                            'type': 'session_history',
                            'history': history
                        }))
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 WebSocket connection closed")
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
    
    def start_websocket_server(self):
        """Start WebSocket server for real-time integration"""
        try:
            logger.info(f"🚀 Starting WebSocket server on port {self.websocket_port}...")
            
            start_server = websockets.serve(
                self.websocket_handler,
                "localhost",
                self.websocket_port
            )
            
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
            
        except Exception as e:
            logger.error(f"❌ Error starting WebSocket server: {e}")
    
    def start_integration_service(self):
        """Start the complete integration service"""
        try:
            logger.info("🚀 Starting GitHub Copilot Integration Service...")
            
            # Start cleanup scheduler
            def periodic_cleanup():
                while True:
                    time.sleep(300)  # Clean up every 5 minutes
                    self.cleanup_expired_sessions()
            
            cleanup_thread = threading.Thread(target=periodic_cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            # Start WebSocket server
            self.start_websocket_server()
            
        except KeyboardInterrupt:
            logger.info("⏹️ Shutting down integration service...")
        except Exception as e:
            logger.error(f"❌ Error in integration service: {e}")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Copilot Enterprise Integration Framework')
    parser.add_argument('--path', default='e:/gh_COPILOT', help='Deployment path')
    parser.add_argument('--port', type=int, default=8765, help='WebSocket server port')
    parser.add_argument('--start-service', action='store_true', help='Start integration service')
    parser.add_argument('--generate-report', action='store_true', help='Generate integration report')
    parser.add_argument('--create-templates', action='store_true', help='Create default templates')
    
    args = parser.parse_args()
    
    # Initialize integration framework
    framework = GitHubCopilotIntegrationFramework(args.path)
    framework.websocket_port = args.port
    
    if args.start_service:
        # Start integration service
        framework.start_integration_service()
    elif args.generate_report:
        # Generate integration report
        report = framework.generate_integration_report()
        print(f"✅ Integration report generated: {json.dumps(report, indent=2)}")
    elif args.create_templates:
        # Create default templates
        framework.create_default_templates()
        print("✅ Default templates created")
    else:
        print("GitHub Copilot Enterprise Integration Framework")
        print("Available commands:")
        print("  --start-service    Start integration service")
        print("  --generate-report  Generate integration report")
        print("  --create-templates Create default templates")

if __name__ == "__main__":
    main()
