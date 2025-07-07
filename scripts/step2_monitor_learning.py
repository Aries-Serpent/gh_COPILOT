#!/usr/bin/env python3
"""
STEP 2: Monitor Learning - Enterprise-Grade Learning Pattern Monitoring System
Part of the 6-Step Factory Deployment Integration Framework

Features:
- Real-time learning pattern effectiveness tracking
- Visual processing indicators with DUAL COPILOT validation
- Anti-recursion validation and enterprise compliance
- Performance metrics collection and analysis
- Integration with factory deployment data
"""

import os
import sys
import json
import time
import sqlite3
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

# Visual processing indicators
class VisualIndicators:
    """Visual processing indicators for monitoring operations"""
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 50) -> str:
        """Generate visual progress bar"""
        filled = int(width * current / total)
        bar = "" * filled + "" * (width - filled)
        percentage = (current / total) * 100
        return f"[{bar}] {percentage:.1f}% ({current}/{total})"
    
    @staticmethod
    def status_indicator(status: str) -> str:
        """Generate visual status indicator"""
        indicators = {
            "active": " ACTIVE",
            "warning": " WARNING", 
            "error": " ERROR",
            "processing": " PROCESSING",
            "complete": "SUCCESS COMPLETE",
            "monitoring": " MONITORING"
        }
        return indicators.get(status.lower(), f" {status.upper()}")

@dataclass
class LearningMetric:
    """Data class for learning metrics"""
    timestamp: datetime
    pattern_id: str
    effectiveness_score: float
    learning_rate: float
    adaptation_speed: float
    resource_usage: Dict[str, float]
    performance_indicators: Dict[str, Any]
    validation_status: str

@dataclass
class MonitoringSession:
    """Data class for monitoring sessions"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_patterns_monitored: int
    average_effectiveness: float
    alerts_generated: int
    status: str

class AntiRecursionValidator:
    """Anti-recursion validation system"""
    
    def __init__(self, max_depth: int = 10, cooldown_seconds: int = 1):
        self.max_depth = max_depth
        self.cooldown_seconds = cooldown_seconds
        self.call_stack = []
        self.last_call_time = {}
    
    def validate_call(self, function_name: str, context: Dict[str, Any]) -> bool:
        """Validate function call for recursion"""
        current_time = time.time()
        
        # Check call frequency
        if function_name in self.last_call_time:
            time_diff = current_time - self.last_call_time[function_name]
            if time_diff < self.cooldown_seconds:
                return False
        
        # Check stack depth
        if len(self.call_stack) >= self.max_depth:
            return False
        
        # Check for recursive patterns
        context_key = f"{function_name}_{hash(str(sorted(context.items())))}"
        if context_key in self.call_stack:
            return False
        
        # Update tracking
        self.call_stack.append(context_key)
        self.last_call_time[function_name] = current_time
        return True
    
    def release_call(self, function_name: str, context: Dict[str, Any]):
        """Release function call from tracking"""
        context_key = f"{function_name}_{hash(str(sorted(context.items())))}"
        if context_key in self.call_stack:
            self.call_stack.remove(context_key)

class DualCopilotValidator:
    """DUAL COPILOT validation system"""
    
    @staticmethod
    def validate_learning_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate learning data with dual validation"""
        errors = []
        
        # Primary validation
        required_fields = ['pattern_id', 'effectiveness_score', 'learning_rate', 'timestamp']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Secondary validation
        if 'effectiveness_score' in data:
            if not isinstance(data['effectiveness_score'], (int, float)):
                errors.append("effectiveness_score must be numeric")
            elif not 0 <= data['effectiveness_score'] <= 1:
                errors.append("effectiveness_score must be between 0 and 1")
        
        if 'learning_rate' in data:
            if not isinstance(data['learning_rate'], (int, float)):
                errors.append("learning_rate must be numeric")
            elif data['learning_rate'] < 0:
                errors.append("learning_rate must be non-negative")
        
        return len(errors) == 0, errors

