#!/usr/bin/env python3
"""
Comprehensive Script Consolidation & Modulation Analysis Engine
gh_COPILOT Toolkit v4.0 Enterprise Consolidation Framework

CONSOLIDATION OBJECTIVES:
- Identify similar functional scripts for consolidation
- Analyze script modulation similarities and patterns
- Create unified enterprise modules from duplicated functionality
- Generate comprehensive consolidation recommendations
- Implement production-ready consolidated scripts

Enterprise Standards Compliance:
- DUAL COPILOT pattern validation
- Visual processing indicators with tqdm
- Anti-recursion protection protocols
- Database-first analysis approach
- 100% enterprise certification ready
"""

import os
import sys
import ast
import json
import sqlite3
import logging
import hashlib
import difflib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from tqdm import tqdm
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import re


@dataclass
class ScriptAnalysis:
    """Script analysis dataclass for modulation tracking"""
    file_path: str
    file_name: str
    file_size: int
    line_count: int
    function_count: int
    class_count: int
    import_count: int
    complexity_score: float
    similarity_hash: str
    modulation_patterns: List[str]
    functionality_category: str
    consolidation_candidate: bool


@dataclass
class ConsolidationOpportunity:
    """Consolidation opportunity tracking"""
    category: str
    scripts: List[str]
    similarity_score: float
    consolidation_potential: str
    estimated_reduction: int
    recommended_action: str


