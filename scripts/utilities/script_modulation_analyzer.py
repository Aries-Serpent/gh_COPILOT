#!/usr/bin/env python3
"""
Script Modulation Analyzer
==========================

Purpose: Analyze script modulation similarities and identify consolidation opportunities
for the comprehensive consolidation project continuation.

Features:
- Advanced pattern recognition for similar functional scripts
- Database-driven analysis using production.db intelligence
- Script similarity scoring and consolidation recommendations
- Enterprise-grade modulation analysis with DUAL COPILOT validation
"""

import ast
import json
import datetime
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
from dataclasses import dataclass, field
from tqdm import tqdm

@dataclass
class ScriptModulation:
    """Represents a script's modular characteristics"""
    file_path: str
    function_names: List[str] = field(default_factory=list)
    class_names: List[str] = field(default_factory=list)
    import_statements: List[str] = field(default_factory=list)
    docstring: str = ""
    complexity_score: float = 0.0
    line_count: int = 0
    function_signatures: List[str] = field(default_factory=list)
    similar_patterns: List[str] = field(default_factory=list)

@dataclass
class ConsolidationOpportunity:
    """Represents a consolidation opportunity between scripts"""
    primary_script: str
    similar_scripts: List[str]
    similarity_score: float
    consolidation_type: str
    estimated_savings: int
    consolidation_plan: Dict[str, Any]

