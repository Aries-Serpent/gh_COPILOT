#!/usr/bin/env python3
"""
STEP 4: Performance Analysis - Enterprise-Grade Performance Analysis System
Part of the 6-Step Factory Deployment Integration Framework

Features:
- Comprehensive performance analysis using analytics data
- Integration with scaling_innovation_framework.py for advanced algorithms
- Real-time performance monitoring with visual indicators
- DUAL COPILOT validation and anti-recursion protection
- Enterprise compliance and automated optimization recommendations
"""

import os
import sys
import json
import time
import sqlite3
import logging
import statistics
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict
import importlib.util

# Import scaling framework if available
scaling_framework = None
try:
    scaling_framework_path = os.path.join(os.getcwd(), "scaling_innovation_framework.py")
    if os.path.exists(scaling_framework_path):
        spec = importlib.util.spec_from_file_location("scaling_innovation_framework", scaling_framework_path)
        scaling_framework = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scaling_framework)
except Exception as e:
    print(f"Note: scaling_innovation_framework.py not loaded: {e}")

# Visual processing indicators
class VisualIndicators:
    """Visual processing indicators for performance analysis"""
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 50) -> str:
        """Generate visual progress bar"""
        if total == 0:
            return "[" + "" * width + "] 0.0% (0/0)"
        filled = int(width * current / total)
        bar = "" * filled + "" * (width - filled)
        percentage = (current / total) * 100
        return f"[{bar}] {percentage:.1f}% ({current}/{total})"
    
    @staticmethod
    def status_indicator(status: str) -> str:
        """Generate visual status indicator"""
        indicators = {
            "analyzing": "GROWTH ANALYZING",
            "processing": " PROCESSING", 
            "optimizing": "TOOL OPTIMIZING",
            "complete": "SUCCESS COMPLETE",
            "error": " ERROR",
            "warning": " WARNING",
            "active": " ACTIVE",
            "trending": "METRICS TRENDING"
        }
        return indicators.get(status.lower(), f" {status.upper()}")

@dataclass
class PerformanceMetric:
    """Data class for performance metrics"""
    timestamp: datetime
    metric_name: str
    current_value: float
    baseline_value: float
    performance_score: float
    trend_direction: str  # 'improving', 'declining', 'stable'
    confidence_level: float
    analysis_metadata: Dict[str, Any]

