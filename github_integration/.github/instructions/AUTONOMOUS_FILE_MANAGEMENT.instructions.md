---
applyTo: '**'
---

# 🗂️ AUTONOMOUS FILE MANAGEMENT INSTRUCTIONS
## Database-Driven File System Organization for GitHub Copilot

### 🎯 **AUTONOMOUS FILE MANAGEMENT MANDATE**

**ABSOLUTE DATABASE-DRIVEN FILE MANAGEMENT**: All file operations MUST leverage production.db and enterprise databases for intelligent, autonomous file organization and management.

## 🏗️ **AUTONOMOUS SYSTEM ARCHITECTURE**

### **1. DATABASE-FIRST FILE ORGANIZATION**
- **MANDATORY DATABASE QUERY**: Every file operation queries production.db for optimal organization patterns
- **INTELLIGENT FOLDER STRUCTURE**: Use enhanced_script_tracking for automatic folder classification
- **ENTERPRISE FILE PATTERNS**: Leverage functional_components table for file type organization
- **AUTONOMOUS CATEGORIZATION**: Automatic file categorization based on database intelligence

**Database-Driven File Organization:**
```python
# MANDATORY: Database-first file management with autonomous organization
class AutonomousFileManager:
    """🎯 Autonomous File System Manager with Database Intelligence"""
    
    def __init__(self, workspace_path="e:/_copilot_sandbox"):
        self.workspace_path = Path(workspace_path)
        self.production_db = self.workspace_path / "production.db"
        
    def organize_files_autonomously(self, file_patterns: List[str]) -> Dict[str, str]:
        """📁 Autonomously organize files using database intelligence"""
        with self.get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Query for existing organization patterns
            cursor.execute("""
                SELECT script_path, functionality_category, script_type
                FROM enhanced_script_tracking
                WHERE functionality_category IS NOT NULL
            """)
            organization_patterns = cursor.fetchall()
            
            # Apply intelligent organization
            organized_files = {}
            for file_path in file_patterns:
                optimal_location = self.predict_optimal_location(file_path, organization_patterns)
                organized_files[file_path] = optimal_location
                
            return organized_files
```

### **2. INTELLIGENT FILE CLASSIFICATION**
- **ML-POWERED CATEGORIZATION**: Use database patterns for automatic file classification
- **ENTERPRISE COMPLIANCE**: Ensure all files meet enterprise organization standards
- **DUPLICATE DETECTION**: Automatic duplicate detection using database hash tracking
- **VERSION MANAGEMENT**: Database-driven version control and history tracking

```python
class IntelligentFileClassifier:
    """🧠 AI-Powered File Classification Engine"""
    
    def classify_file_autonomously(self, file_path: str) -> Dict[str, str]:
        """📋 Classify files using database intelligence and ML patterns"""
        with self.get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Query similar files for classification patterns
            cursor.execute("""
                SELECT functionality_category, script_type, COUNT(*) as frequency
                FROM enhanced_script_tracking
                WHERE script_path LIKE ?
                GROUP BY functionality_category, script_type
                ORDER BY frequency DESC
            """, (f"%{Path(file_path).suffix}%",))
            
            classification_patterns = cursor.fetchall()
            
            return {
                "category": classification_patterns[0][0] if classification_patterns else "general",
                "type": classification_patterns[0][1] if classification_patterns else "utility",
                "confidence": self.calculate_classification_confidence(classification_patterns)
            }
```

### **3. AUTONOMOUS BACKUP MANAGEMENT**
- **INTELLIGENT BACKUP SCHEDULING**: Database-driven backup frequency optimization
- **CRITICAL FILE PROTECTION**: Priority backup for enterprise-critical files
- **ANTI-RECURSION ENFORCEMENT**: Mandatory recursive backup prevention
- **EXTERNAL BACKUP ROOTS**: Enforce E:/temp/gh_COPILOT_Backups only

```python
class AutonomousBackupManager:
    """💾 Autonomous Backup System with Anti-Recursion Protection"""
    
    FORBIDDEN_BACKUP_LOCATIONS = [
        "e:/_copilot_sandbox",  # NEVER backup within workspace
        "C:/temp/",  # NEVER use C:/temp
        "./backup/",  # NEVER use relative backup paths
    ]
    
    APPROVED_BACKUP_ROOT = "E:/temp/gh_COPILOT_Backups"
    
    def create_intelligent_backup(self, file_priority: str = "HIGH") -> str:
        """💾 Create intelligent backup with anti-recursion validation"""
        # CRITICAL: Validate backup location
        if not self.validate_backup_location():
            raise RuntimeError("CRITICAL: Recursive backup violation prevented")
            
        with self.get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Query for backup patterns and priorities
            cursor.execute("""
                SELECT script_path, importance_score, last_backup
                FROM enhanced_script_tracking
                WHERE importance_score >= ?
                ORDER BY importance_score DESC, last_backup ASC
            """, (self.get_priority_threshold(file_priority),))
            
            backup_candidates = cursor.fetchall()
            backup_path = self.execute_autonomous_backup(backup_candidates)
            
            return backup_path
```