class LearningMonitor:
    """Main learning monitoring system"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.db_path = os.path.join(self.workspace_path, "databases", "learning_monitor.db")
        self.log_path = os.path.join(self.workspace_path, "learning_monitor.log")
        
        # Initialize components
        self.visual = VisualIndicators()
        self.anti_recursion = AntiRecursionValidator()
        self.dual_validator = DualCopilotValidator()
        
        # Monitoring state
        self.is_monitoring = False
        self.current_session: Optional[MonitoringSession] = None
        self.learning_metrics = []
        self.alert_thresholds = {
            'min_effectiveness': 0.3,
            'max_resource_usage': 0.8,
            'min_learning_rate': 0.01
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for monitoring data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Learning metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    pattern_id TEXT NOT NULL,
                    effectiveness_score REAL NOT NULL,
                    learning_rate REAL NOT NULL,
                    adaptation_speed REAL NOT NULL,
                    resource_usage TEXT NOT NULL,
                    performance_indicators TEXT NOT NULL,
                    validation_status TEXT NOT NULL
                )
            ''')
            
            # Monitoring sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_patterns_monitored INTEGER DEFAULT 0,
                    average_effectiveness REAL DEFAULT 0.0,
                    alerts_generated INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    pattern_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def start_monitoring_session(self) -> str:
        """Start a new learning monitoring session"""
        try:
            if not self.anti_recursion.validate_call("start_monitoring_session", {}):
                raise Exception("Anti-recursion validation failed")
            
            session_id = f"monitor_session_{int(time.time())}"
            
            # Create session
            self.current_session = MonitoringSession(
                session_id=session_id,
                start_time=datetime.now(),
                end_time=None,
                total_patterns_monitored=0,
                average_effectiveness=0.0,
                alerts_generated=0,
                status="active"
            )
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO monitoring_sessions 
                (session_id, start_time, status)
                VALUES (?, ?, ?)
            ''', (session_id, self.current_session.start_time.isoformat(), "active"))
            conn.commit()
            conn.close()
            
            self.is_monitoring = True
            self.logger.info(f"{self.visual.status_indicator('active')} Monitoring session started: {session_id}")
            
            # Start monitoring thread
            monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitoring_thread.start()
            
            self.anti_recursion.release_call("start_monitoring_session", {})
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring session: {e}")
            self.anti_recursion.release_call("start_monitoring_session", {})
            raise
    
    def _monitoring_loop(self):
        """Main monitoring loop running in background thread"""
        while self.is_monitoring and self.current_session:
            try:
                # Collect learning patterns from factory deployment
                patterns = self._collect_learning_patterns()
                
                # Process each pattern
                for pattern in patterns:
                    if not self.is_monitoring:
                        break
                    
                    metric = self._analyze_pattern(pattern)
                    if metric:
                        self._store_learning_metric(metric)
                        self._check_alerts(metric)
                        
                        # Update session statistics
                        if self.current_session:
                            self.current_session.total_patterns_monitored += 1
                        self._update_session_stats()
                
                # Visual progress indicator
                print(f"\r{self.visual.status_indicator('monitoring')} "
                      f"Patterns monitored: {self.current_session.total_patterns_monitored} | "
                      f"Avg effectiveness: {self.current_session.average_effectiveness:.3f}", end="")
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Back off on error
    
    def _collect_learning_patterns(self) -> List[Dict[str, Any]]:
        """Collect learning patterns from various sources"""
        patterns = []
        
        try:
            # Check for factory deployment data
            factory_db_path = os.path.join(self.workspace_path, "databases", "factory_deployment.db")
            if os.path.exists(factory_db_path):
                conn = sqlite3.connect(factory_db_path)
                cursor = conn.cursor()
                
                # Get recent deployment patterns
                cursor.execute('''
                    SELECT pattern_id, success_rate, performance_metrics, timestamp
                    FROM deployment_patterns
                    WHERE datetime(timestamp) > datetime('now', '-1 hour')
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''')
                
                for row in cursor.fetchall():
                    patterns.append({
                        'pattern_id': row[0],
                        'success_rate': row[1],
                        'performance_metrics': json.loads(row[2]),
                        'timestamp': row[3],
                        'source': 'factory_deployment'
                    })
                
                conn.close()
            
            # Add synthetic patterns for demonstration
            if len(patterns) < 5:
                import random
                for i in range(5):
                    patterns.append({
                        'pattern_id': f"synthetic_pattern_{i}",
                        'success_rate': random.uniform(0.3, 0.9),
                        'performance_metrics': {
                            'cpu_usage': random.uniform(0.1, 0.8),
                            'memory_usage': random.uniform(0.2, 0.7),
                            'response_time': random.uniform(100, 1000)
                        },
                        'timestamp': datetime.now().isoformat(),
                        'source': 'synthetic'
                    })
            
        except Exception as e:
            self.logger.error(f"Error collecting learning patterns: {e}")
        
        return patterns
    
    def _analyze_pattern(self, pattern: Dict[str, Any]) -> Optional[LearningMetric]:
        """Analyze a learning pattern and generate metrics"""
        try:
            # Validate pattern data
            is_valid, errors = self.dual_validator.validate_learning_data({
                'pattern_id': pattern.get('pattern_id'),
                'effectiveness_score': pattern.get('success_rate', 0),
                'learning_rate': 0.05,  # Default learning rate
                'timestamp': pattern.get('timestamp')
            })
            
            if not is_valid:
                self.logger.warning(f"Invalid pattern data: {errors}")
                return None
            
            # Calculate learning metrics
            effectiveness_score = pattern.get('success_rate', 0)
            learning_rate = self._calculate_learning_rate(pattern)
            adaptation_speed = self._calculate_adaptation_speed(pattern)
            resource_usage = pattern.get('performance_metrics', {})
            
            # Create learning metric
            metric = LearningMetric(
                timestamp=datetime.fromisoformat(pattern['timestamp']),
                pattern_id=pattern['pattern_id'],
                effectiveness_score=effectiveness_score,
                learning_rate=learning_rate,
                adaptation_speed=adaptation_speed,
                resource_usage=resource_usage,
                performance_indicators={
                    'source': pattern.get('source', 'unknown'),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'quality_score': min(effectiveness_score * learning_rate * 2, 1.0)
                },
                validation_status="validated"
            )
            
            return metric
            
        except Exception as e:
            self.logger.error(f"Error analyzing pattern {pattern.get('pattern_id', 'unknown')}: {e}")
            return None
    
    def _calculate_learning_rate(self, pattern: Dict[str, Any]) -> float:
        """Calculate learning rate based on pattern characteristics"""
        try:
            success_rate = pattern.get('success_rate', 0)
            performance_metrics = pattern.get('performance_metrics', {})
            
            # Base learning rate
            base_rate = 0.05
            
            # Adjust based on success rate
            success_factor = success_rate * 0.5
            
            # Adjust based on resource efficiency
            resource_efficiency = 1.0
            if performance_metrics:
                cpu_usage = performance_metrics.get('cpu_usage', 0.5)
                memory_usage = performance_metrics.get('memory_usage', 0.5)
                resource_efficiency = 1.0 - ((cpu_usage + memory_usage) / 2) * 0.3
            
            learning_rate = base_rate + success_factor * resource_efficiency
            return min(max(learning_rate, 0.01), 0.5)  # Clamp between 0.01 and 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating learning rate: {e}")
            return 0.05  # Default learning rate
    
    def _calculate_adaptation_speed(self, pattern: Dict[str, Any]) -> float:
        """Calculate adaptation speed based on pattern characteristics"""
        try:
            performance_metrics = pattern.get('performance_metrics', {})
            response_time = performance_metrics.get('response_time', 500)
            
            # Lower response time = higher adaptation speed
            max_response_time = 2000  # 2 seconds
            adaptation_speed = 1.0 - min(response_time / max_response_time, 1.0)
            
            return max(adaptation_speed, 0.1)  # Minimum 0.1
            
        except Exception as e:
            self.logger.error(f"Error calculating adaptation speed: {e}")
            return 0.5  # Default adaptation speed
    
    def _store_learning_metric(self, metric: LearningMetric):
        """Store learning metric in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_metrics 
                (timestamp, pattern_id, effectiveness_score, learning_rate, 
                 adaptation_speed, resource_usage, performance_indicators, validation_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.timestamp.isoformat(),
                metric.pattern_id,
                metric.effectiveness_score,
                metric.learning_rate,
                metric.adaptation_speed,
                json.dumps(metric.resource_usage),
                json.dumps(metric.performance_indicators),
                metric.validation_status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing learning metric: {e}")
    
    def _check_alerts(self, metric: LearningMetric):
        """Check if metric triggers any alerts"""
        alerts = []
        
        # Check effectiveness threshold
        if metric.effectiveness_score < self.alert_thresholds['min_effectiveness']:
            alerts.append({
                'type': 'low_effectiveness',
                'severity': 'warning',
                'message': f"Low effectiveness score: {metric.effectiveness_score:.3f}"
            })
        
        # Check learning rate threshold
        if metric.learning_rate < self.alert_thresholds['min_learning_rate']:
            alerts.append({
                'type': 'low_learning_rate',
                'severity': 'warning',
                'message': f"Low learning rate: {metric.learning_rate:.3f}"
            })
        
        # Check resource usage
        if isinstance(metric.resource_usage, dict):
            for resource, usage in metric.resource_usage.items():
                if isinstance(usage, (int, float)) and usage > self.alert_thresholds['max_resource_usage']:
                    alerts.append({
                        'type': 'high_resource_usage',
                        'severity': 'error',
                        'message': f"High {resource} usage: {usage:.3f}"
                    })
        
        # Store alerts
        for alert in alerts:
            self._store_alert(metric.pattern_id, alert)
            if self.current_session:
                self.current_session.alerts_generated += 1
    
    def _store_alert(self, pattern_id: str, alert: Dict[str, str]):
        """Store alert in database"""
        try:
            if not self.current_session:
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO monitoring_alerts 
                (timestamp, session_id, alert_type, pattern_id, severity, message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                self.current_session.session_id,
                alert['type'],
                pattern_id,
                alert['severity'],
                alert['message']
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.warning(f"{self.visual.status_indicator('warning')} "
                              f"Alert: {alert['message']} (Pattern: {pattern_id})")
            
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}")
    
    def _update_session_stats(self):
        """Update session statistics"""
        try:
            if not self.current_session:
                return
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate average effectiveness
            cursor.execute('''
                SELECT AVG(effectiveness_score)
                FROM learning_metrics
                WHERE pattern_id IN (
                    SELECT DISTINCT pattern_id FROM learning_metrics
                    WHERE datetime(timestamp) >= ?
                )
            ''', (self.current_session.start_time.isoformat(),))
            
            avg_effectiveness = cursor.fetchone()[0] or 0.0
            self.current_session.average_effectiveness = avg_effectiveness
            
            # Update session in database
            cursor.execute('''
                UPDATE monitoring_sessions
                SET total_patterns_monitored = ?,
                    average_effectiveness = ?,
                    alerts_generated = ?
                WHERE session_id = ?
            ''', (
                self.current_session.total_patterns_monitored,
                self.current_session.average_effectiveness,
                self.current_session.alerts_generated,
                self.current_session.session_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating session stats: {e}")
    
    def stop_monitoring_session(self):
        """Stop the current monitoring session"""
        try:
            if not self.current_session:
                self.logger.warning("No active monitoring session to stop")
                return
            
            self.is_monitoring = False
            self.current_session.end_time = datetime.now()
            self.current_session.status = "completed"
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE monitoring_sessions
                SET end_time = ?, status = ?
                WHERE session_id = ?
            ''', (
                self.current_session.end_time.isoformat(),
                "completed",
                self.current_session.session_id
            ))
            conn.commit()
            conn.close()
            
            self.logger.info(f"{self.visual.status_indicator('complete')} "
                           f"Monitoring session completed: {self.current_session.session_id}")
            
            # Generate session report
            self._generate_session_report()
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring session: {e}")
    
    def _generate_session_report(self):
        """Generate comprehensive session report"""
        try:
            if not self.current_session or not self.current_session.end_time:
                return
            
            report = {
                'session_summary': asdict(self.current_session),
                'monitoring_duration': str(self.current_session.end_time - self.current_session.start_time),
                'performance_analysis': self._get_performance_analysis(),
                'alert_summary': self._get_alert_summary(),
                'recommendations': self._get_recommendations(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save report
            report_path = os.path.join(self.workspace_path, 
                                     f"learning_monitor_report_{self.current_session.session_id}.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Session report saved: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating session report: {e}")
    
    def _get_performance_analysis(self) -> Dict[str, Any]:
        """Get performance analysis for current session"""
        try:
            if not self.current_session:
                return {}
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    AVG(effectiveness_score) as avg_effectiveness,
                    MAX(effectiveness_score) as max_effectiveness,
                    MIN(effectiveness_score) as min_effectiveness,
                    AVG(learning_rate) as avg_learning_rate,
                    AVG(adaptation_speed) as avg_adaptation_speed,
                    COUNT(*) as total_metrics
                FROM learning_metrics
                WHERE datetime(timestamp) >= ?
            ''', (self.current_session.start_time.isoformat(),))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'average_effectiveness': result[0] or 0.0,
                'max_effectiveness': result[1] or 0.0,
                'min_effectiveness': result[2] or 0.0,
                'average_learning_rate': result[3] or 0.0,
                'average_adaptation_speed': result[4] or 0.0,
                'total_metrics_collected': result[5] or 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance analysis: {e}")
            return {}
    
    def _get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary for current session"""
        try:
            if not self.current_session:
                return {}
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT alert_type, severity, COUNT(*) as count
                FROM monitoring_alerts
                WHERE session_id = ?
                GROUP BY alert_type, severity
            ''', (self.current_session.session_id,))
            
            alerts = {}
            for row in cursor.fetchall():
                alert_type, severity, count = row
                if alert_type not in alerts:
                    alerts[alert_type] = {}
                alerts[alert_type][severity] = count
            
            conn.close()
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting alert summary: {e}")
            return {}
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on monitoring results"""
        recommendations = []
        
        try:
            if not self.current_session:
                return ["No active session to analyze"]
                
            if self.current_session.average_effectiveness < 0.5:
                recommendations.append("Consider adjusting learning algorithms - low average effectiveness detected")
            
            if self.current_session.alerts_generated > 10:
                recommendations.append("High number of alerts generated - review alert thresholds")
            
            if self.current_session.total_patterns_monitored < 10:
                recommendations.append("Low pattern monitoring volume - consider increasing monitoring frequency")
            
            recommendations.append("Continue monitoring for trend analysis")
            recommendations.append("Consider implementing adaptive thresholds based on historical data")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations

def main():
    """Main execution function for Step 2: Monitor Learning"""
    print("=" * 80)
    print("STEP 2: Monitor Learning - Enterprise Learning Pattern Monitoring")
    print("=" * 80)
    
    try:
        # Initialize monitor
        workspace = os.getcwd()
        monitor = LearningMonitor(workspace)
        
        print(f"{monitor.visual.status_indicator('processing')} Initializing learning monitor...")
        
        # Start monitoring session
        session_id = monitor.start_monitoring_session()
        print(f"{monitor.visual.status_indicator('active')} Monitoring session started: {session_id}")
        
        # Run monitoring for demonstration (30 seconds)
        print(f"{monitor.visual.status_indicator('monitoring')} Running monitoring for 30 seconds...")
        time.sleep(30)
        
        # Stop monitoring
        monitor.stop_monitoring_session()
        
        print(f"\n{monitor.visual.status_indicator('complete')} Step 2: Monitor Learning completed successfully!")
        print(f"Database: {monitor.db_path}")
        print(f"Log file: {monitor.log_path}")
        
        return True
        
    except Exception as e:
        print(f"ERROR Step 2 failed: {e}")
        return False

if __name__ == "__main__":
    main()