class ComprehensiveScriptConsolidationEngine:
    """
    Advanced Script Consolidation & Modulation Analysis Engine
    Enterprise-grade similarity detection and consolidation framework
    """
    
    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # MANDATORY: Visual processing indicators
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        
        # CRITICAL: Anti-recursion validation
        self.validate_enterprise_environment()
        
        # Initialize consolidation system
        self.workspace_path = Path(workspace_path)
        self.production_db = self.workspace_path / "databases" / "production.db"
        self.analysis_db = self.workspace_path / "databases" / "consolidation_analysis.db"
        
        # Consolidation tracking
        self.script_analyses: List[ScriptAnalysis] = []
        self.consolidation_opportunities: List[ConsolidationOpportunity] = []
        self.modulation_patterns: Dict[str, List[str]] = defaultdict(list)
        self.similarity_matrix: Dict[Tuple[str, str], float] = {}
        
        # Advanced analysis settings
        self.similarity_threshold = 0.75  # 75% similarity for consolidation
        self.min_script_size = 100  # Minimum lines to consider
        self.complexity_threshold = 5.0  # Complexity score threshold
        
        # Initialize enterprise logging
        self.setup_enterprise_logging()
        
        # MANDATORY: Log initialization with visual indicators
        self.logger.info("="*80)
        self.logger.info("🚀 COMPREHENSIVE SCRIPT CONSOLIDATION ENGINE INITIALIZED")
        self.logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Process ID: {self.process_id}")
        self.logger.info(f"Workspace: {self.workspace_path}")
        self.logger.info(f"Similarity Threshold: {self.similarity_threshold}")
        self.logger.info("="*80)
    
    def validate_enterprise_environment(self):
        """CRITICAL: Validate enterprise environment before consolidation"""
        workspace_root = Path(os.getcwd())
        
        # MANDATORY: Anti-recursion validation
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
        violations = []
        
        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))
        
        if violations:
            raise RuntimeError(f"CRITICAL: Environment violations prevent consolidation: {violations}")
        
        logging.info("✅ ENTERPRISE ENVIRONMENT VALIDATED FOR CONSOLIDATION")
    
    def setup_enterprise_logging(self):
        """Setup enterprise logging for consolidation tracking"""
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_dir / "script_consolidation_analysis.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def execute_comprehensive_consolidation_analysis(self):
        """
        Execute comprehensive script consolidation and modulation analysis
        Main orchestration method with DUAL COPILOT validation
        """
        self.logger.info("🔄 STARTING COMPREHENSIVE CONSOLIDATION ANALYSIS")
        
        try:
            # Phase 1: Script Discovery and Analysis
            with tqdm(total=100, desc="📁 Script Discovery", unit="%") as pbar:
                python_scripts = self.discover_python_scripts()
                pbar.update(100)
                self.logger.info(f"✅ Discovered {len(python_scripts)} Python scripts")
            
            # Phase 2: Individual Script Analysis
            with tqdm(total=len(python_scripts), desc="🔍 Script Analysis", unit="scripts") as pbar:
                for script_path in python_scripts:
                    analysis = self.analyze_script(script_path)
                    if analysis:
                        self.script_analyses.append(analysis)
                    pbar.update(1)
                
                self.logger.info(f"✅ Analyzed {len(self.script_analyses)} scripts successfully")
            
            # Phase 3: Similarity Matrix Calculation
            with tqdm(total=len(self.script_analyses)**2, desc="📊 Similarity Analysis", unit="comparisons") as pbar:
                self.calculate_similarity_matrix(pbar)
                self.logger.info(f"✅ Calculated {len(self.similarity_matrix)} similarity comparisons")
            
            # Phase 4: Modulation Pattern Detection
            with tqdm(total=100, desc="🧩 Pattern Detection", unit="%") as pbar:
                self.detect_modulation_patterns()
                pbar.update(100)
                self.logger.info(f"✅ Detected {len(self.modulation_patterns)} modulation patterns")
            
            # Phase 5: Consolidation Opportunity Identification
            with tqdm(total=100, desc="💡 Opportunity Identification", unit="%") as pbar:
                self.identify_consolidation_opportunities()
                pbar.update(100)
                self.logger.info(f"✅ Identified {len(self.consolidation_opportunities)} consolidation opportunities")
            
            # Phase 6: Generate Comprehensive Report
            with tqdm(total=100, desc="📋 Report Generation", unit="%") as pbar:
                report = self.generate_consolidation_report()
                pbar.update(100)
                self.logger.info("✅ Generated comprehensive consolidation report")
            
            # Phase 7: Database Storage
            with tqdm(total=100, desc="🗄️ Database Storage", unit="%") as pbar:
                self.store_analysis_results()
                pbar.update(100)
                self.logger.info("✅ Stored analysis results in database")
            
            # MANDATORY: Success completion logging
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger.info("="*80)
            self.logger.info("🏆 COMPREHENSIVE CONSOLIDATION ANALYSIS COMPLETED")
            self.logger.info(f"Total Scripts Analyzed: {len(self.script_analyses)}")
            self.logger.info(f"Consolidation Opportunities: {len(self.consolidation_opportunities)}")
            self.logger.info(f"Analysis Duration: {duration:.1f} seconds")
            self.logger.info("="*80)
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ CONSOLIDATION ANALYSIS ERROR: {e}")
            raise
    
    def discover_python_scripts(self) -> List[Path]:
        """Discover all Python scripts in the workspace"""
        python_scripts = []
        
        # Search patterns for Python files
        search_patterns = [
            "*.py",
            "**/*.py"
        ]
        
        # Exclusion patterns to avoid
        exclusion_patterns = [
            "*/__pycache__/*",
            "*/.venv/*",
            "*/.git/*",
            "*/node_modules/*",
            "*test*",  # Exclude test files for now
        ]
        
        for pattern in search_patterns:
            for script_path in self.workspace_path.rglob(pattern):
                if script_path.is_file():
                    # Check if path should be excluded
                    exclude = False
                    for exclusion in exclusion_patterns:
                        if script_path.match(exclusion):
                            exclude = True
                            break
                    
                    if not exclude:
                        python_scripts.append(script_path)
        
        return sorted(python_scripts)
    
    def analyze_script(self, script_path: Path) -> Optional[ScriptAnalysis]:
        """Analyze individual script for modulation patterns"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic metrics
            line_count = len(content.splitlines())
            file_size = len(content.encode('utf-8'))
            
            # Skip very small files
            if line_count < self.min_script_size:
                return None
            
            # Parse AST for advanced analysis
            try:
                tree = ast.parse(content)
                function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                import_count = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
            except SyntaxError:
                # Handle files with syntax errors
                function_count = content.count('def ')
                class_count = content.count('class ')
                import_count = content.count('import ')
            
            # Calculate complexity score
            complexity_score = self.calculate_complexity_score(content, function_count, class_count)
            
            # Generate similarity hash
            similarity_hash = self.generate_similarity_hash(content)
            
            # Detect modulation patterns
            modulation_patterns = self.extract_modulation_patterns(content)
            
            # Categorize functionality
            functionality_category = self.categorize_functionality(script_path, content)
            
            # Determine consolidation candidacy
            consolidation_candidate = (
                line_count >= self.min_script_size and
                complexity_score >= self.complexity_threshold and
                len(modulation_patterns) > 0
            )
            
            return ScriptAnalysis(
                file_path=str(script_path),
                file_name=script_path.name,
                file_size=file_size,
                line_count=line_count,
                function_count=function_count,
                class_count=class_count,
                import_count=import_count,
                complexity_score=complexity_score,
                similarity_hash=similarity_hash,
                modulation_patterns=modulation_patterns,
                functionality_category=functionality_category,
                consolidation_candidate=consolidation_candidate
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Analysis failed for {script_path}: {e}")
            return None
    
    def calculate_complexity_score(self, content: str, function_count: int, class_count: int) -> float:
        """Calculate script complexity score"""
        # Base complexity factors
        line_complexity = len(content.splitlines()) * 0.01
        function_complexity = function_count * 1.5
        class_complexity = class_count * 2.0
        
        # Advanced complexity indicators
        conditional_complexity = content.count('if ') * 0.5
        loop_complexity = content.count('for ') + content.count('while ') * 0.7
        exception_complexity = content.count('try:') * 0.3
        
        total_complexity = (
            line_complexity + function_complexity + class_complexity +
            conditional_complexity + loop_complexity + exception_complexity
        )
        
        return round(total_complexity, 2)
    
    def generate_similarity_hash(self, content: str) -> str:
        """Generate similarity hash for script comparison"""
        # Normalize content for similarity comparison
        normalized = re.sub(r'\s+', ' ', content.lower())
        normalized = re.sub(r'#.*$', '', normalized, flags=re.MULTILINE)  # Remove comments
        normalized = re.sub(r'["\'].*?["\']', '""', normalized)  # Normalize strings
        
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def extract_modulation_patterns(self, content: str) -> List[str]:
        """Extract modulation patterns from script content"""
        patterns = []
        
        # Common modulation patterns
        pattern_checks = {
            'database_operations': ['sqlite3', 'cursor', 'execute', 'fetchall', 'commit'],
            'file_operations': ['open(', 'Path(', 'read(', 'write(', 'exists()'],
            'logging_operations': ['logging', 'logger', 'info(', 'error(', 'debug('],
            'datetime_operations': ['datetime', 'strftime', 'now()', 'timedelta'],
            'json_operations': ['json.load', 'json.dump', 'json.loads', 'json.dumps'],
            'validation_operations': ['validate', 'check', 'verify', 'assert'],
            'enterprise_patterns': ['enterprise', 'production', 'deployment', 'orchestrator'],
            'utility_patterns': ['utility', 'helper', 'tool', 'framework'],
            'error_handling': ['try:', 'except:', 'raise', 'Exception'],
            'progress_tracking': ['tqdm', 'progress', 'percentage', 'completion']
        }
        
        for pattern_name, keywords in pattern_checks.items():
            if any(keyword in content for keyword in keywords):
                patterns.append(pattern_name)
        
        return patterns
    
    def categorize_functionality(self, script_path: Path, content: str) -> str:
        """Categorize script functionality based on path and content"""
        path_str = str(script_path).lower()
        content_lower = content.lower()
        
        # Category mapping
        categories = {
            'database': ['database', 'db', 'sqlite', 'sql'],
            'deployment': ['deploy', 'orchestrator', 'deployment'],
            'validation': ['validate', 'verify', 'check', 'compliance'],
            'utility': ['utility', 'helper', 'tool', 'framework'],
            'enterprise': ['enterprise', 'production', 'certification'],
            'analysis': ['analysis', 'report', 'metrics', 'statistics'],
            'consolidation': ['consolidation', 'merge', 'combine'],
            'optimization': ['optimization', 'optimize', 'enhance'],
            'monitoring': ['monitoring', 'monitor', 'watch', 'track'],
            'correction': ['correction', 'fix', 'repair', 'clean']
        }
        
        for category, keywords in categories.items():
            if any(keyword in path_str or keyword in content_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def calculate_similarity_matrix(self, pbar: tqdm):
        """Calculate similarity matrix for all script pairs"""
        script_count = len(self.script_analyses)
        
        for i, script1 in enumerate(self.script_analyses):
            for j, script2 in enumerate(self.script_analyses):
                if i != j:
                    similarity = self.calculate_script_similarity(script1, script2)
                    self.similarity_matrix[(script1.file_path, script2.file_path)] = similarity
                pbar.update(1)
    
    def calculate_script_similarity(self, script1: ScriptAnalysis, script2: ScriptAnalysis) -> float:
        """Calculate similarity score between two scripts"""
        # Hash similarity (quick check)
        hash_similarity = 1.0 if script1.similarity_hash == script2.similarity_hash else 0.0
        
        # Pattern similarity
        common_patterns = set(script1.modulation_patterns) & set(script2.modulation_patterns)
        total_patterns = set(script1.modulation_patterns) | set(script2.modulation_patterns)
        pattern_similarity = len(common_patterns) / len(total_patterns) if total_patterns else 0.0
        
        # Structural similarity
        size_ratio = min(script1.file_size, script2.file_size) / max(script1.file_size, script2.file_size)
        line_ratio = min(script1.line_count, script2.line_count) / max(script1.line_count, script2.line_count)
        function_ratio = min(script1.function_count, script2.function_count) / max(script1.function_count, script2.function_count) if max(script1.function_count, script2.function_count) > 0 else 1.0
        
        structural_similarity = (size_ratio + line_ratio + function_ratio) / 3
        
        # Category similarity
        category_similarity = 1.0 if script1.functionality_category == script2.functionality_category else 0.0
        
        # Weighted total similarity
        total_similarity = (
            hash_similarity * 0.4 +
            pattern_similarity * 0.3 +
            structural_similarity * 0.2 +
            category_similarity * 0.1
        )
        
        return round(total_similarity, 3)
    
    def detect_modulation_patterns(self):
        """Detect common modulation patterns across scripts"""
        pattern_frequency = Counter()
        
        for analysis in self.script_analyses:
            for pattern in analysis.modulation_patterns:
                pattern_frequency[pattern] += 1
                self.modulation_patterns[pattern].append(analysis.file_path)
        
        # Log top patterns
        top_patterns = pattern_frequency.most_common(10)
        self.logger.info("🧩 TOP MODULATION PATTERNS:")
        for pattern, count in top_patterns:
            self.logger.info(f"   - {pattern}: {count} scripts")
    
    def identify_consolidation_opportunities(self):
        """Identify specific consolidation opportunities"""
        # Group scripts by similarity
        similarity_groups = defaultdict(list)
        
        for (script1, script2), similarity in self.similarity_matrix.items():
            if similarity >= self.similarity_threshold:
                # Find existing group or create new one
                found_group = False
                for group_key, group_scripts in similarity_groups.items():
                    if script1 in group_scripts or script2 in group_scripts:
                        group_scripts.extend([script1, script2])
                        found_group = True
                        break
                
                if not found_group:
                    group_key = f"group_{len(similarity_groups)}"
                    similarity_groups[group_key] = [script1, script2]
        
        # Create consolidation opportunities
        for group_key, scripts in similarity_groups.items():
            unique_scripts = list(set(scripts))
            if len(unique_scripts) >= 2:
                # Calculate group similarity
                group_similarity = sum(
                    self.similarity_matrix.get((s1, s2), 0) 
                    for s1 in unique_scripts for s2 in unique_scripts if s1 != s2
                ) / (len(unique_scripts) * (len(unique_scripts) - 1))
                
                # Determine consolidation potential
                if group_similarity >= 0.9:
                    potential = "HIGH"
                    action = "IMMEDIATE_CONSOLIDATION"
                elif group_similarity >= 0.8:
                    potential = "MEDIUM"
                    action = "PLANNED_CONSOLIDATION"
                else:
                    potential = "LOW"
                    action = "REVIEW_FOR_PATTERNS"
                
                # Calculate estimated reduction
                total_lines = sum(
                    next(a.line_count for a in self.script_analyses if a.file_path == script)
                    for script in unique_scripts
                )
                estimated_reduction = int(total_lines * (group_similarity * 0.7))
                
                # Get category from scripts
                categories = [
                    next(a.functionality_category for a in self.script_analyses if a.file_path == script)
                    for script in unique_scripts
                ]
                primary_category = Counter(categories).most_common(1)[0][0]
                
                opportunity = ConsolidationOpportunity(
                    category=primary_category,
                    scripts=unique_scripts,
                    similarity_score=round(group_similarity, 3),
                    consolidation_potential=potential,
                    estimated_reduction=estimated_reduction,
                    recommended_action=action
                )
                
                self.consolidation_opportunities.append(opportunity)
    
    def generate_consolidation_report(self) -> Dict[str, Any]:
        """Generate comprehensive consolidation analysis report"""
        total_scripts = len(self.script_analyses)
        total_lines = sum(a.line_count for a in self.script_analyses)
        total_functions = sum(a.function_count for a in self.script_analyses)
        
        # Calculate potential savings
        total_estimated_reduction = sum(o.estimated_reduction for o in self.consolidation_opportunities)
        reduction_percentage = (total_estimated_reduction / total_lines) * 100 if total_lines > 0 else 0
        
        # Category breakdown
        category_stats = defaultdict(int)
        for analysis in self.script_analyses:
            category_stats[analysis.functionality_category] += 1
        
        # Consolidation summary
        consolidation_summary = {
            "HIGH": len([o for o in self.consolidation_opportunities if o.consolidation_potential == "HIGH"]),
            "MEDIUM": len([o for o in self.consolidation_opportunities if o.consolidation_potential == "MEDIUM"]),
            "LOW": len([o for o in self.consolidation_opportunities if o.consolidation_potential == "LOW"])
        }
        
        report = {
            "analysis_metadata": {
                "analysis_date": self.start_time.isoformat(),
                "analysis_duration": (datetime.now() - self.start_time).total_seconds(),
                "workspace_path": str(self.workspace_path),
                "similarity_threshold": self.similarity_threshold
            },
            "script_statistics": {
                "total_scripts_analyzed": total_scripts,
                "total_lines_of_code": total_lines,
                "total_functions": total_functions,
                "average_script_size": round(total_lines / total_scripts, 1) if total_scripts > 0 else 0,
                "consolidation_candidates": len([a for a in self.script_analyses if a.consolidation_candidate])
            },
            "category_breakdown": dict(category_stats),
            "modulation_patterns": {
                pattern: len(scripts) for pattern, scripts in self.modulation_patterns.items()
            },
            "consolidation_opportunities": consolidation_summary,
            "potential_savings": {
                "estimated_line_reduction": total_estimated_reduction,
                "reduction_percentage": round(reduction_percentage, 2),
                "estimated_script_reduction": len(self.consolidation_opportunities)
            },
            "detailed_opportunities": [asdict(o) for o in self.consolidation_opportunities],
            "top_consolidation_targets": self.get_top_consolidation_targets(),
            "recommendations": self.generate_recommendations()
        }
        
        # Save report to file
        report_path = self.workspace_path / "reports" / f"comprehensive_consolidation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📋 Consolidation report saved: {report_path}")
        return report
    
    def get_top_consolidation_targets(self) -> List[Dict[str, Any]]:
        """Get top consolidation targets sorted by potential impact"""
        sorted_opportunities = sorted(
            self.consolidation_opportunities,
            key=lambda x: (x.similarity_score, x.estimated_reduction),
            reverse=True
        )
        
        return [
            {
                "rank": i + 1,
                "category": opp.category,
                "scripts": [Path(s).name for s in opp.scripts],
                "similarity_score": opp.similarity_score,
                "estimated_reduction": opp.estimated_reduction,
                "recommended_action": opp.recommended_action
            }
            for i, opp in enumerate(sorted_opportunities[:10])
        ]
    
    def generate_recommendations(self) -> List[str]:
        """Generate consolidation recommendations"""
        recommendations = []
        
        high_priority = len([o for o in self.consolidation_opportunities if o.consolidation_potential == "HIGH"])
        medium_priority = len([o for o in self.consolidation_opportunities if o.consolidation_potential == "MEDIUM"])
        
        if high_priority > 0:
            recommendations.append(f"🔴 IMMEDIATE ACTION: {high_priority} high-priority consolidation opportunities identified")
        
        if medium_priority > 0:
            recommendations.append(f"🟡 PLANNED ACTION: {medium_priority} medium-priority consolidation opportunities for next sprint")
        
        # Pattern-based recommendations
        top_patterns = sorted(self.modulation_patterns.items(), key=lambda x: len(x[1]), reverse=True)
        if top_patterns:
            pattern, scripts = top_patterns[0]
            recommendations.append(f"🧩 PATTERN FOCUS: '{pattern}' pattern appears in {len(scripts)} scripts - prime consolidation target")
        
        # Category-based recommendations
        category_counts = defaultdict(int)
        for analysis in self.script_analyses:
            category_counts[analysis.functionality_category] += 1
        
        top_category = max(category_counts.items(), key=lambda x: x[1])
        if top_category[1] > 5:
            recommendations.append(f"📂 CATEGORY FOCUS: '{top_category[0]}' category has {top_category[1]} scripts - consider unified module")
        
        return recommendations
    
    def store_analysis_results(self):
        """Store analysis results in database"""
        # Create consolidation analysis database
        self.analysis_db.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.analysis_db) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS script_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    file_name TEXT,
                    file_size INTEGER,
                    line_count INTEGER,
                    function_count INTEGER,
                    class_count INTEGER,
                    import_count INTEGER,
                    complexity_score REAL,
                    similarity_hash TEXT,
                    modulation_patterns TEXT,
                    functionality_category TEXT,
                    consolidation_candidate BOOLEAN,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consolidation_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    scripts TEXT,
                    similarity_score REAL,
                    consolidation_potential TEXT,
                    estimated_reduction INTEGER,
                    recommended_action TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert script analyses
            for analysis in self.script_analyses:
                cursor.execute("""
                    INSERT OR REPLACE INTO script_analyses 
                    (file_path, file_name, file_size, line_count, function_count, class_count, 
                     import_count, complexity_score, similarity_hash, modulation_patterns, 
                     functionality_category, consolidation_candidate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis.file_path, analysis.file_name, analysis.file_size,
                    analysis.line_count, analysis.function_count, analysis.class_count,
                    analysis.import_count, analysis.complexity_score, analysis.similarity_hash,
                    json.dumps(analysis.modulation_patterns), analysis.functionality_category,
                    analysis.consolidation_candidate
                ))
            
            # Insert consolidation opportunities
            for opportunity in self.consolidation_opportunities:
                cursor.execute("""
                    INSERT INTO consolidation_opportunities 
                    (category, scripts, similarity_score, consolidation_potential, 
                     estimated_reduction, recommended_action)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    opportunity.category, json.dumps(opportunity.scripts),
                    opportunity.similarity_score, opportunity.consolidation_potential,
                    opportunity.estimated_reduction, opportunity.recommended_action
                ))
            
            conn.commit()
            self.logger.info(f"🗄️ Stored {len(self.script_analyses)} analyses and {len(self.consolidation_opportunities)} opportunities in database")


def main():
    """Main execution function with DUAL COPILOT validation"""
    
    # MANDATORY: Start time logging
    start_time = datetime.now()
    process_id = os.getpid()
    
    print("="*80)
    print("🚀 COMPREHENSIVE SCRIPT CONSOLIDATION & MODULATION ANALYSIS")
    print("="*80)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {process_id}")
    print("="*80)
    
    try:
        # Initialize consolidation engine
        engine = ComprehensiveScriptConsolidationEngine()
        
        # Execute comprehensive analysis
        report = engine.execute_comprehensive_consolidation_analysis()
        
        # MANDATORY: Success summary with visual indicators
        duration = (datetime.now() - start_time).total_seconds()
        print("="*80)
        print("🏆 CONSOLIDATION ANALYSIS COMPLETED SUCCESSFULLY")
        print(f"✅ Scripts Analyzed: {report['script_statistics']['total_scripts_analyzed']}")
        print(f"✅ Consolidation Opportunities: {len(report['detailed_opportunities'])}")
        print(f"✅ Potential Line Reduction: {report['potential_savings']['estimated_line_reduction']}")
        print(f"✅ Reduction Percentage: {report['potential_savings']['reduction_percentage']}%")
        print(f"✅ Analysis Duration: {duration:.1f} seconds")
        print("="*80)
        
        # Print top recommendations
        if report['recommendations']:
            print("🎯 TOP RECOMMENDATIONS:")
            for recommendation in report['recommendations']:
                print(f"   {recommendation}")
            print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ CONSOLIDATION ANALYSIS ERROR: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
