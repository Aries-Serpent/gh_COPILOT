# Migration Procedures Guide
============================

🔄 Environment migration and upgrade procedures

## Migration Types

### Environment Migration
**Supported Environments**:
- **Development**: `$GH_COPILOT_WORKSPACE`
- **Staging**: `$GH_COPILOT_WORKSPACE`
- **Production**: `e:/_copilot_production`

**Migration Paths**:
- Development → Staging
- Staging → Production
- Cross-platform migration (Windows ↔ Linux)

### Version Upgrades
- Database schema updates
- Application version upgrades
- Configuration migrations
- Template and static file updates

### Component Migration
- **Databases**: SQLite files with schema validation
- **Scripts**: Python scripts and modules
- **Templates**: HTML, CSS, JavaScript files
- **Configuration**: Environment-specific settings

## Pre-Migration Planning

### Migration Assessment
```bash
# Run migration assessment
python migration_scripts/assess_migration.py \
  --source $GH_COPILOT_WORKSPACE \
  --target $GH_COPILOT_WORKSPACE
```

### Compatibility Check
```python
def check_migration_compatibility(source_env, target_env):
    checks = {
        "python_version": check_python_compatibility(),
        "dependencies": check_dependency_compatibility(),
        "database_schema": check_database_schema(),
        "file_permissions": check_file_permissions(),
        "disk_space": check_disk_space_requirements()
    }
    return checks
```

### Migration Planning
1. **Component Inventory**:
   - Database files and schemas
   - Application scripts
   - Template and static files
   - Configuration files

2. **Dependency Mapping**:
   - Python package versions
   - System requirements
   - File system permissions
   - Network configurations

3. **Risk Assessment**:
   - Data loss potential
   - Downtime requirements
   - Rollback complexity
   - Business impact

## Migration Procedures

### Pre-Migration Checklist
- [ ] Source environment backup completed
- [ ] Target environment prepared
- [ ] Dependency compatibility verified
- [ ] Downtime window scheduled
- [ ] Rollback plan documented
- [ ] Stakeholder notification sent

### Development to Staging Migration

#### Step 1: Environment Preparation
```bash
# Create staging environment
mkdir -p $GH_COPILOT_WORKSPACE
cd $GH_COPILOT_WORKSPACE

# Setup Python environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install web dashboard dependencies
pip install -r ../requirements.txt  # install only if migrating the dashboard
```

#### Step 2: Database Migration
```bash
# Copy production database
cp $GH_COPILOT_WORKSPACE/production.db $GH_COPILOT_WORKSPACE/

# Verify database integrity
python migration_scripts/verify_database.py \
  --database $GH_COPILOT_WORKSPACE/production.db
```

#### Step 3: Application Migration
```bash
# Copy web GUI components
cp -r $GH_COPILOT_WORKSPACE/web_gui/scripts $GH_COPILOT_WORKSPACE/
cp -r $GH_COPILOT_WORKSPACE/templates $GH_COPILOT_WORKSPACE/
cp -r $GH_COPILOT_WORKSPACE/web_gui_documentation $GH_COPILOT_WORKSPACE/

# Update configuration paths
python migration_scripts/update_config_paths.py \
  --target $GH_COPILOT_WORKSPACE
```

#### Step 4: Validation
```bash
# Start staging application
cd $(os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd())))/web_gui/scripts/flask_apps
python enterprise_dashboard.py &

# Run validation tests
python ../../migration_scripts/validate_staging.py
```

### Staging to Production Migration

#### Step 1: Production Preparation
```bash
# Stop production services (if running)
systemctl stop gh-copilot-web-gui  # Linux
# or manually stop on Windows

# Backup current production
python backup_scripts/full_backup.py \
  --source e:/_copilot_production \
  --destination e:/_copilot_backups/pre_migration
```

#### Step 2: Production Deployment
```bash
# Deploy validated staging to production
python migration_scripts/deploy_to_production.py \
  --source $(os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))) \
  --target e:/_copilot_production \
  --validate
```

#### Step 3: Production Validation
```bash
# Start production services
cd e:/_copilot_production/web_gui/scripts/flask_apps
python enterprise_dashboard.py &

# Run production validation
python migration_scripts/validate_production.py

# Monitor for issues
python monitoring_scripts/production_monitor.py
```

## Web Interface Migration Tools

### Migration Dashboard
Access migration tools through the web interface:
1. Navigate to http://localhost:5000/migration
2. Select source and target environments
3. Choose migration components:
   - [ ] Databases
   - [ ] Scripts and applications
   - [ ] Templates and static files
   - [ ] Configuration files

