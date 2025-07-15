#!/usr/bin/env python3
"""
Windows-Compatible Autonomous Database Health Optimizer
Self-Healing, Self-Learning Database Improvement System
Fixed for Windows Console Unicode Issues
"""

import os
import sqlite3
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional, Any
import time
import shutil
from concurrent.futures import ThreadPoolExecutor
import statistics

# Windows-compatible indicators (no emoji)
INDICATORS = {
    'analyze': '[ANALYZE]',
    'optimize': '[OPTIMIZE]',
    'success': '[SUCCESS]', 
    'warning': '[WARNING]',
    'error': '[ERROR]',
    'ai': '[AI]',
    'learn': '[LEARN]',
    'quantum': '[QUANTUM]',
    'monitor': '[MONITOR]',
    'backup': '[BACKUP]',
    'heal': '[HEAL]'
}

@dataclass
class DatabaseHealth:
    """Enhanced database health metrics"""
    database_name: str
    file_size: int
    table_count: int
    record_count: int
    integrity_score: float
    performance_score: float
    optimization_score: float
    fragmentation_level: float
    health_score: float
    priority_level: str
    recommendations: List[str]
    last_modified: str
    backup_available: bool

class WindowsCompatibleOptimizer:
    """Windows-compatible autonomous database optimizer"""
    
    def __init__(self):
        self.workspace_path = Path("e:/gh_COPILOT")
        self.results_dir = self.workspace_path / "results" / "autonomous_optimization"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging with UTF-8 encoding
        log_file = self.workspace_path / "autonomous_optimization.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize system
        self.database_registry = self._discover_databases()
        self.priority_databases = self._classify_priorities()
        
        self.logger.info("="*100)
        self.logger.info(f"{INDICATORS['success']} Windows-Compatible Autonomous Database Optimizer Initialized")
        self.logger.info(f"{INDICATORS['analyze']} Discovered {len(self.database_registry)} databases")
        self.logger.info("="*100)
    
    def _discover_databases(self) -> Dict[str, str]:
        """Discover all database files"""
        databases = {}
        
        db_extensions = ['.db', '.sqlite', '.sqlite3']
        
        for ext in db_extensions:
            for db_file in self.workspace_path.glob(f"**/*{ext}"):
                if db_file.is_file() and db_file.stat().st_size > 0:
                    db_name = db_file.stem
                    databases[db_name] = str(db_file)
        
        self.logger.info(f"{INDICATORS['success']} Database discovery complete: {len(databases)} databases found")
        return databases
    
    def _classify_priorities(self) -> Dict[str, List[str]]:
        """Classify databases by priority"""
        priorities = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }
        
        critical_keywords = ['production', 'core', 'main', 'primary', 'critical']
        high_keywords = ['analytics', 'monitoring', 'security', 'compliance', 'audit']
        medium_keywords = ['cache', 'session', 'temp', 'log', 'metrics']
        
        for db_name in self.database_registry.keys():
            name_lower = db_name.lower()
            
            if any(keyword in name_lower for keyword in critical_keywords):
                priorities['CRITICAL'].append(db_name)
            elif any(keyword in name_lower for keyword in high_keywords):
                priorities['HIGH'].append(db_name)
            elif any(keyword in name_lower for keyword in medium_keywords):
                priorities['MEDIUM'].append(db_name)
            else:
                priorities['LOW'].append(db_name)
        
        self.logger.info(f"{INDICATORS['ai']} Priority classification complete:")
        for level, dbs in priorities.items():
            self.logger.info(f"  {level}: {len(dbs)} databases")
        
        return priorities
    
    def analyze_database_health(self, db_name: str, db_path: str) -> DatabaseHealth:
        """Analyze comprehensive database health"""
        try:
            # Basic file metrics
            file_size = os.path.getsize(db_path)
            last_modified = datetime.fromtimestamp(os.path.getmtime(db_path)).isoformat()
            
            # Initialize default values
            table_count = 0
            record_count = 0
            integrity_score = 100.0
            performance_score = 100.0
            optimization_score = 100.0
            fragmentation_level = 0.0
            recommendations = []
            
            # Try to connect and analyze
            try:
                with sqlite3.connect(db_path, timeout=5) as conn:
                    cursor = conn.cursor()
                    
                    # Count tables
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    # Count total records (approximate)
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                            record_count += cursor.fetchone()[0]
                        except sqlite3.Error:
                            continue
                    
                    # Database integrity check
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    if integrity_result != "ok":
                        integrity_score = 75.0
                        recommendations.append("Database integrity issues detected")
                    
                    # Check for optimization opportunities
                    if file_size > 10*1024*1024:  # > 10MB
                        recommendations.append("Consider VACUUM for large database")
                        optimization_score = 85.0
                    
                    if table_count == 0:
                        recommendations.append("Empty database - consider initialization")
                        performance_score = 50.0
            
            except sqlite3.Error as e:
                self.logger.warning(f"{INDICATORS['warning']} Database analysis issue for {db_name}: {e}")
                integrity_score = 50.0
                recommendations.append(f"Database access issue: {str(e)}")
            
            # Calculate overall health score
            health_score = (integrity_score + performance_score + optimization_score) / 3
            
            # Determine priority level
            priority_level = "MEDIUM"
            for level, dbs in self.priority_databases.items():
                if db_name in dbs:
                    priority_level = level
                    break
            
            # Check for backup
            backup_available = (self.workspace_path / "backups" / f"{db_name}_backup.db").exists()
            
            return DatabaseHealth(
                database_name=db_name,
                file_size=file_size,
                table_count=table_count,
                record_count=record_count,
                integrity_score=integrity_score,
                performance_score=performance_score,
                optimization_score=optimization_score,
                fragmentation_level=fragmentation_level,
                health_score=health_score,
                priority_level=priority_level,
                recommendations=recommendations,
                last_modified=last_modified,
                backup_available=backup_available
            )
            
        except Exception as e:
            self.logger.error(f"{INDICATORS['error']} Failed to analyze {db_name}: {e}")
            return DatabaseHealth(
                database_name=db_name,
                file_size=0,
                table_count=0,
                record_count=0,
                integrity_score=0.0,
                performance_score=0.0,
                optimization_score=0.0,
                fragmentation_level=100.0,
                health_score=0.0,
                priority_level="LOW",
                recommendations=["Analysis failed"],
                last_modified="",
                backup_available=False
            )
    
    async def run_optimization(self) -> Dict[str, Any]:
        """Run the complete optimization process"""
        start_time = time.time()
        results = {
            'optimization_id': f"AUTO_OPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'total_databases': len(self.database_registry),
            'databases_analyzed': 0,
            'databases_optimized': 0,
            'health_improvements': [],
            'recommendations': [],
            'execution_time': 0,
            'success_rate': 0.0
        }
        
        self.logger.info(f"{INDICATORS['analyze']} Starting autonomous database optimization")
        self.logger.info(f"{INDICATORS['monitor']} Processing {len(self.database_registry)} databases")
        
        # Process databases by priority
        all_health_reports = []
        
        for priority_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            priority_dbs = self.priority_databases[priority_level]
            if not priority_dbs:
                continue
                
            self.logger.info(f"{INDICATORS['ai']} Processing {priority_level} priority: {len(priority_dbs)} databases")
            
            for db_name in priority_dbs:
                db_path = self.database_registry[db_name]
                
                # Analyze health
                health = self.analyze_database_health(db_name, db_path)
                all_health_reports.append(health)
                results['databases_analyzed'] += 1
                
                # Log health status
                if health.health_score >= 90:
                    status = "EXCELLENT"
                elif health.health_score >= 75:
                    status = "GOOD"
                elif health.health_score >= 50:
                    status = "FAIR"
                else:
                    status = "POOR"
                
                self.logger.info(f"{INDICATORS['success']} [{priority_level}] {db_name}: {status} ({health.health_score:.1f}%)")
                
                # Optimization if needed
                if health.health_score < 80:
                    optimized = await self._optimize_database(db_name, db_path, health)
                    if optimized:
                        results['databases_optimized'] += 1
                        results['health_improvements'].append({
                            'database': db_name,
                            'before': health.health_score,
                            'improvement': 'Applied optimizations'
                        })
                
                # Add recommendations
                if health.recommendations:
                    results['recommendations'].extend([
                        f"{db_name}: {rec}" for rec in health.recommendations
                    ])
        
        # Calculate final metrics
        results['execution_time'] = time.time() - start_time
        results['success_rate'] = (results['databases_optimized'] / max(results['databases_analyzed'], 1)) * 100
        results['end_time'] = datetime.now().isoformat()
        
        # Save detailed results
        await self._save_results(results, all_health_reports)
        
        return results
    
    async def _optimize_database(self, db_name: str, db_path: str, health: DatabaseHealth) -> bool:
        """Perform database optimization"""
        try:
            self.logger.info(f"{INDICATORS['optimize']} Optimizing {db_name}")
            
            # Create backup first
            backup_path = self.workspace_path / "backups" / f"{db_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(db_path, backup_path)
            
            # Perform optimizations
            with sqlite3.connect(db_path) as conn:
                # VACUUM to reclaim space
                conn.execute("VACUUM")
                
                # Analyze for query optimization
                conn.execute("ANALYZE")
                
                # Reindex if needed
                conn.execute("REINDEX")
            
            self.logger.info(f"{INDICATORS['success']} Database {db_name} optimized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"{INDICATORS['error']} Optimization failed for {db_name}: {e}")
            return False
    
    async def _save_results(self, results: Dict[str, Any], health_reports: List[DatabaseHealth]):
        """Save optimization results"""
        try:
            # Save summary results
            results_file = self.results_dir / f"optimization_summary_{results['optimization_id']}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Save detailed health reports
            health_file = self.results_dir / f"health_analysis_{results['optimization_id']}.json"
            health_data = [asdict(report) for report in health_reports]
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"{INDICATORS['success']} Results saved to {results_file}")
            
        except Exception as e:
            self.logger.error(f"{INDICATORS['error']} Failed to save results: {e}")

async def main():
    """Main execution function"""
    print("="*100)
    print(f"{INDICATORS['analyze']} WINDOWS-COMPATIBLE AUTONOMOUS DATABASE OPTIMIZER")
    print("Self-Healing, Self-Learning Database Improvement System")
    print("="*100)
    
    optimizer = WindowsCompatibleOptimizer()
    results = await optimizer.run_optimization()
    
    # Display summary
    print("\n" + "="*100)
    print(f"{INDICATORS['success']} OPTIMIZATION COMPLETED")
    print("="*100)
    print(f"Total Databases: {results['total_databases']}")
    print(f"Databases Analyzed: {results['databases_analyzed']}")
    print(f"Databases Optimized: {results['databases_optimized']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Execution Time: {results['execution_time']:.1f} seconds")
    print(f"Recommendations: {len(results['recommendations'])}")
    print("="*100)
    
    if results['recommendations']:
        print(f"\n{INDICATORS['ai']} KEY RECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'][:10], 1):
            print(f"  {i}. {rec}")
    
    return results

if __name__ == "__main__":
    try:
        results = asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{INDICATORS['warning']} Optimization interrupted by user")
    except Exception as e:
        print(f"{INDICATORS['error']} Optimization failed: {e}")
