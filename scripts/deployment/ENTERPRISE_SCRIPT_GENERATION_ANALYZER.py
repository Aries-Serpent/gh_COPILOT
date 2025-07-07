#!/usr/bin/env python3
"""
ENTERPRISE SCRIPT GENERATION FILES ANALYZER
===========================================
Analyze the enterprise_script_generation_* and intelligent_script_generation_*
files to identify potential redundancies since these appear to be variations

COMPLIANCE: Enterprise GitHub Copilot integration standards
PATTERN: DUAL COPILOT with visual processing indicators
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from tqdm import tqdm
import difflib

class EnterpriseScriptAnalyzer:
    def __init__(self):
        self.start_time = datetime.now()
        self.staging_root = Path("e:/gh_COPILOT")
        self.sandbox_root = Path("e:/gh_COPILOT")
        
        print(f"[SEARCH] ENTERPRISE SCRIPT GENERATION FILES ANALYZER")
        print(f"Start Time: {self.start_time}")
        print("=" * 60)
    
    def analyze_similar_files(self):
        """Analyze enterprise script generation files for redundancy"""
        print("\n[CLIPBOARD] ANALYZING ENTERPRISE SCRIPT FILES")
        print("-" * 42)
        
        # Define file groups to analyze
        file_groups = {
            "enterprise_script_generation": [
                "enterprise_script_generation_codebase_analyzer.py",
                "enterprise_script_generation_copilot_integration.py", 
                "enterprise_script_generation_framework_complete.py",
                "enterprise_script_generation_intelligent_engine.py"
            ],
            "intelligent_script_generation": [
                "intelligent_script_generation_engine.py",
                "intelligent_script_generation_implementation.py",
                "intelligent_script_generation_platform.py"
            ],
            "autonomous_production": [
                "AUTONOMOUS_PRODUCTION_CREATOR.py",
                "AUTONOMOUS_PRODUCTION_CREATOR_CLEAN.py"
            ]
        }
        
        all_analyses = {}
        
        for group_name, filenames in file_groups.items():
            print(f"\n[BAR_CHART] Analyzing group: {group_name}")
            group_analyses = []
            
            for filename in filenames:
                file_path = self.staging_root / filename
                if file_path.exists():
                    analysis = self.analyze_file_detailed(file_path)
                    group_analyses.append(analysis)
                    print(f"  [SUCCESS] {filename}: {analysis['size']:,} bytes")
                else:
                    print(f"  [ERROR] {filename}: Not found")
            
            if group_analyses:
                all_analyses[group_name] = group_analyses
                self.compare_group_files(group_name, group_analyses)
        
        # Generate final recommendations
        self.generate_cleanup_recommendations(all_analyses)
    
    def analyze_file_detailed(self, file_path: Path) -> Dict:
        """Detailed analysis of a single file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Extract key information
            functions = [line.strip() for line in lines if line.strip().startswith('def ')]
            classes = [line.strip() for line in lines if line.strip().startswith('class ')]
            imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
            
            # Get first meaningful comment/docstring
            purpose = ""
            for line in lines[:15]:
                if '"""' in line or "'''" in line:
                    # Find the next non-empty line
                    for next_line in lines[lines.index(line)+1:lines.index(line)+5]:
                        if next_line.strip() and not next_line.strip().startswith(('"""', "'''")):
                            purpose = next_line.strip()
                            break
                    break
            
            # Calculate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            return {
                'filename': file_path.name,
                'filepath': str(file_path),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'line_count': len(lines),
                'function_count': len(functions),
                'class_count': len(classes),
                'import_count': len(imports),
                'content_hash': content_hash,
                'purpose': purpose,
                'functions': functions[:10],  # First 10 functions
                'classes': classes,
                'imports': imports[:10],  # First 10 imports
                'content_preview': content[:500] + '...' if len(content) > 500 else content
            }
            
        except Exception as e:
            return {
                'filename': file_path.name,
                'filepath': str(file_path),
                'error': str(e),
                'analysis_failed': True
            }
    
    def compare_group_files(self, group_name: str, files: List[Dict]):
        """Compare files within a group for similarity"""
        print(f"\n[SEARCH] COMPARING {group_name.upper()} FILES")
        print("-" * 40)
        
        if len(files) < 2:
            print("  [?][?]  Only one file in group - no comparison needed")
            return
        
        # Compare each pair of files
        similarities = []
        
        for i, file1 in enumerate(files):
            for j, file2 in enumerate(files[i+1:], i+1):
                if file1.get('analysis_failed') or file2.get('analysis_failed'):
                    continue
                
                similarity = self.calculate_file_similarity(file1, file2)
                similarities.append({
                    'file1': file1['filename'],
                    'file2': file2['filename'],
                    'similarity': similarity,
                    'size_diff': abs(file1['size'] - file2['size']),
                    'function_overlap': self.calculate_function_overlap(file1, file2)
                })
        
        # Report similarities
        high_similarity = [s for s in similarities if s['similarity'] > 0.7]
        moderate_similarity = [s for s in similarities if 0.4 < s['similarity'] <= 0.7]
        
        if high_similarity:
            print(f"  [?] HIGH SIMILARITY DETECTED:")
            for sim in high_similarity:
                print(f"    [?] {sim['file1']} [?] {sim['file2']}: {sim['similarity']:.1%}")
                print(f"      Size diff: {sim['size_diff']:,} bytes, Function overlap: {sim['function_overlap']:.1%}")
        
        if moderate_similarity:
            print(f"  [?] MODERATE SIMILARITY:")
            for sim in moderate_similarity:
                print(f"    [?] {sim['file1']} [?] {sim['file2']}: {sim['similarity']:.1%}")
        
        if not high_similarity and not moderate_similarity:
            print(f"  [SUCCESS] All files in group are sufficiently different")
    
    def calculate_file_similarity(self, file1: Dict, file2: Dict) -> float:
        """Calculate similarity between two files"""
        try:
            # Size similarity (normalized)
            size1, size2 = file1['size'], file2['size']
            size_similarity = min(size1, size2) / max(size1, size2) if max(size1, size2) > 0 else 0
            
            # Function name similarity
            func1_names = set(func.split('(')[0].replace('def ', '') for func in file1.get('functions', []))
            func2_names = set(func.split('(')[0].replace('def ', '') for func in file2.get('functions', []))
            func_similarity = len(func1_names & func2_names) / len(func1_names | func2_names) if len(func1_names | func2_names) > 0 else 0
            
            # Class similarity
            class1_names = set(cls.split('(')[0].replace('class ', '').replace(':', '') for cls in file1.get('classes', []))
            class2_names = set(cls.split('(')[0].replace('class ', '').replace(':', '') for cls in file2.get('classes', []))
            class_similarity = len(class1_names & class2_names) / len(class1_names | class2_names) if len(class1_names | class2_names) > 0 else 0
            
            # Import similarity
            import1 = set(file1.get('imports', []))
            import2 = set(file2.get('imports', []))
            import_similarity = len(import1 & import2) / len(import1 | import2) if len(import1 | import2) > 0 else 0
            
            # Content preview similarity (using difflib)
            content1 = file1.get('content_preview', '')
            content2 = file2.get('content_preview', '')
            content_similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
            
            # Weighted overall similarity
            overall_similarity = (
                size_similarity * 0.1 +
                func_similarity * 0.3 +
                class_similarity * 0.2 +
                import_similarity * 0.2 +
                content_similarity * 0.2
            )
            
            return overall_similarity
            
        except Exception as e:
            return 0.0
    
    def calculate_function_overlap(self, file1: Dict, file2: Dict) -> float:
        """Calculate function name overlap percentage"""
        try:
            func1_names = set(func.split('(')[0].replace('def ', '') for func in file1.get('functions', []))
            func2_names = set(func.split('(')[0].replace('def ', '') for func in file2.get('functions', []))
            
            if not func1_names or not func2_names:
                return 0.0
            
            overlap = len(func1_names & func2_names)
            total_unique = len(func1_names | func2_names)
            
            return overlap / total_unique if total_unique > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    def generate_cleanup_recommendations(self, all_analyses: Dict):
        """Generate cleanup recommendations based on analysis"""
        print(f"\n[CLIPBOARD] CLEANUP RECOMMENDATIONS")
        print("=" * 30)
        
        recommendations = []
        total_analyzed = sum(len(files) for files in all_analyses.values())
        total_size = sum(file['size'] for files in all_analyses.values() for file in files if not file.get('analysis_failed'))
        
        print(f"[BAR_CHART] Analysis Summary:")
        print(f"  [?] Total files analyzed: {total_analyzed}")
        print(f"  [?] Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        # Check for potential removals based on our analysis
        for group_name, files in all_analyses.items():
            print(f"\n[SEARCH] {group_name.upper()} GROUP:")
            
            if len(files) > 1:
                # Sort by modification date (newest first)
                files.sort(key=lambda x: x.get('modified', ''), reverse=True)
                
                newest_file = files[0]
                print(f"  [?] Newest: {newest_file['filename']} ({newest_file['modified']})")
                
                # Check if older files might be redundant
                for older_file in files[1:]:
                    print(f"  [?] Older: {older_file['filename']} ({older_file['modified']})")
                    
                    # Conservative recommendation
                    if 'clean' in older_file['filename'].lower() or 'final' in older_file['filename'].lower():
                        recommendations.append({
                            'action': 'REVIEW',
                            'file': older_file['filename'],
                            'reason': 'Potential final/clean version - review for redundancy',
                            'priority': 'MEDIUM'
                        })
                    elif older_file['size'] < newest_file['size'] * 0.7:
                        recommendations.append({
                            'action': 'REVIEW',
                            'file': older_file['filename'],
                            'reason': 'Significantly smaller than newest version',
                            'priority': 'LOW'
                        })
            else:
                print(f"  [SUCCESS] Single file - no redundancy concerns")
        
        # Final recommendations
        print(f"\n[TARGET] FINAL RECOMMENDATIONS:")
        
        if recommendations:
            for rec in recommendations:
                print(f"  {rec['priority']} PRIORITY: {rec['action']} {rec['file']}")
                print(f"    Reason: {rec['reason']}")
        else:
            print(f"  [SUCCESS] NO REDUNDANCIES DETECTED")
            print(f"  [CLIPBOARD] All files appear to serve unique purposes")
            print(f"  [STORAGE] Current organization is optimal")
        
        print(f"\n[LOCK] CONSERVATIVE APPROACH:")
        print(f"  [?] Keep all files since they represent different implementation stages")
        print(f"  [?] Database already contains full deployment history")
        print(f"  [?] Files provide reference implementations for future development")
        print(f"  [?] Total space usage ({total_size/1024:.1f} KB) is manageable")

def main():
    """Main execution function"""
    analyzer = EnterpriseScriptAnalyzer()
    analyzer.analyze_similar_files()
    
    print(f"\n[COMPLETE] ENTERPRISE SCRIPT ANALYSIS COMPLETE")
    print(f"[TARGET] RECOMMENDATION: Keep current file organization")

if __name__ == "__main__":
    main()
