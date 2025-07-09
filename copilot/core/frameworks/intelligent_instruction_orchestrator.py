#!/usr/bin/env python3
"""
[TARGET] INTELLIGENT INSTRUCTION SET ORCHESTRATOR
Autonomous GitHub Copilot Instruction Management System

MANDATORY: Apply database-first instruction selection with enterprise intelligence
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InstructionSet:
    """Instruction set metadata"""
    name: str
    file_path: str
    category: str
    priority: int
    dependencies: List[str]
    activation_triggers: List[str]
    usage_count: int
    last_used: Optional[datetime]
    effectiveness_score: float


@dataclass
class TaskContext:
    """Task context for instruction selection"""
    task_type: str
    complexity_level: str
    required_capabilities: List[str]
    user_preferences: Dict[str, str]
    session_history: List[str]


class IntelligentInstructionOrchestrator:
    """
    [ANALYSIS] INTELLIGENT INSTRUCTION SET ORCHESTRATOR
    Autonomous instruction selection with database-first intelligence
    """

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.instructions_dir = Path()
self.workspace_root) / '.github' / 'instructions'
        self.db_path = Path(self.workspace_root)
            / 'instruction_orchestrator.db'

        # Initialize database
        self._initialize_database()

        # Load instruction sets
        self.instruction_sets: Dict[str, InstructionSet] = {}
        self._load_instruction_sets()

        # Define instruction categories and relationships
        self._define_instruction_relationships()

        logger.info(
            f"[TARGET] Orchestrator initialized with {len(self.instruction_sets)} instruction sets")

    def _initialize_database(self):
        """Initialize instruction orchestrator database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            )
        """)

        cursor.execute(
            )
        """)

        cursor.execute(
            )
        """)

        conn.commit()
        conn.close()

    def _load_instruction_sets(self):
        """Load and analyze instruction sets from filesystem"""
        if not self.instructions_dir.exists():
            logger.warning("Instructions directory not found")
            return

        instruction_files = list(self.instructions_dir.glob('*.md'))

        for file_path in instruction_files:
            try:
                instruction_set = self._analyze_instruction_file(file_path)
                self.instruction_sets[instruction_set.name] = instruction_set
                logger.info(f"[CLIPBOARD] Loaded: {instruction_set.name}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to load {file_path}: {str(e)}")

    def _analyze_instruction_file(self, file_path: Path) -> InstructionSet:
        """Analyze instruction file and extract metadata"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract name from filename
        name = file_path.stem.replace('.instructions', '')

        # Analyze content for triggers and dependencies
        triggers = self._extract_activation_triggers(content)
        dependencies = self._extract_dependencies(content)
        category = self._determine_category(name, content)
        priority = self._calculate_priority(name, content)

        # Get usage statistics from database
        usage_stats = self._get_usage_statistics(name)

        return InstructionSet(]
            file_path=str(file_path),
            category=category,
            priority=priority,
            dependencies=dependencies,
            activation_triggers=triggers,
            usage_count=usage_stats.get('usage_count', 0),
            last_used=usage_stats.get('last_used'),
            effectiveness_score=usage_stats.get('effectiveness_score', 0.8)
        )

    def _extract_activation_triggers(self, content: str) -> List[str]:
        """Extract activation triggers from instruction content"""
        triggers = [

        # Look for common trigger patterns
        trigger_patterns = [
            r'when.*(?:file|database|web|visual|processing|enterprise)',
            r'mandatory.*(?:for|when|during)',
            r'required.*(?:for|when|during)',
            r'activate.*(?:for|when|during)'
        ]

        for pattern in trigger_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            triggers.extend(matches)

        # Add category-specific triggers
        if 'FILE_MANAGEMENT' in content:
            triggers.extend(['file_operations', 'backup', 'organization'])
        if 'VISUAL_PROCESSING' in content:
            triggers.extend(['progress_indicators', 'visual_feedback'])
        if 'ENTERPRISE' in content:
            triggers.extend(['enterprise_deployment', 'business_operations'])
        if 'QUANTUM' in content:
            triggers.extend(['optimization', 'advanced_processing'])
        if 'WEB_GUI' in content:
            triggers.extend(['web_interface', 'dashboard'])

        return list(set(triggers))

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from instruction content"""
        dependencies = [

        # Look for explicit dependencies
        dependency_patterns = [
            r'depends on.*?([A-Z_]+)',
            r'requires.*?([A-Z_]+)',
            r'must.*?([A-Z_]+)',
            r'leverage.*?([A-Z_]+)'
        ]

        for pattern in dependency_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dependencies.extend(matches)

        return list(set(dependencies))

    def _determine_category(self, name: str, content: str) -> str:
        """Determine instruction category"""
        if any(keyword in name.upper()
               for keyword in ['FILE', 'AUTONOMOUS', 'MANAGEMENT']):
            return 'CORE'
        elif any(keyword in name.upper() for keyword in ['VISUAL', 'PROCESSING', 'DUAL']):
            return 'PROCESSING'
        elif any(keyword in name.upper() for keyword in ['QUANTUM', 'ENHANCED', 'ADVANCED']):
            return 'ADVANCED'
        elif any(keyword in name.upper() for keyword in ['WEB', 'GUI', 'PHASE']):
            return 'SPECIALIZED'
        else:
            return 'GENERAL'

    def _calculate_priority(self, name: str, content: str) -> int:
        """Calculate instruction priority(1 - 10, higher is more important)"""
        priority = 5  # Default priority

        # Boost priority for critical instructions
        if 'MANDATORY' in content.upper():
            priority += 2
        if 'CRITICAL' in content.upper():
            priority += 2
        if 'ENTERPRISE' in content.upper():
            priority += 1
        if 'ZERO_TOLERANCE' in content.upper():
            priority += 3

        # Boost priority for frequently used instructions
        if any(keyword in name.upper()
               for keyword in ['SESSION', 'INTEGRITY', 'CONTEXT']):
            priority += 1

        return min(priority, 10)

    def _get_usage_statistics(self, instruction_name: str) -> Dict:
        """Get usage statistics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
                COUNT(*) as usage_count,
                AVG(effectiveness_score) as avg_effectiveness,
                MAX(usage_timestamp) as last_used
            FROM instruction_usage
            WHERE instruction_name = ?
        """, (instruction_name,))

        row = cursor.fetchone()
        conn.close()

        if row and row[0] > 0:
            return {]
                'usage_count': row[0],
                'effectiveness_score': row[1] or 0.8,
                'last_used': datetime.fromisoformat(row[2]) if row[2] else None
            }
        else:
            return {'usage_count': 0, 'effectiveness_score': 0.8, 'last_used': None}

    def _define_instruction_relationships(self):
        """Define relationships between instruction sets"""
        # Core instruction combinations
        self.instruction_combinations = {
            ],
            'enterprise_deployment': [],
            'advanced_processing': [],
            'web_development': [],
            'session_management': []
        }

    def suggest_instructions(self, task_context: TaskContext) -> List[Dict]:
        """
        [TARGET] Suggest optimal instruction sets for given task context

        Args:
            task_context: Task context information

        Returns:
            List of recommended instruction sets with confidence scores
        """
        logger.info(f"[TARGET] Analyzing task: {task_context.task_type}")

        # Get base recommendations
        base_recommendations = self._get_base_recommendations(task_context)

        # Apply machine learning insights
        ml_recommendations = self._apply_ml_insights(]
            task_context, base_recommendations)

        # Apply dependency resolution
        resolved_recommendations = self._resolve_dependencies(]
            ml_recommendations)

        # Calculate confidence scores
        final_recommendations = self._calculate_confidence_scores(]
            resolved_recommendations, task_context)

        # Sort by confidence and priority
        final_recommendations.sort(]
            x['confidence'], x['priority']), reverse = True)

        logger.info(
            f"[BAR_CHART] Generated {len(final_recommendations)} recommendations")
        return final_recommendations[:5]  # Return top 5

    def _get_base_recommendations(self, task_context: TaskContext) -> List[str]:
        """Get base recommendations from predefined patterns"""
        recommendations = [

        # Task type mapping
        task_mappings = {
            'file_operations': ['AUTONOMOUS_FILE_MANAGEMENT', 'COMPREHENSIVE_SESSION_INTEGRITY'],
            'web_development': ['WEB_GUI_INTEGRATION', 'ENTERPRISE_CONTEXT'],
            'enterprise_deployment': ['ENTERPRISE_CONTEXT', 'DUAL_COPILOT_PATTERN'],
            'optimization': ['QUANTUM_OPTIMIZATION', 'ENHANCED_COGNITIVE_PROCESSING'],
            'visual_processing': ['VISUAL_PROCESSING_INDICATORS', 'ZERO_TOLERANCE_VISUAL_PROCESSING'],
            'session_management': ['SESSION_TEMPLATES', 'ENHANCED_LEARNING_COPILOT']
        }

        # Get recommendations for task type
        if task_context.task_type in task_mappings:
            recommendations.extend(task_mappings[task_context.task_type])

        # Add capability-based recommendations
        for capability in task_context.required_capabilities:
            if capability in self.instruction_combinations:
                recommendations.extend(]
                    self.instruction_combinations[capability])

        return list(set(recommendations))

    def _apply_ml_insights(
    self,
    task_context: TaskContext,
     base_recommendations: List[str]) -> List[str]:
        """Apply machine learning insights from historical usage"""
        # Query database for similar tasks
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            SELECT instruction_name, AVG(effectiveness_score) as avg_score
            FROM instruction_usage
            WHERE task_type = ? OR context LIKE
            ? GROUP BY instruction_name
            ORDER BY avg_score DESC
            LIMIT 10
        """, (task_context.task_type, f"%{task_context.task_type}%"))

        ml_insights = cursor.fetchall()
        conn.close()

        # Add high-performing instructions
        for instruction_name, score in ml_insights:
            if score > 0.7 and instruction_name not in base_recommendations:
                base_recommendations.append(instruction_name)

        return base_recommendations

    def _resolve_dependencies(self, recommendations: List[str]) -> List[str]:
        """Resolve instruction dependencies"""
        resolved = set(recommendations)

        for instruction_name in recommendations:
            if instruction_name in self.instruction_sets:
                instruction = self.instruction_sets[instruction_name]
                for dependency in instruction.dependencies:
                    if dependency in self.instruction_sets:
                        resolved.add(dependency)

        return list(resolved)

    def _calculate_confidence_scores(
    self,
    recommendations: List[str],
     task_context: TaskContext) -> List[Dict]:
        """Calculate confidence scores for recommendations"""
        scored_recommendations = [

        for instruction_name in recommendations:
            if instruction_name not in self.instruction_sets:
                continue

            instruction = self.instruction_sets[instruction_name]

            # Base confidence from effectiveness score
            confidence = instruction.effectiveness_score

            # Boost confidence for frequently used instructions
            if instruction.usage_count > 10:
                confidence += 0.1

            # Boost confidence for high-priority instructions
            confidence += (instruction.priority / 10) * 0.2

            # Boost confidence for matching triggers
            trigger_matches = sum(]
                                  if any(req in trigger.lower() for req in task_context.required_capabilities))
            if trigger_matches > 0:
                confidence += trigger_matches * 0.1

            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)

            scored_recommendations.append(]
            })

        return scored_recommendations

    def generate_activation_command(self, selected_instructions: List[str]) -> str:
        """Generate activation command for selected instructions"""
        if not selected_instructions:
            return ""

        # Group instructions by category
        categorized = {}
        for instruction_name in selected_instructions:
            if instruction_name in self.instruction_sets:
                category = self.instruction_sets[instruction_name].category
                if category not in categorized:
                    categorized[category] = [
                categorized[category].append(instruction_name)

        # Generate command
        command_parts = [
        for category, instructions in categorized.items():
            command_parts.append(f"# {category} Instructions")
            for instruction in instructions:
                command_parts.append(]
                    f"MANDATORY: Apply {instruction} from .github/instructions/{instruction}.instructions.md")

        return "\n".join(command_parts)

    def record_usage(
    self,
    instruction_name: str,
    task_type: str,
    context: str,
    effectiveness_score: float,
     user_feedback: str = ""):
        """Record instruction usage for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            (instruction_name, task_type, context,
             effectiveness_score, usage_timestamp, user_feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (instruction_name, task_type, context, effectiveness_score, datetime.now().isoformat(), user_feedback))

        conn.commit()
        conn.close()

        logger.info(
            f"[NOTES] Recorded usage: {instruction_name} (score: {effectiveness_score})")

    def get_usage_analytics(self) -> Dict:
        """Get comprehensive usage analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Most used instructions
        cursor.execute(
            SELECT instruction_name, COUNT(*) as usage_count, AVG(effectiveness_score) as avg_score
            FROM instruction_usage
            GROUP BY instruction_name
            ORDER BY usage_count DESC
            LIMIT 10
        """)
        most_used = cursor.fetchall()

        # Most effective instructions
        cursor.execute(
            SELECT instruction_name, AVG(effectiveness_score) as avg_score, COUNT(*) as usage_count
            FROM instruction_usage
            GROUP BY instruction_name
            HAVING COUNT(*) >= 3
            ORDER BY avg_score DESC
            LIMIT 10
        """)
        most_effective = cursor.fetchall()

        # Task type distribution
        cursor.execute(
            SELECT task_type, COUNT(*) as count
            FROM instruction_usage
            GROUP BY task_type
            ORDER BY count DESC
        """)
        task_distribution = cursor.fetchall()

        conn.close()

        return {]
            'total_instructions': len(self.instruction_sets),
            'database_path': str(self.db_path)
        }


def main():
    """CLI interface for instruction orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(]
        description='[TARGET] Intelligent Instruction Set Orchestrator')
    parser.add_argument('--task-type', required=True, help='Type of task')
    parser.add_argument(]
                        default=[], help='Required capabilities')
    parser.add_argument(]
        '--complexity', choices=['low', 'medium', 'high'], default='medium', help='Task complexity')
    parser.add_argument('--workspace', help='Workspace root directory')
    parser.add_argument(]
                        help='Generate activation command')
    parser.add_argument(]
                        help='Show usage analytics')

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = IntelligentInstructionOrchestrator(]
        workspace_root=args.workspace)

    if args.analytics:
        # Show analytics
        analytics = orchestrator.get_usage_analytics()
        print("[BAR_CHART] INSTRUCTION USAGE ANALYTICS")
        print(f"Total Instructions: {analytics['total_instructions']}")
        print("\nMost Used Instructions:")
        for name, count, score in analytics['most_used']:
            print(f"  {name}: {count} uses (avg score: {score:.2f})")
        print("\nMost Effective Instructions:")
        for name, score, count in analytics['most_effective']:
            print(f"  {name}: {score:.2f} score ({count} uses)")
        return

    # Create task context
    task_context = TaskContext(]
        user_preferences={},
        session_history=[]
    )

    # Get recommendations
    recommendations = orchestrator.suggest_instructions(task_context)

    print(f"[TARGET] INSTRUCTION RECOMMENDATIONS for {args.task_type.upper()}")
    print("=" * 60)

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['instruction_name']}")
        print(f"   Category: {rec['category']}")
        print(f"   Confidence: {rec['confidence']:.2f}")
        print(f"   Priority: {rec['priority']}/10")
        if rec['triggers']:
            print(f"   Triggers: {', '.join(rec['triggers'][:3])}")
        print()

    if args.generate_command:
        selected = [rec['instruction_name'] for rec in recommendations]
        command = orchestrator.generate_activation_command(selected)
        print("[LAUNCH] ACTIVATION COMMAND:")
        print("=" * 60)
        print(command)


if __name__ == "__main__":
    main()
