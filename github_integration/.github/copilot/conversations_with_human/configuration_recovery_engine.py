#!/usr/bin/env python3
"""
# Tool: Configuration Recovery Engine
> Generated: 2025-07-03 21:30:06 | Author: mbaetiong

Roles: [Primary: Configuration Recovery Engineer], [Secondary: System State Restoration Specialist]
Energy: [5]
Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

MISSION: Complete configuration recovery engine for disaster recovery scenarios
Capabilities: Multi-format config restoration, dependency resolution, validation testing
"""

import os
import sys
import sqlite3
import json
import yaml
import configparser
import toml
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import tempfile
import subprocess
from jinja2 import Template, Environment, FileSystemLoader

@dataclass
class ConfigurationMetadata:
    """Metadata structure for configuration information"""
    config_id: int
    config_category: str
    config_key: str
    config_type: str
    file_path: str
    is_critical: bool
    recovery_priority: int
    validation_schema: Optional[str]

@dataclass
class RecoveryResult:
    """Result structure for configuration recovery operations"""
    success: bool
    config_path: str
    config_type: str
    restored_content: str
    validation_passed: bool
    error_message: Optional[str]
    execution_time: float
    file_size: int
    backup_created: bool

class ConfigurationRecoveryEngine:
    """Advanced configuration recovery engine with multi-format support"""
    
    def __init__(self, database_path: str = "production.db", 
                 output_directory: str = "recovered_configs",
                 backup_directory: str = "config_backups"):
        self.database_path = Path(database_path)
        self.output_directory = Path(output_directory)
        self.backup_directory = Path(backup_directory)
        self.template_directory = Path("config_templates")
        
        # Ensure directories exist
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.template_directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('configuration_recovery.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_directory)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Recovery statistics
        self.recovery_stats = {
            "total_configurations": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "validation_passes": 0,
            "validation_failures": 0,
            "backups_created": 0,
            "start_time": None,
            "end_time": None
        }
        
        # Status indicators
        self.indicators = {
            'info': '[INFO]',
            'success': '[SUCCESS]',
            'warning': '[WARN]',
            'error': '[ERROR]',
            'processing': '[PROC]',
            'validation': '[VALIDATE]',
            'recovery': '[RECOVER]',
            'backup': '[BACKUP]'
        }
        
        # Initialize configuration templates
        self._initialize_config_templates()
    
    def _initialize_config_templates(self) -> None:
        """Initialize configuration templates for different types"""
        templates = {
            'application_config': {
                'filename': 'application_config.json.j2',
                'content': '''{
  "application": {
    "name": "{{ app_name }}",
    "version": "{{ app_version }}",
    "environment": "{{ environment }}",
    "debug": {{ debug_mode | lower }},
    "log_level": "{{ log_level }}"
  },
  "database": {
    "url": "{{ database_url }}",
    "pool_size": {{ db_pool_size }},
    "timeout": {{ db_timeout }},
    "retry_attempts": {{ db_retry_attempts }}
  },
  "security": {
    "secret_key": "{{ secret_key }}",
    "jwt_expiry": {{ jwt_expiry }},
    "encryption_enabled": {{ encryption_enabled | lower }},
    "rate_limiting": {
      "enabled": {{ rate_limiting_enabled | lower }},
      "requests_per_minute": {{ rate_limit_rpm }}
    }
  },
  "features": {
    "caching_enabled": {{ caching_enabled | lower }},
    "monitoring_enabled": {{ monitoring_enabled | lower }},
    "backup_enabled": {{ backup_enabled | lower }}
  },
  "generated_at": "{{ generation_timestamp }}",
  "recovery_metadata": {
    "original_config_id": {{ config_id }},
    "recovery_priority": {{ recovery_priority }},
    "is_critical": {{ is_critical | lower }}
  }
}'''
            },
            'deployment_config': {
                'filename': 'deployment_config.yaml.j2',
                'content': '''# Deployment Configuration
# Generated: {{ generation_timestamp }}
# Recovery Priority: {{ recovery_priority }}

version: '{{ config_version }}'

services:
  {{ service_name }}:
    image: {{ docker_image }}
    ports:
      - "{{ host_port }}:{{ container_port }}"
    environment:
      - DATABASE_URL={{ database_url }}
      - SECRET_KEY={{ secret_key }}
      - LOG_LEVEL={{ log_level }}
      - ENVIRONMENT={{ environment }}
    volumes:
      - {{ volume_mapping }}
    restart: {{ restart_policy }}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{{ container_port }}/api/health"]
      interval: {{ health_check_interval }}
      timeout: {{ health_check_timeout }}
      retries: {{ health_check_retries }}

networks:
  {{ network_name }}:
    driver: {{ network_driver }}

volumes:
  {{ volume_name }}:
    driver: {{ volume_driver }}

# Recovery metadata
x-recovery-info:
  config_id: {{ config_id }}
  original_path: "{{ original_path }}"
  recovery_timestamp: "{{ generation_timestamp }}"
  is_critical: {{ is_critical }}
'''
            },
            'dependencies': {
                'filename': 'requirements.txt.j2',
                'content': '''# Requirements File
# Generated: {{ generation_timestamp }}
# Recovery Priority: {{ recovery_priority }}

# Core Dependencies
{% for package in core_packages %}
{{ package.name }}=={{ package.version }}{% if package.extras %} # {{ package.extras }}{% endif %}
{% endfor %}

# Development Dependencies
{% for package in dev_packages %}
{{ package.name }}=={{ package.version }} # dev{% if package.extras %}, {{ package.extras }}{% endif %}
{% endfor %}

# Optional Dependencies
{% for package in optional_packages %}
# {{ package.name }}=={{ package.version }} # optional: {{ package.description }}
{% endfor %}

# Recovery metadata (as comments)
# Original config ID: {{ config_id }}
# Recovery timestamp: {{ generation_timestamp }}
# Critical configuration: {{ is_critical }}
'''
            },
            'environment': {
                'filename': 'environment.env.j2',
                'content': '''# Environment Configuration
# Generated: {{ generation_timestamp }}
# Recovery Priority: {{ recovery_priority }}

# Application Settings
APP_NAME={{ app_name }}
APP_VERSION={{ app_version }}
ENVIRONMENT={{ environment }}
DEBUG={{ debug_mode | upper }}
LOG_LEVEL={{ log_level | upper }}

# Database Configuration
DATABASE_URL={{ database_url }}
DB_POOL_SIZE={{ db_pool_size }}
DB_TIMEOUT={{ db_timeout }}

# Security Configuration
SECRET_KEY={{ secret_key }}
JWT_SECRET={{ jwt_secret }}
ENCRYPTION_KEY={{ encryption_key }}

# Service Configuration
{% for service, config in services.items() %}
{{ service | upper }}_HOST={{ config.host }}
{{ service | upper }}_PORT={{ config.port }}
{{ service | upper }}_ENABLED={{ config.enabled | upper }}
{% endfor %}

# Feature Flags
{% for feature, enabled in features.items() %}
FEATURE_{{ feature | upper }}={{ enabled | upper }}
{% endfor %}

# Recovery Metadata
RECOVERY_CONFIG_ID={{ config_id }}
RECOVERY_TIMESTAMP={{ generation_timestamp }}
RECOVERY_CRITICAL={{ is_critical | upper }}
'''
            },
            'general_config': {
                'filename': 'general_config.ini.j2',
                'content': '''# General Configuration File
# Generated: {{ generation_timestamp }}
# Recovery Priority: {{ recovery_priority }}

[DEFAULT]
app_name = {{ app_name }}
app_version = {{ app_version }}
environment = {{ environment }}

[database]
url = {{ database_url }}
pool_size = {{ db_pool_size }}
timeout = {{ db_timeout }}
retry_attempts = {{ db_retry_attempts }}

[logging]
level = {{ log_level }}
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
file_path = {{ log_file_path }}
max_file_size = {{ log_max_size }}
backup_count = {{ log_backup_count }}

[security]
secret_key = {{ secret_key }}
jwt_expiry = {{ jwt_expiry }}
encryption_enabled = {{ encryption_enabled }}

{% for section, options in custom_sections.items() %}
[{{ section }}]
{% for key, value in options.items() %}
{{ key }} = {{ value }}
{% endfor %}

{% endfor %}
[recovery_metadata]
config_id = {{ config_id }}
original_path = {{ original_path }}
recovery_timestamp = {{ generation_timestamp }}
is_critical = {{ is_critical }}
'''
            }
        }
        
        # Create template files
        for category, template_data in templates.items():
            template_path = self.template_directory / template_data['filename']
            if not template_path.exists():
                with open(template_path, 'w') as f:
                    f.write(template_data['content'])
                self.logger.info(f"Created config template: {template_path}")
    
    def load_configuration_metadata(self) -> List[ConfigurationMetadata]:
        """Load configuration metadata from database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT config_id, config_category, config_key, config_type,
                       file_path, is_critical, recovery_priority, validation_schema
                FROM system_configurations
                ORDER BY recovery_priority ASC, config_category, config_key
            """)
            
            configurations = [
for row in cursor.fetchall():
                config = ConfigurationMetadata(
                    config_id=row[0],
                    config_category=row[1],
                    config_key=row[2],
                    config_type=row[3],
                    file_path=row[4],
                    is_critical=bool(row[5]),
                    recovery_priority=row[6],
                    validation_schema=row[7]
                )
                configurations.append(config)
            
            conn.close()
            self.logger.info(f"Loaded metadata for {len(configurations)} configurations")
            return configurations
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration metadata: {e}")
            return []
    
    def analyze_configuration_content(self, config_content: str, 
                                    config_type: str) -> Dict[str, Any]:
        """Analyze configuration content to extract key components"""
        try:
            analysis = {
                "format": config_type,
                "size": len(config_content),
                "line_count": len(config_content.splitlines()),
                "sections": [],
                "keys": [],
                "values_sample": {},
                "structure": {}
            }
            
            if config_type == 'json':
                data = json.loads(config_content)
                analysis["structure"] = self._analyze_json_structure(data)
                analysis["keys"] = self._extract_json_keys(data)
                analysis["values_sample"] = self._sample_json_values(data, 5)
                
            elif config_type in ['yaml', 'yml']:
                data = yaml.safe_load(config_content)
                analysis["structure"] = self._analyze_yaml_structure(data)
                analysis["keys"] = self._extract_yaml_keys(data)
                analysis["values_sample"] = self._sample_yaml_values(data, 5)
                
            elif config_type == 'ini':
                config = configparser.ConfigParser()
                config.read_string(config_content)
                analysis["sections"] = list(config.sections())
                analysis["keys"] = self._extract_ini_keys(config)
                analysis["values_sample"] = self._sample_ini_values(config, 5)
                
            elif config_type == 'toml':
                data = toml.loads(config_content)
                analysis["structure"] = self._analyze_toml_structure(data)
                analysis["keys"] = self._extract_toml_keys(data)
                analysis["values_sample"] = self._sample_toml_values(data, 5)
                
            elif config_type == 'env':
                lines = [line.strip() for line in config_content.splitlines() 
                        if line.strip() and not line.strip().startswith('#')]
                analysis["keys"] = [line.split('=')[0] for line in lines if '=' in line]
                analysis["values_sample"] = dict(line.split('=', 1) for line in lines[:5] if '=' in line)
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"Configuration analysis failed: {e}")
            return {"format": config_type, "size": len(config_content), "error": str(e)}
    
    def _analyze_json_structure(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
        """Analyze JSON structure recursively"""
        structure = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                structure[full_key] = "object"
                structure.update(self._analyze_json_structure(value, full_key))
            elif isinstance(value, list):
                structure[full_key] = f"array[{len(value)}]"
            else:
                structure[full_key] = type(value).__name__
        return structure
    
    def _extract_json_keys(self, data: Dict[str, Any], prefix: str = "") -> List[str]:
        """Extract all JSON keys recursively"""
        keys = [
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, dict):
                keys.extend(self._extract_json_keys(value, full_key))
        return keys
    
    def _sample_json_values(self, data: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Sample JSON values for analysis"""
        sample = {}
        count = 0
        for key, value in data.items():
            if count >= limit:
                break
            if not isinstance(value, (dict, list)):
                sample[key] = value
                count += 1
        return sample
    
    def _analyze_yaml_structure(self, data: Any, prefix: str = "") -> Dict[str, str]:
        """Analyze YAML structure recursively"""
        if isinstance(data, dict):
            return self._analyze_json_structure(data, prefix)
        elif isinstance(data, list):
            return {prefix: f"array[{len(data)}]"}
        else:
            return {prefix: type(data).__name__}
    
    def _extract_yaml_keys(self, data: Any, prefix: str = "") -> List[str]:
        """Extract all YAML keys recursively"""
        if isinstance(data, dict):
            return self._extract_json_keys(data, prefix)
        else:
            return [prefix] if prefix else []
    
    def _sample_yaml_values(self, data: Any, limit: int) -> Dict[str, Any]:
        """Sample YAML values for analysis"""
        if isinstance(data, dict):
            return self._sample_json_values(data, limit)
        else:
            return {"root": data}
    
    def _analyze_toml_structure(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
        """Analyze TOML structure recursively"""
        return self._analyze_json_structure(data, prefix)
    
    def _extract_toml_keys(self, data: Dict[str, Any], prefix: str = "") -> List[str]:
        """Extract all TOML keys recursively"""
        return self._extract_json_keys(data, prefix)
    
    def _sample_toml_values(self, data: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Sample TOML values for analysis"""
        return self._sample_json_values(data, limit)
    
    def _extract_ini_keys(self, config: configparser.ConfigParser) -> List[str]:
        """Extract all INI keys"""
        keys = [
        for section_name in config.sections():
            for key in config[section_name]:
                keys.append(f"{section_name}.{key}")
        return keys
    
    def _sample_ini_values(self, config: configparser.ConfigParser, limit: int) -> Dict[str, str]:
        """Sample INI values for analysis"""
        sample = {}
        count = 0
        for section_name in config.sections():
            for key, value in config[section_name].items():
                if count >= limit:
                    break
                sample[f"{section_name}.{key}"] = value
                count += 1
        return sample
    
    def generate_configuration_context(self, metadata: ConfigurationMetadata,
                                     original_content: str) -> Dict[str, Any]:
        """Generate context for configuration recovery"""
        analysis = self.analyze_configuration_content(original_content, metadata.config_type)
        
        # Base context
        context = {
            'config_id': metadata.config_id,
            'config_category': metadata.config_category,
            'config_type': metadata.config_type,
            'original_path': metadata.file_path,
            'is_critical': metadata.is_critical,
            'recovery_priority': metadata.recovery_priority,
            'generation_timestamp': datetime.now().isoformat(),
            'config_version': '1.0.0',
            'environment': 'production'
        }
        
        # Category-specific context
        if metadata.config_category == 'application_config':
            context.update({
                'app_name': self._extract_app_name(analysis),
                'app_version': '1.0.0',
                'debug_mode': False,
                'log_level': 'INFO',
                'database_url': 'sqlite:///production.db',
                'db_pool_size': 10,
                'db_timeout': 30,
                'db_retry_attempts': 3,
                'secret_key': 'generated-secret-key',
                'jwt_expiry': 3600,
                'encryption_enabled': True,
                'rate_limiting_enabled': True,
                'rate_limit_rpm': 100,
                'caching_enabled': True,
                'monitoring_enabled': True,
                'backup_enabled': True
            })
            
        elif metadata.config_category == 'deployment_config':
            context.update({
                'service_name': self._extract_service_name(analysis),
                'docker_image': 'app:latest',
                'host_port': 8000,
                'container_port': 8000,
                'database_url': 'sqlite:///production.db',
                'secret_key': 'generated-secret-key',
                'log_level': 'INFO',
                'volume_mapping': './data:/app/data',
                'restart_policy': 'unless-stopped',
                'health_check_interval': '30s',
                'health_check_timeout': '10s',
                'health_check_retries': 3,
                'network_name': 'app_network',
                'network_driver': 'bridge',
                'volume_name': 'app_data',
                'volume_driver': 'local'
            })
            
        elif metadata.config_category == 'dependencies':
            context.update({
                'core_packages': self._extract_core_packages(analysis),
                'dev_packages': self._extract_dev_packages(analysis),
                'optional_packages': self._extract_optional_packages(analysis)
            })
            
        elif metadata.config_category == 'environment':
            context.update({
                'app_name': 'HAT_COPILOT',
                'app_version': '2.0.0',
                'debug_mode': False,
                'log_level': 'INFO',
                'database_url': 'sqlite:///production.db',
                'db_pool_size': 10,
                'db_timeout': 30,
                'secret_key': 'generated-secret-key',
                'jwt_secret': 'generated-jwt-secret',
                'encryption_key': 'generated-encryption-key',
                'services': {
                    'redis': {'host': 'localhost', 'port': 6379, 'enabled': True},
                    'postgres': {'host': 'localhost', 'port': 5432, 'enabled': False}
                },
                'features': {
                    'caching': True,
                    'monitoring': True,
                    'backup': True,
                    'analytics': True
                }
            })
            
        elif metadata.config_category == 'general_config':
            context.update({
                'app_name': 'HAT_COPILOT',
                'app_version': '2.0.0',
                'database_url': 'sqlite:///production.db',
                'db_pool_size': 10,
                'db_timeout': 30,
                'db_retry_attempts': 3,
                'log_level': 'INFO',
                'log_file_path': 'logs/application.log',
                'log_max_size': '10MB',
                'log_backup_count': 5,
                'secret_key': 'generated-secret-key',
                'jwt_expiry': 3600,
                'encryption_enabled': True,
                'custom_sections': self._extract_custom_sections(analysis)
            })
        
        return context
    
    def _extract_app_name(self, analysis: Dict[str, Any]) -> str:
        """Extract application name from analysis"""
        keys = analysis.get('keys', [])
        for key in keys:
            if 'app' in key.lower() and 'name' in key.lower():
                return analysis.get('values_sample', {}).get(key, 'HAT_COPILOT')
        return 'HAT_COPILOT'
    
    def _extract_service_name(self, analysis: Dict[str, Any]) -> str:
        """Extract service name from analysis"""
        keys = analysis.get('keys', [])
        for key in keys:
            if 'service' in key.lower():
                return analysis.get('values_sample', {}).get(key, 'app')
        return 'app'
    
    def _extract_core_packages(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract core packages from dependencies analysis"""
        return [
            {'name': 'flask', 'version': '2.3.0', 'extras': 'web framework'},
            {'name': 'sqlite3', 'version': 'latest', 'extras': 'database'},
            {'name': 'pathlib', 'version': 'latest', 'extras': 'file handling'},
            {'name': 'json', 'version': 'latest', 'extras': 'data serialization'}
        ]
    
    def _extract_dev_packages(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract development packages from analysis"""
        return [
            {'name': 'pytest', 'version': '7.0.0', 'extras': 'testing framework'},
            {'name': 'black', 'version': '23.0.0', 'extras': 'code formatting'},
            {'name': 'flake8', 'version': '6.0.0', 'extras': 'linting'}
        ]
    
    def _extract_optional_packages(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract optional packages from analysis"""
        return [
            {'name': 'redis', 'version': '4.5.0', 'description': 'caching and session storage'},
            {'name': 'psycopg2', 'version': '2.9.0', 'description': 'PostgreSQL adapter'}
        ]
    
    def _extract_custom_sections(self, analysis: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Extract custom sections from analysis"""
        return {
            'custom': {
                'setting1': 'value1',
                'setting2': 'value2'
            }
        }
    
    def create_backup(self, config_path: str) -> bool:
        """Create backup of existing configuration file"""
        try:
            source_path = Path(config_path)
            if not source_path.exists():
                return True  # No backup needed if file doesn't exist
            
            backup_name = f"{source_path.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_directory / backup_name
            
            shutil.copy2(source_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup creation failed for {config_path}: {e}")
            return False
    
    def recover_configuration(self, metadata: ConfigurationMetadata,
                            original_content: str) -> RecoveryResult:
        """Recover individual configuration file"""
        start_time = datetime.now()
        
        try:
            # Generate context for template
            context = self.generate_configuration_context(metadata, original_content)
            
            # Select appropriate template
            template_mapping = {
                'application_config': 'application_config.json.j2',
                'deployment_config': 'deployment_config.yaml.j2',
                'dependencies': 'requirements.txt.j2',
                'environment': 'environment.env.j2',
                'general_config': 'general_config.ini.j2'
            }
            
            template_name = template_mapping.get(
                metadata.config_category,
                'general_config.ini.j2'  # Fallback template
            )
            
            # Load and render template
            template = self.jinja_env.get_template(template_name)
            recovered_content = template.render(**context)
            
            # Create output path
            output_path = self.output_directory / metadata.file_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup of existing file
            backup_created = self.create_backup(str(output_path))
            
            # Write recovered configuration
            with open(output_path, 'w') as f:
                f.write(recovered_content)
            
            # Validate recovered configuration
            validation_passed = self._validate_recovered_config(
                output_path, recovered_content, metadata.config_type
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = RecoveryResult(
                success=True,
                config_path=str(output_path),
                config_type=metadata.config_type,
                restored_content=recovered_content,
                validation_passed=validation_passed,
                error_message=None,
                execution_time=execution_time,
                file_size=len(recovered_content.encode('utf-8')),
                backup_created=backup_created
            )
            
            self.logger.info(f"Successfully recovered: {metadata.file_path}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = RecoveryResult(
                success=False,
                config_path=metadata.file_path,
                config_type=metadata.config_type,
                restored_content="",
                validation_passed=False,
                error_message=str(e),
                execution_time=execution_time,
                file_size=0,
                backup_created=False
            )
            
            self.logger.error(f"Failed to recover {metadata.file_path}: {e}")
            return result
    
    def _validate_recovered_config(self, config_path: Path, content: str,
                                 config_type: str) -> bool:
        """Validate recovered configuration for format and syntax"""
        try:
            if config_type == 'json':
                json.loads(content)
            elif config_type in ['yaml', 'yml']:
                yaml.safe_load(content)
            elif config_type == 'ini':
                config = configparser.ConfigParser()
                config.read_string(content)
            elif config_type == 'toml':
                toml.loads(content)
            elif config_type == 'env':
                # Basic validation for environment files
                lines = [line.strip() for line in content.splitlines()]
                for line in lines:
                    if line and not line.startswith('#') and '=' not in line:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Validation failed for {config_path}: {e}")
            return False
    
    def recover_all_configurations(self, priority_filter: Optional[int] = None,
                                 category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Recover all configurations with optional filtering"""
        print(f"{self.indicators['recovery']} CONFIGURATION RECOVERY ENGINE")
        print("=" * 60)
        
        self.recovery_stats["start_time"] = datetime.now()
        
        # Load configuration metadata
        configurations = self.load_configuration_metadata()
        
        # Apply filters
        if priority_filter is not None:
            configurations = [c for c in configurations if c.recovery_priority <= priority_filter]
        
        if category_filter:
            configurations = [c for c in configurations if c.config_category == category_filter]
        
        print(f"{self.indicators['info']} Configurations to recover: {len(configurations)}")
        
        if not configurations:
            print(f"{self.indicators['warning']} No configurations found matching criteria")
            return self.recovery_stats
        
        # Load original content for configurations
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        recovery_results = [
        
        for i, config_metadata in enumerate(configurations, 1):
            print(f"{self.indicators['processing']} [{i}/{len(configurations)}] Recovering: {config_metadata.file_path}")
            
            # Get original content
            cursor.execute(
                "SELECT config_value FROM system_configurations WHERE config_id = ?",
                (config_metadata.config_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                self.logger.warning(f"No content found for config: {config_metadata.file_path}")
                continue
            
            original_content = result[0]
            
            # Recover configuration
            recovery_result = self.recover_configuration(config_metadata, original_content)
            recovery_results.append(recovery_result)
            
            # Update statistics
            self.recovery_stats["total_configurations"] += 1
            
            if recovery_result.success:
                self.recovery_stats["successful_recoveries"] += 1
                print(f"  {self.indicators['success']} Recovered successfully")
                
                if recovery_result.backup_created:
                    self.recovery_stats["backups_created"] += 1
                    print(f"  {self.indicators['backup']} Backup created")
                
                if recovery_result.validation_passed:
                    self.recovery_stats["validation_passes"] += 1
                    print(f"  {self.indicators['validation']} Validation: PASSED")
                else:
                    self.recovery_stats["validation_failures"] += 1
                    print(f"  {self.indicators['warning']} Validation: FAILED")
            else:
                self.recovery_stats["failed_recoveries"] += 1
                print(f"  {self.indicators['error']} Recovery failed: {recovery_result.error_message}")
        
        conn.close()
        
        self.recovery_stats["end_time"] = datetime.now()
        duration = self.recovery_stats["end_time"] - self.recovery_stats["start_time"]
        
        # Generate summary report
        summary = self._generate_recovery_summary(recovery_results, duration)
        
        print(f"\n{self.indicators['success']} CONFIGURATION RECOVERY COMPLETE")
        print("=" * 60)
        print(f"Total Configurations: {self.recovery_stats['total_configurations']}")
        print(f"Successful: {self.recovery_stats['successful_recoveries']}")
        print(f"Failed: {self.recovery_stats['failed_recoveries']}")
        print(f"Validation Passes: {self.recovery_stats['validation_passes']}")
        print(f"Backups Created: {self.recovery_stats['backups_created']}")
        print(f"Duration: {duration}")
        
        return summary
    
    def _generate_recovery_summary(self, results: List[RecoveryResult],
                                 duration) -> Dict[str, Any]:
        """Generate comprehensive recovery summary"""
        summary = {
            "recovery_metadata": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration.total_seconds(),
                "engine_version": "2.0.0"
            },
            "statistics": self.recovery_stats.copy(),
            "performance_metrics": {
                "average_recovery_time": sum(r.execution_time for r in results) / len(results) if results else 0,
                "total_files_recovered": len([r for r in results if r.success]),
                "total_file_size": sum(r.file_size for r in results if r.success),
                "success_rate": (self.recovery_stats["successful_recoveries"] / 
                               self.recovery_stats["total_configurations"] * 100) if self.recovery_stats["total_configurations"] > 0 else 0,
                "validation_rate": (self.recovery_stats["validation_passes"] / 
                                  self.recovery_stats["successful_recoveries"] * 100) if self.recovery_stats["successful_recoveries"] > 0 else 0,
                "backup_rate": (self.recovery_stats["backups_created"] / 
                              self.recovery_stats["total_configurations"] * 100) if self.recovery_stats["total_configurations"] > 0 else 0
            },
            "detailed_results": [
                {
                    "config_path": r.config_path,
                    "config_type": r.config_type,
                    "success": r.success,
                    "validation_passed": r.validation_passed,
                    "backup_created": r.backup_created,
                    "execution_time": r.execution_time,
                    "file_size": r.file_size,
                    "error_message": r.error_message
                }
                for r in results
            ]
        }
        
        # Save summary report
        report_filename = f'configuration_recovery_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Recovery summary saved: {report_filename}")
        print(f"{self.indicators['info']} Summary report: {report_filename}")
        
        return summary
    
    def validate_recovery_capability(self) -> Dict[str, Any]:
        """Validate the configuration recovery engine's capabilities"""
        print(f"{self.indicators['validation']} VALIDATING RECOVERY CAPABILITY")
        print("-" * 50)
        
        validation_results = {
            "database_connectivity": False,
            "template_availability": False,
            "output_directory": False,
            "backup_directory": False,
            "config_metadata_count": 0,
            "template_count": 0,
            "capability_score": 0
        }
        
        try:
            # Test database connectivity
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM system_configurations")
            config_count = cursor.fetchone()[0]
            conn.close()
            
            validation_results["database_connectivity"] = True
            validation_results["config_metadata_count"] = config_count
            print(f"{self.indicators['success']} Database connectivity: OK ({config_count} configurations)")
            
        except Exception as e:
            print(f"{self.indicators['error']} Database connectivity: FAILED - {e}")
        
        try:
            # Check template availability
            template_files = list(self.template_directory.glob("*.j2"))
            validation_results["template_count"] = len(template_files)
            validation_results["template_availability"] = len(template_files) >= 3
            
            if validation_results["template_availability"]:
                print(f"{self.indicators['success']} Template availability: OK ({len(template_files)} templates)")
            else:
                print(f"{self.indicators['warning']} Template availability: LIMITED ({len(template_files)} templates)")
            
        except Exception as e:
            print(f"{self.indicators['error']} Template check: FAILED - {e}")
        
        try:
            # Check output directory
            validation_results["output_directory"] = self.output_directory.exists() and os.access(self.output_directory, os.W_OK)
            if validation_results["output_directory"]:
                print(f"{self.indicators['success']} Output directory: OK")
            else:
                print(f"{self.indicators['error']} Output directory: NOT ACCESSIBLE")
                
        except Exception as e:
            print(f"{self.indicators['error']} Output directory check: FAILED - {e}")
        
        try:
            # Check backup directory
            validation_results["backup_directory"] = self.backup_directory.exists() and os.access(self.backup_directory, os.W_OK)
            if validation_results["backup_directory"]:
                print(f"{self.indicators['success']} Backup directory: OK")
            else:
                print(f"{self.indicators['error']} Backup directory: NOT ACCESSIBLE")
                
        except Exception as e:
            print(f"{self.indicators['error']} Backup directory check: FAILED - {e}")
        
        # Calculate capability score
        score = 0
        if validation_results["database_connectivity"]:
            score += 30
        if validation_results["template_availability"]:
            score += 25
        if validation_results["output_directory"]:
            score += 20
        if validation_results["backup_directory"]:
            score += 15
        if validation_results["config_metadata_count"] > 10:
            score += 10
        
        validation_results["capability_score"] = score
        
        status = "EXCELLENT" if score >= 90 else "GOOD" if score >= 70 else "ACCEPTABLE" if score >= 50 else "POOR"
        print(f"\n{self.indicators['validation']} Recovery Capability: {score}% ({status})")
        
        return validation_results

def main():
    """Main execution function"""
    try:
        engine = ConfigurationRecoveryEngine()
        
        # Validate recovery capability
        validation = engine.validate_recovery_capability()
        
        if validation["capability_score"] < 50:
            print(f"\n{engine.indicators['error']} Recovery capability insufficient")
            return False
        
        # Allow command line arguments for filtering
        priority_filter = None
        category_filter = None
        
        if len(sys.argv) > 1:
            if sys.argv[1].isdigit():
                priority_filter = int(sys.argv[1])
            else:
                category_filter = sys.argv[1]
        
        # Run configuration recovery
        summary = engine.recover_all_configurations(
            priority_filter=priority_filter,
            category_filter=category_filter
        )
        
        success_rate = summary["performance_metrics"]["success_rate"]
        return success_rate >= 80
        
    except Exception as e:
        print(f"Configuration recovery engine failed: {e}")
        logging.error(f"Critical error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)