### Migration Wizard
```python
class MigrationWizard:
    def __init__(self, source_env, target_env):
        self.source_env = source_env
        self.target_env = target_env
    
    def start_migration(self):
        steps = [
            self.validate_environments,
            self.backup_target,
            self.copy_databases,
            self.copy_applications,
            self.copy_templates,
            self.update_configurations,
            self.validate_migration
        ]
        
        for step in steps:
            result = step()
            if not result.success:
                return self.handle_migration_error(result)
        
        return MigrationResult(success=True)
```

## Advanced Migration Scenarios

### Cross-Platform Migration (Windows to Linux)
```bash
# Handle path separators
python migration_scripts/cross_platform_migrate.py \
  --source "e:\gh_COPILOT" \
  --target "/opt/copilot/production" \
  --platform-conversion

# Fix file permissions (Linux)
chmod +x /opt/copilot/production/web_gui/scripts/flask_apps/*.py
```

### Database Schema Migration
```python
def migrate_database_schema(source_db, target_db, schema_version):
    """Migrate database schema between versions"""
    
    # Backup current database
    backup_database(target_db)
    
    # Apply schema migrations
    migrations = get_schema_migrations(schema_version)
    
    for migration in migrations:
        try:
            execute_migration(target_db, migration)
            log_migration_success(migration)
        except Exception as e:
            log_migration_error(migration, e)
            rollback_migration(target_db)
            raise
```

### Zero-Downtime Migration
```python
def zero_downtime_migration():
    """Blue-green deployment for zero downtime"""
    
    # Setup green environment
    setup_green_environment()
    
    # Migrate data to green
    migrate_to_green()
    
    # Validate green environment
    if validate_green_environment():
        # Switch traffic to green
        switch_to_green()
        # Cleanup blue environment
        cleanup_blue_environment()
    else:
        # Rollback to blue
        cleanup_green_environment()
        raise MigrationError("Green validation failed")
```

## Rollback Procedures

### Immediate Rollback
```bash
# Stop current services
pkill -f "enterprise_dashboard.py"

# Restore from pre-migration backup
python backup_scripts/restore_backup.py \
  --backup e:/_copilot_backups/pre_migration.tar.gz \
  --target e:/_copilot_production

# Restart services
cd e:/_copilot_production/web_gui/scripts/flask_apps
python enterprise_dashboard.py
```

### Partial Rollback
```bash
# Rollback specific components
python migration_scripts/partial_rollback.py \
  --component database \
  --backup pre_migration_database.db

# Validate partial rollback
python migration_scripts/validate_partial_rollback.py
```

### Emergency Rollback
```bash
# Emergency procedure for critical issues
python emergency_scripts/emergency_rollback.py \
  --restore-last-known-good \
  --notify-stakeholders \
  --log-incident
```

## Migration Validation

### Automated Testing
```python
def run_migration_tests():
    """Comprehensive migration validation"""
    
    tests = [
        test_database_connectivity,
        test_web_interface_accessibility,
        test_api_endpoints,
        test_template_rendering,
        test_performance_benchmarks,
        test_security_configurations
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        if not result.passed:
            log_test_failure(test, result)
    
    return MigrationTestResults(results)
```

### Performance Validation
```bash
# Run performance benchmarks
python performance_scripts/benchmark_migration.py \
  --before-migration baseline.json \
  --after-migration current.json \
  --generate-report
```

### Data Integrity Validation
```python
def validate_data_integrity():
    """Ensure data integrity post-migration"""
    
    # Compare record counts
    source_counts = get_table_counts(source_db)
    target_counts = get_table_counts(target_db)
    
    # Validate checksums
    source_checksums = calculate_table_checksums(source_db)
    target_checksums = calculate_table_checksums(target_db)
    
    # Compare critical data
    return compare_data_integrity(
        source_counts, target_counts,
        source_checksums, target_checksums
    )
```

## Best Practices

### Migration Planning
- Always perform full backups before migration
- Test migration procedures in non-production environments
- Document all configuration changes
- Plan for rollback scenarios
- Communicate with stakeholders

### Risk Mitigation
- Use staging environments for validation
- Implement automated testing
- Monitor system health post-migration
- Have emergency contacts ready
- Maintain detailed logs

### Post-Migration
- Validate all functionality
- Monitor performance metrics
- Update documentation
- Train users on changes
- Schedule post-migration review

## Troubleshooting Migration Issues

### Common Migration Problems
1. **Path Resolution Issues**: Fix absolute/relative paths
2. **Permission Problems**: Adjust file/directory permissions
3. **Database Locks**: Close connections before migration
4. **Port Conflicts**: Update port configurations
5. **Template Not Found**: Verify template paths

### Migration Recovery
```bash
# If migration fails mid-process
python migration_scripts/recovery_migration.py \
  --checkpoint migration_checkpoint.json \
  --resume-from database_copy
```

### Support Escalation
- **Level 1**: Check migration logs and common issues
- **Level 2**: Contact technical support with logs
- **Level 3**: Emergency rollback and incident response

Generated: 2025-01-06T04:53:00Z
