"""
Tests for the validation package.
"""

import tempfile
import json
import sqlite3
from pathlib import Path

from validation.core.validators import BaseValidator, ValidationResult, ValidationStatus, CompositeValidator
from validation.core.rules import (
    FileExistsRule, NoZeroByteFilesRule,
    DatabaseIntegrityRule, JsonValidRule, ThresholdRule, RuleBasedValidator
)
from validation.protocols.session import SessionProtocolValidator
from validation.protocols.deployment import DeploymentValidator
from validation.reporting.formatters import ValidationReportFormatter


class MockValidator(BaseValidator):
    """Mock validator for testing"""
    
    def __init__(self, name: str, should_pass: bool = True):
        super().__init__(name)
        self.should_pass = should_pass
    
    def validate(self, target) -> ValidationResult:
        if self.should_pass:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message=f"{self.name} passed"
            )
        else:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"{self.name} failed",
                errors=["Mock validation error"]
            )


class TestValidationCore:
    """Test core validation functionality"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation"""
        result = ValidationResult(
            status=ValidationStatus.PASSED,
            message="Test passed"
        )
        
        assert result.status == ValidationStatus.PASSED
        assert result.message == "Test passed"
        assert result.is_success is True
        assert result.is_failure is False
    
    def test_validation_result_failure(self):
        """Test ValidationResult for failure"""
        result = ValidationResult(
            status=ValidationStatus.FAILED,
            message="Test failed",
            errors=["Error 1", "Error 2"]
        )
        
        assert result.status == ValidationStatus.FAILED
        assert result.is_success is False
        assert result.is_failure is True
        assert len(result.errors) == 2
    
    def test_base_validator_run(self):
        """Test base validator run_validation"""
        validator = MockValidator("test", should_pass=True)
        result = validator.run_validation("dummy_target")
        
        assert result.is_success
        assert "test passed" in result.message
    
    def test_base_validator_error_handling(self):
        """Test base validator error handling"""
        class ErrorValidator(BaseValidator):
            def validate(self, target):
                raise Exception("Test error")
        
        validator = ErrorValidator("error_test")
        result = validator.run_validation("dummy")
        
        assert result.status == ValidationStatus.ERROR
        assert "Test error" in result.message
    
    def test_composite_validator(self):
        """Test composite validator"""
        validators = [
            MockValidator("validator1", True),
            MockValidator("validator2", True),
            MockValidator("validator3", False)
        ]
        
        composite = CompositeValidator("composite_test", validators)
        result = composite.run_validation("dummy")
        
        assert result.status == ValidationStatus.FAILED
        assert "1/3" in result.message  # 1 failed out of 3


class TestValidationRules:
    """Test validation rules"""
    
    def test_file_exists_rule(self):
        """Test FileExistsRule"""
        with tempfile.NamedTemporaryFile() as temp_file:
            rule = FileExistsRule(temp_file.name)
            assert rule.check(None) is True
        
        # Test non-existent file
        rule = FileExistsRule("/nonexistent/file.txt")
        assert rule.check(None) is False
    
    def test_no_zero_byte_files_rule(self):
        """Test NoZeroByteFilesRule"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create normal file
            (temp_path / "normal.txt").write_text("content")
            
            rule = NoZeroByteFilesRule(temp_path)
            assert rule.check(None) is True
            
            # Create zero-byte file
            (temp_path / "empty.txt").touch()
            
            rule = NoZeroByteFilesRule(temp_path)
            assert rule.check(None) is False
            assert len(rule.zero_byte_files) == 1
    
    def test_database_integrity_rule(self):
        """Test DatabaseIntegrityRule"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = Path(temp_db.name)
        
        # Create valid database
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.commit()
        
        rule = DatabaseIntegrityRule(db_path)
        assert rule.check(None) is True
        assert rule.integrity_result == 'ok'
        
        # Clean up
        db_path.unlink()
    
    def test_json_valid_rule(self):
        """Test JsonValidRule"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_json:
            json.dump({"test": "data"}, temp_json)
            json_path = Path(temp_json.name)
        
        rule = JsonValidRule(json_path)
        assert rule.check(None) is True
        
        # Test invalid JSON
        with open(json_path, 'w') as f:
            f.write("invalid json {")
        
        rule = JsonValidRule(json_path)
        assert rule.check(None) is False
        assert rule.error_message is not None
        
        # Clean up
        json_path.unlink()
    
    def test_threshold_rule(self):
        """Test ThresholdRule"""
        rule = ThresholdRule("test_threshold", 50.0, ">=")
        
        assert rule.check(75.0) is True
        assert rule.check(25.0) is False
        assert rule.check({"value": 60.0}) is True
        assert rule.check({"value": 30.0}) is False
    
    def test_rule_based_validator(self):
        """Test RuleBasedValidator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("content")
            
            rules = [
                FileExistsRule(str(test_file)),
                NoZeroByteFilesRule(temp_path)
            ]
            
            validator = RuleBasedValidator("rule_test", rules)
            result = validator.run_validation(temp_path)
            
            assert result.is_success
            assert result.details['passed_count'] == 2
            assert result.details['failed_count'] == 0