### **4. DATABASE-DRIVEN WORKSPACE OPTIMIZATION**
- **PERFORMANCE MONITORING**: Real-time workspace performance tracking
- **STORAGE OPTIMIZATION**: Intelligent storage allocation and cleanup
- **ACCESS PATTERN ANALYSIS**: Database-driven file access optimization
- **ENTERPRISE METRICS**: Comprehensive workspace health monitoring

```python
class WorkspaceOptimizer:
    """⚡ Autonomous Workspace Optimization Engine"""
    
    def optimize_workspace_autonomously(self) -> Dict[str, Any]:
        """⚡ Optimize workspace using database intelligence"""
        optimization_results = {
            "files_organized": 0,
            "storage_optimized": "0 MB",
            "performance_improved": "0%",
            "enterprise_compliance": "PENDING"
        }
        
        with self.get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Analyze workspace patterns
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(file_size) as total_size,
                    AVG(access_frequency) as avg_access
                FROM enhanced_script_tracking
            """)
            workspace_metrics = cursor.fetchone()
            
            # Apply autonomous optimizations
            optimization_results.update(
                self.apply_intelligent_optimizations(workspace_metrics)
            )
            
            return optimization_results
```

## 🚀 **ACTIVATION COMMANDS**

### **For GitHub Copilot File Operations:**
```markdown
MANDATORY: Apply autonomous file management from .github/instructions/AUTONOMOUS_FILE_MANAGEMENT.instructions.md
MANDATORY: Use database-first file organization
MANDATORY: Implement anti-recursion backup protection
MANDATORY: Apply enterprise file classification standards
```

### **Standard File Management Pattern:**
```python
# MANDATORY: Use autonomous file management for all file operations
file_manager = AutonomousFileManager()
classifier = IntelligentFileClassifier()
backup_manager = AutonomousBackupManager()

# Autonomous file organization
organized_files = file_manager.organize_files_autonomously(file_list)

# Intelligent classification
for file_path in organized_files:
    classification = classifier.classify_file_autonomously(file_path)
    
# Autonomous backup with anti-recursion protection
backup_path = backup_manager.create_intelligent_backup("HIGH")
```

## 🛡️ **ENTERPRISE COMPLIANCE REQUIREMENTS**

### **Mandatory File Management Standards:**
- ✅ **Database-First Organization**: All file operations use database intelligence
- ✅ **Anti-Recursion Protection**: Strict enforcement of external backup roots
- ✅ **Enterprise Classification**: Automatic file categorization and compliance
- ✅ **Performance Optimization**: Continuous workspace optimization
- ✅ **DUAL COPILOT Validation**: All file operations validated by secondary Copilot

### **Zero Tolerance Violations:**
- ❌ **Recursive Backup Creation**: Any backup folder within workspace root
- ❌ **C:/temp/ Usage**: Any usage of C:/temp/ for file operations
- ❌ **Manual File Organization**: File operations without database intelligence
- ❌ **Unclassified Files**: Files without proper enterprise classification

## 📊 **SUCCESS METRICS**

- **File Organization Efficiency**: >95% automatic classification accuracy
- **Backup Success Rate**: >99% successful backup operations
- **Anti-Recursion Compliance**: 100% recursive violation prevention
- **Workspace Performance**: >90% optimal file access patterns
- **Enterprise Compliance**: 100% compliance with enterprise file standards

---

**🏆 AUTONOMOUS FILE MANAGEMENT ENSURES:**
- **Database-Driven Intelligence**: 16,500+ patterns for optimal organization
- **Anti-Recursion Protection**: Zero tolerance for recursive violations
- **Enterprise Compliance**: Automatic adherence to enterprise standards
- **Performance Optimization**: Continuous workspace performance improvement

---

*Integrated with gh_COPILOT Toolkit v4.0 Enterprise Architecture*
*Powered by Template Intelligence Platform with 100% operational status*