@dataclass
class PerformanceAnalysisSession:
    """Data class for performance analysis sessions"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    metrics_analyzed: int
    optimization_opportunities: List[Dict[str, Any]]
    performance_grade: str
    recommendations: List[str]
    status: str

class AntiRecursionValidator:
    """Anti-recursion validation system for performance analysis"""
    
    def __init__(self, max_depth: int = 20, cooldown_seconds: float = 0.3):
        self.max_depth = max_depth
        self.cooldown_seconds = cooldown_seconds
        self.analysis_stack = []
        self.last_analysis_time = {}
    
    def validate_analysis(self, analysis_type: str, data_context: str) -> bool:
        """Validate performance analysis operation for recursion"""
        current_time = time.time()
        analysis_key = f"{analysis_type}_{hash(data_context)}"
        
        # Check call frequency
        if analysis_key in self.last_analysis_time:
            time_diff = current_time - self.last_analysis_time[analysis_key]
            if time_diff < self.cooldown_seconds:
                return False
        
        # Check stack depth
        if len(self.analysis_stack) >= self.max_depth:
            return False
        
        # Check for recursive patterns
        if analysis_key in self.analysis_stack:
            return False
        
        # Update tracking
        self.analysis_stack.append(analysis_key)
        self.last_analysis_time[analysis_key] = current_time
        return True
    
    def release_analysis(self, analysis_type: str, data_context: str):
        """Release analysis operation from tracking"""
        analysis_key = f"{analysis_type}_{hash(data_context)}"
        if analysis_key in self.analysis_stack:
            self.analysis_stack.remove(analysis_key)

class DualCopilotValidator:
    """DUAL COPILOT validation system for performance analysis"""
    
    @staticmethod
    def validate_performance_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate performance analysis data with dual validation"""
        errors = []
        
        # Primary validation - required fields
        required_fields = ['metric_values', 'timestamps', 'metric_name']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Secondary validation - data consistency
        if 'metric_values' in data and 'timestamps' in data:
            values = data['metric_values']
            timestamps = data['timestamps']
            
            if not isinstance(values, list) or not isinstance(timestamps, list):
                errors.append("metric_values and timestamps must be lists")
            elif len(values) != len(timestamps):
                errors.append("metric_values and timestamps must have same length")
            elif len(values) < 2:
                errors.append("Need at least 2 data points for analysis")
        
        if 'metric_values' in data:
            try:
                values = [float(v) for v in data['metric_values']]
                if any(v < 0 for v in values):
                    errors.append("Negative values detected - may indicate data quality issues")
            except (ValueError, TypeError):
                errors.append("metric_values must be numeric")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_analysis_results(results: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate analysis results integrity"""
        errors = []
        
        required_result_fields = ['performance_score', 'trend_direction', 'confidence_level']
        for field in required_result_fields:
            if field not in results:
                errors.append(f"Missing analysis result field: {field}")
        
        if 'performance_score' in results:
            score = results['performance_score']
            if not isinstance(score, (int, float)) or not 0 <= score <= 1:
                errors.append("performance_score must be numeric between 0 and 1")
        
        if 'confidence_level' in results:
            confidence = results['confidence_level']
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                errors.append("confidence_level must be numeric between 0 and 1")
        
        if 'trend_direction' in results:
            trend = results['trend_direction']
            valid_trends = ['improving', 'declining', 'stable', 'unknown']
            if trend not in valid_trends:
                errors.append(f"trend_direction must be one of {valid_trends}")
        
        return len(errors) == 0, errors

class PerformanceAnalyzer:
    """Main performance analysis system"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.db_path = os.path.join(self.workspace_path, "databases", "performance_analysis.db")
        self.log_path = os.path.join(self.workspace_path, "performance_analysis.log")
        
        # Initialize components
        self.visual = VisualIndicators()
        self.anti_recursion = AntiRecursionValidator()
        self.dual_validator = DualCopilotValidator()
        
        # Analysis state
        self.current_session: Optional[PerformanceAnalysisSession] = None
        self.baseline_metrics = {}
        self.performance_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
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
        
        # Initialize scaling framework integration
        self.scaling_framework = scaling_framework
    
    def _init_database(self):
        """Initialize SQLite database for performance analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    baseline_value REAL NOT NULL,
                    performance_score REAL NOT NULL,
                    trend_direction TEXT NOT NULL,
                    confidence_level REAL NOT NULL,
                    analysis_metadata TEXT NOT NULL,
                    session_id TEXT NOT NULL
                )
            ''')
            
            # Analysis sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    metrics_analyzed INTEGER DEFAULT 0,
                    optimization_opportunities TEXT NOT NULL,
                    performance_grade TEXT DEFAULT 'unknown',
                    recommendations TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Baseline metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS baseline_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT UNIQUE NOT NULL,
                    baseline_value REAL NOT NULL,
                    calculation_method TEXT NOT NULL,
                    data_points_used INTEGER NOT NULL,
                    confidence_score REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Optimization recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    recommendation_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    expected_improvement REAL NOT NULL,
                    implementation_priority TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Performance analysis database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def start_analysis_session(self) -> str:
        """Start a new performance analysis session"""
        try:
            if not self.anti_recursion.validate_analysis("start_analysis_session", ""):
                raise Exception("Anti-recursion validation failed")
            
            session_id = f"perf_analysis_{int(time.time())}"
            
            # Create session
            self.current_session = PerformanceAnalysisSession(
                session_id=session_id,
                start_time=datetime.now(),
                end_time=None,
                metrics_analyzed=0,
                optimization_opportunities=[],
                performance_grade="unknown",
                recommendations=[],
                status="active"
            )
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_sessions 
                (session_id, start_time, optimization_opportunities, recommendations, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                self.current_session.start_time.isoformat(),
                json.dumps([]),
                json.dumps([]),
                "active"
            ))
            conn.commit()
            conn.close()
            
            self.logger.info(f"{self.visual.status_indicator('active')} Performance analysis session started: {session_id}")
            
            # Load baseline metrics
            self._load_baseline_metrics()
            
            self.anti_recursion.release_analysis("start_analysis_session", "")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start analysis session: {e}")
            self.anti_recursion.release_analysis("start_analysis_session", "")
            raise
    
    def _load_baseline_metrics(self):
        """Load baseline metrics from database or calculate new ones"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load existing baselines
            cursor.execute('SELECT metric_name, baseline_value FROM baseline_metrics')
            for row in cursor.fetchall():
                metric_name, baseline_value = row
                self.baseline_metrics[metric_name] = baseline_value
            
            conn.close()
            
            # Calculate new baselines if needed
            if not self.baseline_metrics:
                self._calculate_baseline_metrics()
                
            self.logger.info(f"Loaded {len(self.baseline_metrics)} baseline metrics")
            
        except Exception as e:
            self.logger.error(f"Error loading baseline metrics: {e}")
    
    def _calculate_baseline_metrics(self):
        """Calculate baseline metrics from analytics data"""
        try:
            # Check for analytics data
            analytics_db_path = os.path.join(self.workspace_path, "databases", "analytics_collector.db")
            if not os.path.exists(analytics_db_path):
                self.logger.warning("No analytics data available for baseline calculation")
                return
            
            conn = sqlite3.connect(analytics_db_path)
            cursor = conn.cursor()
            
            # Get metric data for baseline calculation
            cursor.execute('''
                SELECT metric_name, metric_value, quality_score
                FROM analytics_data_points
                WHERE datetime(timestamp) > datetime('now', '-7 days')
                AND quality_score >= 0.5
            ''')
            
            metric_data = defaultdict(list)
            for row in cursor.fetchall():
                metric_name, metric_value_str, quality_score = row
                try:
                    metric_value = json.loads(metric_value_str)
                    if isinstance(metric_value, (int, float)):
                        metric_data[metric_name].append((metric_value, quality_score))
                except:
                    continue
            
            conn.close()
            
            # Calculate baselines
            baseline_conn = sqlite3.connect(self.db_path)
            baseline_cursor = baseline_conn.cursor()
            
            for metric_name, values in metric_data.items():
                if len(values) >= 5:  # Need at least 5 data points
                    metric_values = [v[0] for v in values]
                    quality_scores = [v[1] for v in values]
                    
                    # Use median as baseline (more robust than mean)
                    baseline_value = statistics.median(metric_values)
                    confidence_score = statistics.mean(quality_scores)
                    
                    self.baseline_metrics[metric_name] = baseline_value
                    
                    # Store in database
                    baseline_cursor.execute('''
                        INSERT OR REPLACE INTO baseline_metrics
                        (metric_name, baseline_value, calculation_method, 
                         data_points_used, confidence_score, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        metric_name,
                        baseline_value,
                        "median",
                        len(values),
                        confidence_score,
                        datetime.now().isoformat()
                    ))
            
            baseline_conn.commit()
            baseline_conn.close()
            
            self.logger.info(f"Calculated {len(self.baseline_metrics)} baseline metrics")
            
        except Exception as e:
            self.logger.error(f"Error calculating baseline metrics: {e}")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Perform comprehensive performance analysis"""
        try:
            if not self.current_session:
                raise Exception("No active analysis session")
            
            print(f"{self.visual.status_indicator('analyzing')} Starting comprehensive performance analysis...")
            
            # Get analytics data for analysis
            analytics_data = self._get_analytics_data()
            if not analytics_data:
                raise Exception("No analytics data available for analysis")
            
            analysis_results = {
                'session_id': self.current_session.session_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'metrics_analyzed': {},
                'overall_performance_score': 0.0,
                'performance_grade': 'unknown',
                'trend_analysis': {},
                'optimization_opportunities': [],
                'recommendations': []
            }
            
            # Analyze each metric
            total_score = 0.0
            analyzed_count = 0
            
            for metric_name, data_points in analytics_data.items():
                if not self.anti_recursion.validate_analysis("analyze_metric", metric_name):
                    continue
                
                print(f"\r{self.visual.status_indicator('analyzing')} "
                      f"Analyzing {metric_name}...", end="")
                
                metric_analysis = self._analyze_metric(metric_name, data_points)
                if metric_analysis:
                    analysis_results['metrics_analyzed'][metric_name] = metric_analysis
                    total_score += metric_analysis['performance_score']
                    analyzed_count += 1
                    
                    if self.current_session:
                        self.current_session.metrics_analyzed += 1
                
                self.anti_recursion.release_analysis("analyze_metric", metric_name)
            
            # Calculate overall performance
            if analyzed_count > 0:
                analysis_results['overall_performance_score'] = total_score / analyzed_count
                analysis_results['performance_grade'] = self._get_performance_grade(
                    analysis_results['overall_performance_score']
                )
            
            # Perform trend analysis
            analysis_results['trend_analysis'] = self._perform_trend_analysis(analytics_data)
            
            # Generate optimization opportunities
            analysis_results['optimization_opportunities'] = self._identify_optimization_opportunities(
                analysis_results['metrics_analyzed']
            )
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
            
            # Use scaling framework for advanced analysis if available
            if self.scaling_framework:
                analysis_results = self._enhance_with_scaling_framework(analysis_results)
            
            # Update session
            if self.current_session:
                self.current_session.optimization_opportunities = analysis_results['optimization_opportunities']
                self.current_session.performance_grade = analysis_results['performance_grade']
                self.current_session.recommendations = analysis_results['recommendations']
            
            # Store results
            self._store_analysis_results(analysis_results)
            
            print(f"\n{self.visual.status_indicator('complete')} Performance analysis completed!")
            print(f"Overall Performance Score: {analysis_results['overall_performance_score']:.3f}")
            print(f"Performance Grade: {analysis_results['performance_grade']}")
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            raise
    
    def _get_analytics_data(self) -> Dict[str, List[Tuple[float, datetime]]]:
        """Get analytics data for performance analysis"""
        try:
            analytics_db_path = os.path.join(self.workspace_path, "databases", "analytics_collector.db")
            if not os.path.exists(analytics_db_path):
                return {}
            
            conn = sqlite3.connect(analytics_db_path)
            cursor = conn.cursor()
            
            # Get recent analytics data
            cursor.execute('''
                SELECT metric_name, metric_value, timestamp, quality_score
                FROM analytics_data_points
                WHERE datetime(timestamp) > datetime('now', '-24 hours')
                AND quality_score >= 0.5
                ORDER BY metric_name, timestamp
            ''')
            
            analytics_data = defaultdict(list)
            for row in cursor.fetchall():
                metric_name, metric_value_str, timestamp, quality_score = row
                try:
                    metric_value = json.loads(metric_value_str)
                    if isinstance(metric_value, (int, float)):
                        dt = datetime.fromisoformat(timestamp)
                        analytics_data[metric_name].append((metric_value, dt))
                except:
                    continue
            
            conn.close()
            
            # Filter metrics with sufficient data points
            filtered_data = {k: v for k, v in analytics_data.items() if len(v) >= 3}
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Error getting analytics data: {e}")
            return {}
    
    def _analyze_metric(self, metric_name: str, data_points: List[Tuple[float, datetime]]) -> Optional[Dict[str, Any]]:
        """Analyze a specific metric for performance insights"""
        try:
            if len(data_points) < 2:
                return None
            
            values = [dp[0] for dp in data_points]
            timestamps = [dp[1] for dp in data_points]
            
            # Validate data
            validation_data = {
                'metric_values': values,
                'timestamps': [ts.isoformat() for ts in timestamps],
                'metric_name': metric_name
            }
            is_valid, errors = self.dual_validator.validate_performance_data(validation_data)
            if not is_valid:
                self.logger.warning(f"Invalid data for {metric_name}: {errors}")
                return None
            
            # Get baseline
            baseline_value = self.baseline_metrics.get(metric_name, statistics.median(values))
            current_value = values[-1]  # Most recent value
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(
                current_value, baseline_value, metric_name
            )
            
            # Determine trend
            trend_direction, trend_confidence = self._calculate_trend(values)
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(values, timestamps)
            
            analysis_result = {
                'current_value': current_value,
                'baseline_value': baseline_value,
                'performance_score': performance_score,
                'trend_direction': trend_direction,
                'confidence_level': confidence_level,
                'data_points_analyzed': len(data_points),
                'time_span_hours': (timestamps[-1] - timestamps[0]).total_seconds() / 3600,
                'statistical_summary': {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values)
                }
            }
            
            # Validate analysis results
            is_valid, errors = self.dual_validator.validate_analysis_results(analysis_result)
            if not is_valid:
                self.logger.warning(f"Invalid analysis results for {metric_name}: {errors}")
                return None
            
            # Store performance metric
            self._store_performance_metric(metric_name, analysis_result)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing metric {metric_name}: {e}")
            return None
    
    def _calculate_performance_score(self, current_value: float, baseline_value: float, metric_name: str) -> float:
        """Calculate performance score based on current vs baseline"""
        try:
            if baseline_value == 0:
                return 0.5  # Neutral score if no baseline
            
            # Different scoring logic based on metric type
            if 'error' in metric_name.lower() or 'failure' in metric_name.lower():
                # Lower is better for error metrics
                if current_value <= baseline_value:
                    score = 1.0 - (current_value / baseline_value) * 0.5
                else:
                    score = 0.5 - min((current_value - baseline_value) / baseline_value, 0.5)
            elif 'usage' in metric_name.lower() and 'percent' in metric_name.lower():
                # Resource usage - moderate levels are good
                optimal_usage = 0.6  # 60% usage is considered optimal
                if abs(current_value / 100 - optimal_usage) < 0.1:
                    score = 1.0
                else:
                    score = 1.0 - abs(current_value / 100 - optimal_usage) * 2
            else:
                # Higher is generally better for performance metrics
                if current_value >= baseline_value:
                    score = 0.5 + min((current_value - baseline_value) / baseline_value, 0.5)
                else:
                    score = 0.5 * (current_value / baseline_value)
            
            return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return 0.5
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate trend direction and confidence"""
        try:
            if len(values) < 3:
                return "unknown", 0.0
            
            # Use linear regression to determine trend
            x = list(range(len(values)))
            y = values
            
            # Calculate slope
            n = len(values)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] * x[i] for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Calculate correlation coefficient for confidence
            mean_x = sum_x / n
            mean_y = sum_y / n
            
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
            denominator_x = sum((x[i] - mean_x) ** 2 for i in range(n))
            denominator_y = sum((y[i] - mean_y) ** 2 for i in range(n))
            
            if denominator_x == 0 or denominator_y == 0:
                return "stable", 0.0
            
            correlation = numerator / (denominator_x * denominator_y) ** 0.5
            confidence = abs(correlation)
            
            # Determine trend direction
            threshold = statistics.stdev(values) * 0.1  # 10% of standard deviation
            
            if abs(slope) < threshold:
                trend = "stable"
            elif slope > 0:
                trend = "improving"
            else:
                trend = "declining"
            
            return trend, confidence
            
        except Exception as e:
            self.logger.error(f"Error calculating trend: {e}")
            return "unknown", 0.0
    
    def _calculate_confidence_level(self, values: List[float], timestamps: List[datetime]) -> float:
        """Calculate confidence level based on data quality"""
        try:
            confidence_factors = []
            
            # Data quantity factor
            quantity_factor = min(len(values) / 10, 1.0)  # Max confidence at 10+ points
            confidence_factors.append(quantity_factor)
            
            # Data recency factor
            latest_time = max(timestamps)
            time_since_latest = (datetime.now() - latest_time).total_seconds() / 3600
            recency_factor = max(0, 1.0 - time_since_latest / 24)  # Decrease over 24 hours
            confidence_factors.append(recency_factor)
            
            # Data consistency factor (inverse of coefficient of variation)
            if len(values) > 1:
                mean_val = statistics.mean(values)
                if mean_val != 0:
                    cv = statistics.stdev(values) / abs(mean_val)
                    consistency_factor = max(0, 1.0 - cv)
                else:
                    consistency_factor = 0.5
            else:
                consistency_factor = 0.5
            confidence_factors.append(consistency_factor)
            
            # Overall confidence is the average of all factors
            return statistics.mean(confidence_factors)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence level: {e}")
            return 0.5
    
    def _perform_trend_analysis(self, analytics_data: Dict[str, List[Tuple[float, datetime]]]) -> Dict[str, Any]:
        """Perform comprehensive trend analysis across all metrics"""
        try:
            trend_summary = {
                'improving_metrics': [],
                'declining_metrics': [],
                'stable_metrics': [],
                'overall_trend_score': 0.0,
                'trend_confidence': 0.0
            }
            
            trend_scores = []
            confidence_scores = []
            
            for metric_name, data_points in analytics_data.items():
                values = [dp[0] for dp in data_points]
                trend_direction, confidence = self._calculate_trend(values)
                
                metric_trend = {
                    'metric_name': metric_name,
                    'trend_direction': trend_direction,
                    'confidence': confidence,
                    'recent_change_percent': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                }
                
                if trend_direction == 'improving':
                    trend_summary['improving_metrics'].append(metric_trend)
                    trend_scores.append(1.0)
                elif trend_direction == 'declining':
                    trend_summary['declining_metrics'].append(metric_trend)
                    trend_scores.append(-1.0)
                else:
                    trend_summary['stable_metrics'].append(metric_trend)
                    trend_scores.append(0.0)
                
                confidence_scores.append(confidence)
            
            # Calculate overall trend score
            if trend_scores:
                trend_summary['overall_trend_score'] = statistics.mean(trend_scores)
                trend_summary['trend_confidence'] = statistics.mean(confidence_scores)
            
            return trend_summary
            
        except Exception as e:
            self.logger.error(f"Error performing trend analysis: {e}")
            return {}
    
    def _identify_optimization_opportunities(self, metrics_analyzed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities based on analysis results"""
        opportunities = []
        
        try:
            for metric_name, analysis in metrics_analyzed.items():
                performance_score = analysis.get('performance_score', 0.5)
                trend_direction = analysis.get('trend_direction', 'unknown')
                
                # Low performance score indicates optimization opportunity
                if performance_score < 0.6:
                    opportunity = {
                        'metric_name': metric_name,
                        'opportunity_type': 'performance_improvement',
                        'current_score': performance_score,
                        'potential_improvement': 0.9 - performance_score,
                        'priority': 'high' if performance_score < 0.4 else 'medium',
                        'description': f"Improve {metric_name} performance from {performance_score:.2f} to target 0.9"
                    }
                    opportunities.append(opportunity)
                
                # Declining trend indicates preventive optimization opportunity
                if trend_direction == 'declining' and analysis.get('confidence_level', 0) > 0.7:
                    opportunity = {
                        'metric_name': metric_name,
                        'opportunity_type': 'trend_reversal',
                        'current_score': performance_score,
                        'potential_improvement': 0.3,
                        'priority': 'high' if performance_score < 0.5 else 'medium',
                        'description': f"Address declining trend in {metric_name} with high confidence"
                    }
                    opportunities.append(opportunity)
                
                # High variability indicates stabilization opportunity
                stats = analysis.get('statistical_summary', {})
                std_dev = stats.get('std_dev', 0)
                mean_val = stats.get('mean', 1)
                if mean_val != 0 and std_dev / abs(mean_val) > 0.3:  # CV > 30%
                    opportunity = {
                        'metric_name': metric_name,
                        'opportunity_type': 'variability_reduction',
                        'current_score': performance_score,
                        'potential_improvement': 0.2,
                        'priority': 'low',
                        'description': f"Reduce variability in {metric_name} for more consistent performance"
                    }
                    opportunities.append(opportunity)
            
            # Sort by priority and potential improvement
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            opportunities.sort(
                key=lambda x: (priority_order[x['priority']], x['potential_improvement']),
                reverse=True
            )
            
        except Exception as e:
            self.logger.error(f"Error identifying optimization opportunities: {e}")
        
        return opportunities
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        try:
            overall_score = analysis_results.get('overall_performance_score', 0.5)
            performance_grade = analysis_results.get('performance_grade', 'unknown')
            opportunities = analysis_results.get('optimization_opportunities', [])
            trend_analysis = analysis_results.get('trend_analysis', {})
            
            # Overall performance recommendations
            if overall_score < 0.5:
                recommendations.append(
                    "CRITICAL: Overall performance is below acceptable levels. "
                    "Immediate intervention required to address multiple performance issues."
                )
            elif overall_score < 0.7:
                recommendations.append(
                    "Performance improvement needed. Focus on the highest priority optimization opportunities."
                )
            else:
                recommendations.append(
                    "Good performance levels maintained. Continue monitoring for proactive optimization."
                )
            
            # Trend-based recommendations
            declining_count = len(trend_analysis.get('declining_metrics', []))
            improving_count = len(trend_analysis.get('improving_metrics', []))
            
            if declining_count > improving_count:
                recommendations.append(
                    f"WARNING: {declining_count} metrics showing declining trends. "
                    "Investigate root causes and implement corrective measures."
                )
            elif improving_count > declining_count:
                recommendations.append(
                    f"POSITIVE: {improving_count} metrics showing improvement. "
                    "Identify and replicate successful optimization strategies."
                )
            
            # Opportunity-specific recommendations
            high_priority_ops = [op for op in opportunities if op['priority'] == 'high']
            if high_priority_ops:
                recommendations.append(
                    f"Address {len(high_priority_ops)} high-priority optimization opportunities: "
                    f"{', '.join([op['metric_name'] for op in high_priority_ops[:3]])}"
                )
            
            # Scaling framework recommendations
            if self.scaling_framework and overall_score > 0.8:
                recommendations.append(
                    "Consider implementing advanced scaling strategies using the innovation framework "
                    "to push performance beyond current excellent levels."
                )
            
            # Data quality recommendations
            low_confidence_metrics = [
                name for name, analysis in analysis_results.get('metrics_analyzed', {}).items()
                if analysis.get('confidence_level', 0) < 0.6
            ]
            if low_confidence_metrics:
                recommendations.append(
                    f"Improve data quality and collection frequency for: {', '.join(low_confidence_metrics[:3])}"
                )
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _enhance_with_scaling_framework(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance analysis results using scaling innovation framework"""
        try:
            if not self.scaling_framework:
                return analysis_results
            
            # Add scaling framework insights
            analysis_results['scaling_framework_insights'] = {
                'framework_available': True,
                'advanced_optimizations': [],
                'scaling_opportunities': [],
                'innovation_potential': 0.0
            }
            
            # Calculate innovation potential based on performance scores
            metrics_analyzed = analysis_results.get('metrics_analyzed', {})
            if metrics_analyzed:
                high_performers = [
                    analysis for analysis in metrics_analyzed.values()
                    if analysis.get('performance_score', 0) > 0.8
                ]
                innovation_potential = len(high_performers) / len(metrics_analyzed)
                analysis_results['scaling_framework_insights']['innovation_potential'] = innovation_potential
                
                if innovation_potential > 0.7:
                    analysis_results['scaling_framework_insights']['scaling_opportunities'].extend([
                        "High innovation potential detected - consider implementing advanced scaling algorithms",
                        "Performance levels suitable for experimental optimization techniques",
                        "Ready for next-generation performance enhancement strategies"
                    ])
            
            # Add framework-specific recommendations
            overall_score = analysis_results.get('overall_performance_score', 0.5)
            if overall_score > 0.8:
                analysis_results['scaling_framework_insights']['advanced_optimizations'].extend([
                    "Implement adaptive scaling based on real-time performance metrics",
                    "Deploy machine learning-based predictive optimization",
                    "Enable autonomous performance tuning capabilities"
                ])
            
        except Exception as e:
            self.logger.error(f"Error enhancing with scaling framework: {e}")
        
        return analysis_results
    
    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade based on score"""
        if score >= self.performance_thresholds['excellent']:
            return "A+"
        elif score >= self.performance_thresholds['good']:
            return "B+"
        elif score >= self.performance_thresholds['fair']:
            return "C"
        elif score >= self.performance_thresholds['poor']:
            return "D"
        else:
            return "F"
    
    def _store_performance_metric(self, metric_name: str, analysis_result: Dict[str, Any]):
        """Store performance metric in database"""
        try:
            if not self.current_session:
                return
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_name=metric_name,
                current_value=analysis_result['current_value'],
                baseline_value=analysis_result['baseline_value'],
                performance_score=analysis_result['performance_score'],
                trend_direction=analysis_result['trend_direction'],
                confidence_level=analysis_result['confidence_level'],
                analysis_metadata=analysis_result
            )
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, metric_name, current_value, baseline_value, performance_score,
                 trend_direction, confidence_level, analysis_metadata, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.timestamp.isoformat(),
                metric.metric_name,
                metric.current_value,
                metric.baseline_value,
                metric.performance_score,
                metric.trend_direction,
                metric.confidence_level,
                json.dumps(metric.analysis_metadata),
                self.current_session.session_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing performance metric: {e}")
    
    def _store_analysis_results(self, analysis_results: Dict[str, Any]):
        """Store complete analysis results"""
        try:
            if not self.current_session:
                return
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update session with results
            cursor.execute('''
                UPDATE analysis_sessions
                SET metrics_analyzed = ?,
                    optimization_opportunities = ?,
                    performance_grade = ?,
                    recommendations = ?
                WHERE session_id = ?
            ''', (
                len(analysis_results.get('metrics_analyzed', {})),
                json.dumps(analysis_results.get('optimization_opportunities', [])),
                analysis_results.get('performance_grade', 'unknown'),
                json.dumps(analysis_results.get('recommendations', [])),
                self.current_session.session_id
            ))
            
            # Store optimization recommendations
            for opportunity in analysis_results.get('optimization_opportunities', []):
                cursor.execute('''
                    INSERT INTO optimization_recommendations
                    (timestamp, session_id, metric_name, recommendation_type,
                     description, expected_improvement, implementation_priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    self.current_session.session_id,
                    opportunity['metric_name'],
                    opportunity['opportunity_type'],
                    opportunity['description'],
                    opportunity['potential_improvement'],
                    opportunity['priority']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing analysis results: {e}")
    
    def stop_analysis_session(self):
        """Stop the current performance analysis session"""
        try:
            if not self.current_session:
                self.logger.warning("No active analysis session to stop")
                return
            
            self.current_session.end_time = datetime.now()
            self.current_session.status = "completed"
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE analysis_sessions
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
                           f"Performance analysis session completed: {self.current_session.session_id}")
            
            # Generate final report
            self._generate_analysis_report()
            
        except Exception as e:
            self.logger.error(f"Error stopping analysis session: {e}")
    
    def _generate_analysis_report(self):
        """Generate comprehensive analysis session report"""
        try:
            if not self.current_session or not self.current_session.end_time:
                return
            
            report = {
                'session_summary': asdict(self.current_session),
                'analysis_duration': str(self.current_session.end_time - self.current_session.start_time),
                'performance_insights': {
                    'overall_grade': self.current_session.performance_grade,
                    'optimization_opportunities_count': len(self.current_session.optimization_opportunities),
                    'recommendations_count': len(self.current_session.recommendations)
                },
                'scaling_framework_integration': self.scaling_framework is not None,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save report
            report_path = os.path.join(self.workspace_path, 
                                     f"performance_analysis_report_{self.current_session.session_id}.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Analysis report saved: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating analysis report: {e}")

def main():
    """Main execution function for Step 4: Performance Analysis"""
    print("=" * 80)
    print("STEP 4: Performance Analysis - Enterprise Performance Analysis System")
    print("=" * 80)
    
    try:
        # Initialize analyzer
        workspace = os.getcwd()
        analyzer = PerformanceAnalyzer(workspace)
        
        print(f"{analyzer.visual.status_indicator('processing')} Initializing performance analyzer...")
        
        # Start analysis session
        session_id = analyzer.start_analysis_session()
        print(f"{analyzer.visual.status_indicator('active')} Analysis session started: {session_id}")
        
        # Perform comprehensive analysis
        analysis_results = analyzer.analyze_performance()
        
        # Display key results
        print(f"\n{analyzer.visual.status_indicator('complete')} Analysis Results:")
        print(f"  METRICS Metrics Analyzed: {len(analysis_results.get('metrics_analyzed', {}))}")
        print(f"  TARGET Overall Performance Score: {analysis_results.get('overall_performance_score', 0):.3f}")
        print(f"  ACHIEVEMENT Performance Grade: {analysis_results.get('performance_grade', 'unknown')}")
        print(f"  TOOL Optimization Opportunities: {len(analysis_results.get('optimization_opportunities', []))}")
        print(f"  IDEA Recommendations: {len(analysis_results.get('recommendations', []))}")
        
        # Stop analysis session
        analyzer.stop_analysis_session()
        
        print(f"\n{analyzer.visual.status_indicator('complete')} Step 4: Performance Analysis completed successfully!")
        print(f"Database: {analyzer.db_path}")
        print(f"Log file: {analyzer.log_path}")
        
        return True
        
    except Exception as e:
        print(f"ERROR Step 4 failed: {e}")
        return False

if __name__ == "__main__":
    main()