class TestSessionProtocolValidator:
    """Test session protocol validator"""
    
    def test_session_validator_initialization(self):
        """Test session validator initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = SessionProtocolValidator(temp_dir)
            assert validator.workspace_path == Path(temp_dir)
    
    def test_validate_startup_success(self):
        """Test successful startup validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create normal files
            (temp_path / "test1.txt").write_text("content1")
            (temp_path / "test2.py").write_text("print('hello')")
            
            validator = SessionProtocolValidator(temp_dir)
            result = validator.validate_startup()
            
            assert result.is_success
    
    def test_validate_startup_failure(self):
        """Test startup validation with zero-byte files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create zero-byte file
            (temp_path / "empty.txt").touch()
            
            validator = SessionProtocolValidator(temp_dir)
            result = validator.validate_startup()
            
            assert result.is_failure
            assert "rule validation failed" in result.message.lower()
            assert "zero-byte" in str(result.errors[0]).lower()
    
    def test_validate_session_cleanup(self):
        """Test session cleanup validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            validator = SessionProtocolValidator(temp_dir)
            
            # Test clean workspace
            result = validator.validate_session_cleanup()
            assert result.is_success
            
            # Add some temporary files
            (temp_path / "temp.tmp").touch()
            (temp_path / "lock.lock").touch()
            
            result = validator.validate_session_cleanup()
            assert result.status == ValidationStatus.WARNING
            assert len(result.warnings) > 0
    
    def test_validate_session_permissions(self):
        """Test session permission validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = SessionProtocolValidator(temp_dir)
            result = validator.validate_session_permissions()
            
            # Should pass for temporary directory
            assert result.is_success
            assert result.details['write_permission'] is True
            assert result.details['read_permission'] is True

    def test_validate_credential_sanitization(self, monkeypatch):
        monkeypatch.setenv("MY_PASSWORD", "secret")
        validator = SessionProtocolValidator()
        result = validator.validate_credential_sanitization()
        assert result.is_failure

    def test_validate_session_timeout(self, monkeypatch):
        monkeypatch.setenv("SESSION_TIMEOUT", "30")
        validator = SessionProtocolValidator()
        result = validator.validate_session_timeout()
        assert result.is_failure

    def test_validate_secure_connection(self, monkeypatch):
        monkeypatch.setenv("USE_HTTPS", "0")
        validator = SessionProtocolValidator()
        result = validator.validate_secure_connection()
        assert result.is_failure


class TestDeploymentValidator:
    """Test deployment validator"""
    
    def test_deployment_validator_initialization(self):
        """Test deployment validator initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = DeploymentValidator(temp_dir)
            assert validator.workspace_path == Path(temp_dir)
    
    def test_validate_enterprise_certificate_missing(self):
        """Test enterprise certificate validation when missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = DeploymentValidator(temp_dir)
            result = validator._validate_enterprise_certificate()
            
            assert result.is_failure
            assert "missing" in result.message.lower()
    
    def test_validate_enterprise_certificate_valid(self):
        """Test enterprise certificate validation when valid"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create valid certificate
            certificate_data = {
                "ENTERPRISE_READINESS": {
                    "overall_readiness_percentage": 100.0
                }
            }
            
            cert_file = temp_path / "ENTERPRISE_READINESS_100_PERCENT_CERTIFICATE.json"
            with open(cert_file, 'w') as f:
                json.dump(certificate_data, f)
            
            validator = DeploymentValidator(temp_dir)
            result = validator._validate_enterprise_certificate()
            
            assert result.is_success
            assert "100.0%" in result.message
    
    def test_validate_database_architecture_missing(self):
        """Test database architecture validation when missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = DeploymentValidator(temp_dir)
            result = validator._validate_database_architecture()
            
            assert result.is_failure
            assert "missing" in result.message.lower()
    
    def test_validate_database_architecture_valid(self):
        """Test database architecture validation when valid"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create valid database
            db_path = temp_path / "production.db"
            with sqlite3.connect(db_path) as conn:
                conn.execute("CREATE TABLE test (id INTEGER)")
                conn.commit()
            
            validator = DeploymentValidator(temp_dir)
            result = validator._validate_database_architecture()
            
            assert result.is_success
            assert "database architecture healthy" in result.message.lower()
            assert result.details['integrity'] == 'ok'
    
    def test_validate_autonomous_systems(self):
        """Test autonomous systems validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some autonomous system files
            (temp_path / "autonomous_monitoring_system.py").touch()
            (temp_path / "execute_enterprise_audit.py").touch()
            # Missing optimize_to_100_percent.py
            
            validator = DeploymentValidator(temp_dir)
            result = validator._validate_autonomous_systems()
            
            assert result.status == ValidationStatus.WARNING
            assert len(result.details['missing_systems']) == 1
            assert len(result.details['present_systems']) == 2


class TestValidationReporting:
    """Test validation reporting"""
    
    def test_text_report_format(self):
        """Test text report formatting"""
        results = [
            ValidationResult(ValidationStatus.PASSED, "Test 1 passed"),
            ValidationResult(ValidationStatus.FAILED, "Test 2 failed", errors=["Error 1"]),
            ValidationResult(ValidationStatus.WARNING, "Test 3 warning", warnings=["Warning 1"])
        ]
        
        formatter = ValidationReportFormatter()
        report = formatter.format_text_report(results, "Test Report")
        
        assert "Test Report" in report
        assert "Passed: 1" in report
        assert "Failed: 1" in report
        assert "Warnings: 1" in report
    
    def test_json_report_format(self):
        """Test JSON report formatting"""
        results = [
            ValidationResult(ValidationStatus.PASSED, "Test passed")
        ]
        
        formatter = ValidationReportFormatter()
        report = formatter.format_json_report(results)
        
        # Verify it's valid JSON
        data = json.loads(report)
        assert data['title'] == "Validation Report"
        assert len(data['results']) == 1
        assert data['results'][0]['status'] == 'passed'
    
    def test_markdown_report_format(self):
        """Test Markdown report formatting"""
        results = [
            ValidationResult(ValidationStatus.PASSED, "Test passed")
        ]
        
        formatter = ValidationReportFormatter()
        report = formatter.format_markdown_report(results)
        
        assert "# Validation Report" in report
        assert "## Summary" in report
        assert "✅" in report  # Success emoji
    
    def test_save_report(self):
        """Test saving report to file"""
        results = [
            ValidationResult(ValidationStatus.PASSED, "Test passed")
        ]
        
        formatter = ValidationReportFormatter()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_report"
            
            success = formatter.save_report(results, output_path, "json")
            assert success is True
            
            json_file = output_path.with_suffix('.json')
            assert json_file.exists()
            
            # Verify content
            with open(json_file) as f:
                data = json.load(f)
            assert len(data['results']) == 1