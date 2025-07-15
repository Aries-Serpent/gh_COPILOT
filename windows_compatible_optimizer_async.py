#!/usr/bin/env python3
"""
🤖 WINDOWS COMPATIBLE OPTIMIZER
Enhanced Database Optimizer with Async Support for CLI Integration

This module provides the WindowsCompatibleOptimizer class with async methods
for seamless integration with the autonomous CLI system.
"""

import asyncio
import sqlite3
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class DatabaseHealth:
    """Database health assessment data structure"""
    path: str
    size_mb: float
    table_count: int
    record_count: int
    health_score: float
    status: str
    recommendations: list


class WindowsCompatibleOptimizer:
    """🤖 Windows Compatible Autonomous Database Optimizer"""
    
    def __init__(self):
        self.workspace_path = Path("e:/gh_COPILOT")
        self.start_time = None
        self.databases_analyzed = 0
        self.databases_optimized = 0
        self.results = []
        
    async def run_optimization(self) -> Dict[str, Any]:
        """🚀 Run async database optimization"""
        self.start_time = time.time()
        print("\n[TEXT] Starting Windows Compatible Database Optimization...")
        
        # Find all database files
        db_files = list(self.workspace_path.glob("**/*.db"))
        total_databases = len(db_files)
        
        print(f"[TEXT] Found {total_databases} databases for analysis")
        
        results = {
            'session_id': f"OPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'total_databases': total_databases,
            'databases_analyzed': 0,
            'databases_optimized': 0,
            'recommendations': [],
            'execution_time': 0,
            'success_rate': 0
        }
        
        # Analyze each database
        for i, db_file in enumerate(db_files, 1):
            try:
                print(f"[TEXT] Analyzing database {i}/{total_databases}: {db_file.name}")
                
                # Analyze database health
                health = await self._analyze_database_health(db_file)
                
                if health:
                    results['databases_analyzed'] += 1
                    
                    # Apply optimizations if needed
                    if health.health_score < 0.8:
                        optimized = await self._optimize_database(db_file, health)
                        if optimized:
                            results['databases_optimized'] += 1
                    
                    # Collect recommendations
                    if health.recommendations:
                        results['recommendations'].extend(health.recommendations)
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.01)
                
            except Exception as e:
                print(f"[TEXT] Warning: Error analyzing {db_file.name}: {e}")
                continue
        
        # Calculate final metrics
        execution_time = time.time() - self.start_time
        results['execution_time'] = execution_time
        
        if total_databases > 0:
            results['success_rate'] = (results['databases_analyzed'] / total_databases * 100)
        else:
            results['success_rate'] = 0
        
        print(f"[TEXT] Optimization completed in {execution_time:.1f} seconds")
        print(f"[TEXT] Success rate: {results['success_rate']:.1f}%")
        
        return results
    
    async def _analyze_database_health(self, db_file: Path) -> Optional[DatabaseHealth]:
        """Analyze individual database health"""
        try:
            # Get file size
            size_mb = db_file.stat().st_size / (1024 * 1024)
            
            # Connect and analyze
            with sqlite3.connect(str(db_file), timeout=5.0) as conn:
                cursor = conn.cursor()
                
                # Get table count
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                # Estimate record count (sample from first few tables)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
                tables = cursor.fetchall()
                
                total_records = 0
                for (table_name,) in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                        count = cursor.fetchone()[0]
                        total_records += count
                    except sqlite3.Error:
                        continue
                
                # Calculate health score
                health_score = self._calculate_health_score(size_mb, table_count, total_records)
                
                # Determine status
                if health_score >= 0.9:
                    status = "EXCELLENT"
                elif health_score >= 0.7:
                    status = "GOOD"
                elif health_score >= 0.5:
                    status = "WARNING"
                else:
                    status = "CRITICAL"
                
                # Generate recommendations
                recommendations = self._generate_recommendations(size_mb, table_count, health_score)
                
                return DatabaseHealth(
                    path=str(db_file),
                    size_mb=size_mb,
                    table_count=table_count,
                    record_count=total_records,
                    health_score=health_score,
                    status=status,
                    recommendations=recommendations
                )
                
        except Exception as e:
            print(f"[TEXT] Error analyzing {db_file.name}: {e}")
            return None
    
    async def _optimize_database(self, db_file: Path, health: DatabaseHealth) -> bool:
        """Optimize database based on health assessment"""
        try:
            with sqlite3.connect(str(db_file), timeout=10.0) as conn:
                cursor = conn.cursor()
                
                # Apply optimizations based on health
                optimizations_applied = 0
                
                # ANALYZE - Update table statistics
                try:
                    cursor.execute("ANALYZE")
                    optimizations_applied += 1
                except sqlite3.Error:
                    pass
                
                # VACUUM for large databases
                if health.size_mb > 10:
                    try:
                        cursor.execute("VACUUM")
                        optimizations_applied += 1
                    except sqlite3.Error:
                        pass
                
                # REINDEX for databases with many tables
                if health.table_count > 20:
                    try:
                        cursor.execute("REINDEX")
                        optimizations_applied += 1
                    except sqlite3.Error:
                        pass
                
                conn.commit()
                return optimizations_applied > 0
                
        except Exception as e:
            print(f"[TEXT] Error optimizing {db_file.name}: {e}")
            return False
    
    def _calculate_health_score(self, size_mb: float, table_count: int, record_count: int) -> float:
        """Calculate database health score (0.0 - 1.0)"""
        score = 1.0
        
        # Size factor (penalize very large databases)
        if size_mb > 100:
            score -= 0.1
        elif size_mb > 500:
            score -= 0.2
        
        # Table factor (penalize too many or too few tables)
        if table_count == 0:
            score -= 0.5
        elif table_count > 100:
            score -= 0.1
        
        # Record factor (penalize empty databases)
        if record_count == 0:
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def _generate_recommendations(self, size_mb: float, table_count: int,
                                  health_score: float) -> list:
        """Generate optimization recommendations"""
        recommendations = []
        
        if health_score < 0.5:
            recommendations.append("CRITICAL: Database requires immediate attention")
        
        if size_mb > 100:
            recommendations.append("Consider VACUUM operation to reduce file size")
        
        if table_count == 0:
            recommendations.append("Database appears to be empty - verify data integrity")
        
        if table_count > 50:
            recommendations.append("Consider REINDEX operation for performance optimization")
        
        if health_score < 0.7:
            recommendations.append("Run ANALYZE to update table statistics")
        
        return recommendations


# For backwards compatibility
async def main():
    """Main function for standalone execution"""
    optimizer = WindowsCompatibleOptimizer()
    results = await optimizer.run_optimization()
    
    print("\n[TEXT] OPTIMIZATION SUMMARY:")
    print(f"[TEXT] Total databases: {results['total_databases']}")
    print(f"[TEXT] Analyzed: {results['databases_analyzed']}")
    print(f"[TEXT] Optimized: {results['databases_optimized']}")
    print(f"[TEXT] Success rate: {results['success_rate']:.1f}%")
    print(f"[TEXT] Execution time: {results['execution_time']:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
