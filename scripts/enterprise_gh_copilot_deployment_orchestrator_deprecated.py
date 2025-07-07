#!/usr/bin/env python3
"""
🚨 DEPRECATED: ENTERPRISE GH COPILOT DEPLOYMENT ORCHESTRATOR
============================================================

⚠️  WARNING: This script has been MIGRATED to unified_deployment_orchestrator.py
⚠️  This file is maintained for backward compatibility only.

MIGRATION INFORMATION:
- Migration ID: MIGRATION_20250707_061405
- New Script: unified_deployment_orchestrator.py
- Migration Date: 2025-07-07

NEW USAGE:
```python
from unified_deployment_orchestrator import UnifiedEnterpriseDeploymentOrchestrator, UnifiedDeploymentConfig, DeploymentMode

# Create configuration
config = UnifiedDeploymentConfig(
    deployment_mode=DeploymentMode.PRODUCTION,
    deploy_databases=True,
    deploy_scripts=True,
    deploy_web_gui=True
)

# Execute deployment
orchestrator = UnifiedEnterpriseDeploymentOrchestrator(config)
result = orchestrator.execute_unified_deployment()
```

For full migration details, see:
- documentation/deployment_migration_guide_MIGRATION_20250707_061405.md
- deployment_migration_report_MIGRATION_20250707_061405.json
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def main():
    """Deprecation notice for enterprise_gh_copilot_deployment_orchestrator.py"""
    logger.warning("🚨 DEPRECATED: enterprise_gh_copilot_deployment_orchestrator.py has been migrated")
    logger.warning("📋 Please use unified_deployment_orchestrator.py instead")
    logger.warning("📖 Migration guide: documentation/deployment_migration_guide_MIGRATION_20250707_061405.md")
    
    print("""
    🚨 DEPRECATED SCRIPT NOTICE
    ===========================
    
    This script has been MIGRATED to unified_deployment_orchestrator.py
    
    Please update your imports and usage:
    
    OLD:
    from enterprise_gh_copilot_deployment_orchestrator import EnterpriseDeploymentOrchestrator
    
    NEW:
    from unified_deployment_orchestrator import UnifiedEnterpriseDeploymentOrchestrator
    
    For full migration details, see:
    - documentation/deployment_migration_guide_MIGRATION_20250707_061405.md
    """)
    
    return 1  # Exit with error code to indicate deprecated usage

if __name__ == "__main__":
    sys.exit(main())