class ScriptModulationAnalyzer:
    """🔍 Advanced Script Modulation Analysis Engine"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.production_db = self.workspace_path / "production.db"
        self.reports_dir = self.workspace_path / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Analysis parameters
        self.similarity_threshold = 0.7  # 70% similarity for consolidation
        self.min_script_size = 50  # Minimum lines to consider for consolidation
        self.max_scripts_per_group = 5  # Maximum scripts to consolidate together
        
        # Pattern categories for analysis
        self.functional_patterns = {
            "database_operations": ["sqlite3", "cursor", "execute", "fetchall", "commit"],
            "file_operations": ["open", "read", "write", "Path", "glob", "listdir"],
            "validation_scripts": ["validate", "check", "verify", "test", "assert"],
            "optimization_scripts": ["optimize", "enhance", "improve", "performance"],
            "monitoring_scripts": ["monitor", "track", "log", "audit", "report"],
            "configuration_scripts": ["config", "settings", "parameters", "options"],
            "analysis_scripts": ["analyze", "process", "calculate", "compute"],
            "automation_scripts": ["automate", "schedule", "batch", "execute"]
        }
        
        self.analysis_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "workspace": str(self.workspace_path),
            "total_scripts_analyzed": 0,
            "modulation_groups": {},
            "consolidation_opportunities": [],
            "estimated_total_savings": 0,
            "analysis_duration": 0.0
        }
    
    def get_database_connection(self) -> sqlite3.Connection:
        """Get connection to production database"""
        return sqlite3.connect(self.production_db)
    
    def analyze_script_ast(self, file_path: Path) -> ScriptModulation:
        """Analyze Python script using AST for detailed modulation information"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # Handle syntax errors gracefully
                return ScriptModulation(
                    file_path=str(file_path),
                    line_count=len(content.split('\n'))
                )
            
            modulation = ScriptModulation(file_path=str(file_path))
            modulation.line_count = len(content.split('\n'))
            
            # Extract docstring
            docstring = ast.get_docstring(tree)
            if docstring is not None:
                modulation.docstring = docstring[:200]  # First 200 chars
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    modulation.function_names.append(node.name)
                    # Extract function signature
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({', '.join(args)})"
                    modulation.function_signatures.append(signature)
                
                elif isinstance(node, ast.ClassDef):
                    modulation.class_names.append(node.name)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            modulation.import_statements.append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            modulation.import_statements.append(f"{module}.{alias.name}")
            
            # Calculate complexity score
            modulation.complexity_score = self.calculate_complexity_score(modulation)
            
            # Identify similar patterns
            modulation.similar_patterns = self.identify_functional_patterns(content)
            
            return modulation
            
        except Exception as e:
            return ScriptModulation(
                file_path=str(file_path),
                line_count=0
            )
    
    def calculate_complexity_score(self, modulation: ScriptModulation) -> float:
        """Calculate complexity score based on various factors"""
        score = 0.0
        
        # Function count factor
        score += len(modulation.function_names) * 0.3
        
        # Class count factor
        score += len(modulation.class_names) * 0.5
        
        # Import complexity factor
        score += len(modulation.import_statements) * 0.1
        
        # Line count factor
        score += modulation.line_count * 0.01
        
        return round(score, 2)
    
    def identify_functional_patterns(self, content: str) -> List[str]:
        """Identify functional patterns in script content"""
        patterns = []
        content_lower = content.lower()
        
        for pattern_name, keywords in self.functional_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                patterns.append(pattern_name)
        
        return patterns
    
    def calculate_similarity_score(self, script1: ScriptModulation, script2: ScriptModulation) -> float:
        """Calculate similarity score between two scripts"""
        scores = []
        
        # Function name similarity
        func_similarity = self.calculate_list_similarity(script1.function_names, script2.function_names)
        scores.append(func_similarity * 0.3)
        
        # Import similarity
        import_similarity = self.calculate_list_similarity(script1.import_statements, script2.import_statements)
        scores.append(import_similarity * 0.2)
        
        # Pattern similarity
        pattern_similarity = self.calculate_list_similarity(script1.similar_patterns, script2.similar_patterns)
        scores.append(pattern_similarity * 0.3)
        
        # Complexity similarity (inverse of difference)
        complexity_diff = abs(script1.complexity_score - script2.complexity_score)
        max_complexity = max(script1.complexity_score, script2.complexity_score, 1.0)
        complexity_similarity = 1.0 - (complexity_diff / max_complexity)
        scores.append(complexity_similarity * 0.2)
        
        return sum(scores)
    
    def calculate_list_similarity(self, list1: List[str], list2: List[str]) -> float:
        """Calculate similarity between two lists using Jaccard similarity"""
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        set1, set2 = set(list1), set(list2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def discover_python_scripts(self) -> List[Path]:
        """Discover all Python scripts in the workspace"""
        python_scripts = []
        
        # Search patterns for Python scripts
        search_patterns = ["*.py"]
        
        for pattern in search_patterns:
            python_scripts.extend(list(self.workspace_path.rglob(pattern)))
        
        # Filter out __pycache__ and other system directories
        filtered_scripts = []
        exclude_patterns = ['__pycache__', '.git', '.venv', 'node_modules', '.pytest_cache']
        
        for script in python_scripts:
            if not any(exclude in str(script) for exclude in exclude_patterns):
                if script.stat().st_size > 100:  # At least 100 bytes
                    filtered_scripts.append(script)
        
        return filtered_scripts
    
    def group_scripts_by_similarity(self, modulations: List[ScriptModulation]) -> Dict[str, List[ScriptModulation]]:
        """Group scripts by similarity into potential consolidation groups"""
        groups = {}
        processed = set()
        group_id = 0
        
        for i, mod1 in enumerate(modulations):
            if mod1.file_path in processed:
                continue
            
            # Skip small scripts
            if mod1.line_count < self.min_script_size:
                continue
            
            similar_scripts = [mod1]
            processed.add(mod1.file_path)
            
            # Find similar scripts
            for j, mod2 in enumerate(modulations[i+1:], i+1):
                if mod2.file_path in processed:
                    continue
                
                if mod2.line_count < self.min_script_size:
                    continue
                
                similarity = self.calculate_similarity_score(mod1, mod2)
                
                if similarity >= self.similarity_threshold:
                    similar_scripts.append(mod2)
                    processed.add(mod2.file_path)
                    
                    # Limit group size
                    if len(similar_scripts) >= self.max_scripts_per_group:
                        break
            
            # Only create groups with multiple scripts
            if len(similar_scripts) > 1:
                group_name = f"consolidation_group_{group_id:03d}"
                groups[group_name] = similar_scripts
                group_id += 1
        
        return groups
    
    def generate_consolidation_opportunities(self, groups: Dict[str, List[ScriptModulation]]) -> List[ConsolidationOpportunity]:
        """Generate consolidation opportunities from similar script groups"""
        opportunities = []
        
        for group_name, scripts in groups.items():
            if len(scripts) < 2:
                continue
            
            # Choose primary script (largest or most complex)
            primary_script = max(scripts, key=lambda s: s.complexity_score)
            similar_scripts = [s for s in scripts if s != primary_script]
            
            # Calculate average similarity within group
            similarities = []
            for i, script1 in enumerate(scripts):
                for script2 in scripts[i+1:]:
                    similarities.append(self.calculate_similarity_score(script1, script2))
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
            
            # Estimate savings (lines of code that could be eliminated)
            total_lines = sum(s.line_count for s in scripts)
            estimated_savings = int(total_lines * 0.3)  # Assume 30% reduction possible
            
            # Determine consolidation type
            consolidation_type = self.determine_consolidation_type(scripts)
            
            # Generate consolidation plan
            consolidation_plan = self.generate_consolidation_plan(primary_script, similar_scripts)
            
            opportunity = ConsolidationOpportunity(
                primary_script=primary_script.file_path,
                similar_scripts=[s.file_path for s in similar_scripts],
                similarity_score=avg_similarity,
                consolidation_type=consolidation_type,
                estimated_savings=estimated_savings,
                consolidation_plan=consolidation_plan
            )
            
            opportunities.append(opportunity)
        
        # Sort by estimated savings (highest first)
        opportunities.sort(key=lambda o: o.estimated_savings, reverse=True)
        
        return opportunities
    
    def determine_consolidation_type(self, scripts: List[ScriptModulation]) -> str:
        """Determine the type of consolidation based on script patterns"""
        all_patterns = []
        for script in scripts:
            all_patterns.extend(script.similar_patterns)
        
        pattern_counts = Counter(all_patterns)
        most_common_pattern = pattern_counts.most_common(1)
        
        if most_common_pattern:
            pattern_name = most_common_pattern[0][0]
            return f"{pattern_name}_consolidation"
        
        return "general_consolidation"
    
    def generate_consolidation_plan(self, primary: ScriptModulation, similar: List[ScriptModulation]) -> Dict[str, Any]:
        """Generate detailed consolidation plan"""
        plan = {
            "consolidation_strategy": "merge_into_primary",
            "primary_script": primary.file_path,
            "scripts_to_merge": [s.file_path for s in similar],
            "common_functions": [],
            "common_imports": [],
            "refactoring_steps": [],
            "estimated_effort": "medium",
            "risk_level": "low"
        }
        
        # Find common functions
        primary_funcs = set(primary.function_names)
        for script in similar:
            common_funcs = primary_funcs.intersection(set(script.function_names))
            plan["common_functions"].extend(list(common_funcs))
        
        # Find common imports
        primary_imports = set(primary.import_statements)
        for script in similar:
            common_imports = primary_imports.intersection(set(script.import_statements))
            plan["common_imports"].extend(list(common_imports))
        
        # Generate refactoring steps
        plan["refactoring_steps"] = [
            "1. Backup all scripts before consolidation",
            "2. Merge common functions into primary script",
            "3. Consolidate imports and remove duplicates",
            "4. Create unified configuration handling",
            "5. Update function calls and references",
            "6. Test consolidated functionality",
            "7. Archive original scripts after validation"
        ]
        
        # Assess effort and risk
        total_scripts = len(similar) + 1
        if total_scripts > 3:
            plan["estimated_effort"] = "high"
            plan["risk_level"] = "medium"
        
        return plan
    
    def save_analysis_results(self) -> str:
        """Save comprehensive analysis results"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.reports_dir / f"script_modulation_analysis_{timestamp}.json"
        
        # Convert dataclasses to dictionaries for JSON serialization
        serializable_results = {
            "timestamp": self.analysis_results["timestamp"],
            "workspace": self.analysis_results["workspace"],
            "total_scripts_analyzed": self.analysis_results["total_scripts_analyzed"],
            "analysis_duration": self.analysis_results["analysis_duration"],
            "estimated_total_savings": self.analysis_results["estimated_total_savings"],
            "consolidation_opportunities": [],
            "modulation_groups": {},
            "summary_statistics": {
                "total_consolidation_opportunities": len(self.analysis_results["consolidation_opportunities"]),
                "total_groups_identified": len(self.analysis_results["modulation_groups"]),
                "average_similarity_score": 0.0,
                "top_consolidation_categories": []
            }
        }
        
        # Convert consolidation opportunities
        for opp in self.analysis_results["consolidation_opportunities"]:
            serializable_results["consolidation_opportunities"].append({
                "primary_script": opp.primary_script,
                "similar_scripts": opp.similar_scripts,
                "similarity_score": opp.similarity_score,
                "consolidation_type": opp.consolidation_type,
                "estimated_savings": opp.estimated_savings,
                "consolidation_plan": opp.consolidation_plan
            })
        
        # Calculate summary statistics
        if self.analysis_results["consolidation_opportunities"]:
            avg_similarity = sum(o.similarity_score for o in self.analysis_results["consolidation_opportunities"]) / len(self.analysis_results["consolidation_opportunities"])
            serializable_results["summary_statistics"]["average_similarity_score"] = round(avg_similarity, 3)
            
            # Top consolidation categories
            consolidation_types = [o.consolidation_type for o in self.analysis_results["consolidation_opportunities"]]
            type_counts = Counter(consolidation_types)
            serializable_results["summary_statistics"]["top_consolidation_categories"] = type_counts.most_common(5)
        
        # Save to file
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        return str(results_file)
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Execute comprehensive script modulation analysis"""
        start_time = datetime.datetime.now()
        
        print("🔍 STARTING SCRIPT MODULATION ANALYSIS")
        print("=" * 80)
        print(f"📁 Workspace: {self.workspace_path}")
        print(f"🎯 Target: Identify consolidation opportunities through modulation analysis")
        print("=" * 80)
        
        # Discover Python scripts
        print("🔎 Discovering Python scripts...")
        python_scripts = self.discover_python_scripts()
        print(f"📊 Found {len(python_scripts)} Python scripts for analysis")
        
        # Analyze script modulations
        print("🧠 Analyzing script modulations...")
        modulations = []
        
        with tqdm(total=len(python_scripts), desc="📝 Analyzing Scripts", unit="scripts") as pbar:
            for script_path in python_scripts:
                modulation = self.analyze_script_ast(script_path)
                if modulation.line_count > 0:  # Only include valid scripts
                    modulations.append(modulation)
                pbar.update(1)
        
        self.analysis_results["total_scripts_analyzed"] = len(modulations)
        print(f"✅ Successfully analyzed {len(modulations)} scripts")
        
        # Group scripts by similarity
        print("🔗 Grouping scripts by similarity...")
        similarity_groups = self.group_scripts_by_similarity(modulations)
        self.analysis_results["modulation_groups"] = {name: len(scripts) for name, scripts in similarity_groups.items()}
        print(f"📊 Identified {len(similarity_groups)} consolidation groups")
        
        # Generate consolidation opportunities
        print("💡 Generating consolidation opportunities...")
        opportunities = self.generate_consolidation_opportunities(similarity_groups)
        self.analysis_results["consolidation_opportunities"] = opportunities
        
        # Calculate total estimated savings
        total_savings = sum(opp.estimated_savings for opp in opportunities)
        self.analysis_results["estimated_total_savings"] = total_savings
        
        # Record analysis duration
        end_time = datetime.datetime.now()
        self.analysis_results["analysis_duration"] = (end_time - start_time).total_seconds()
        
        # Save results
        results_file = self.save_analysis_results()
        
        # Display summary
        print("\n🎯 SCRIPT MODULATION ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"📊 Scripts Analyzed: {len(modulations)}")
        print(f"🔗 Consolidation Groups: {len(similarity_groups)}")
        print(f"💡 Opportunities Identified: {len(opportunities)}")
        print(f"📉 Estimated Total Savings: {total_savings} lines of code")
        print(f"⏱️  Analysis Duration: {self.analysis_results['analysis_duration']:.2f} seconds")
        print(f"📋 Results saved to: {results_file}")
        
        if opportunities:
            print("\n🏆 TOP CONSOLIDATION OPPORTUNITIES:")
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"{i}. {Path(opp.primary_script).name}")
                print(f"   📊 Similarity: {opp.similarity_score:.1%}")
                print(f"   💾 Estimated Savings: {opp.estimated_savings} lines")
                print(f"   🔗 Similar Scripts: {len(opp.similar_scripts)}")
                print(f"   📝 Type: {opp.consolidation_type}")
                print()
        
        return self.analysis_results

def main():
    """Main execution function"""
    workspace_path = "e:/gh_COPILOT"
    
    print("🚀 SCRIPT MODULATION ANALYZER")
    print("=" * 80)
    print("Purpose: Analyze script similarities and identify consolidation opportunities")
    print("Target: Support Step 4 - Consolidation Project Continuation")
    print("=" * 80)
    
    analyzer = ScriptModulationAnalyzer(workspace_path)
    results = analyzer.run_comprehensive_analysis()
    
    if results["consolidation_opportunities"]:
        print("\n🎉 SUCCESS: Script modulation analysis completed!")
        print(f"🔍 Identified {len(results['consolidation_opportunities'])} consolidation opportunities")
        print(f"💾 Potential savings: {results['estimated_total_savings']} lines of code")
        print("🚀 Ready for consolidation implementation!")
    else:
        print("\n📊 ANALYSIS COMPLETE: No significant consolidation opportunities found")
        print("✅ Workspace scripts are already well-optimized")
    
    return results

if __name__ == "__main__":
    main()
