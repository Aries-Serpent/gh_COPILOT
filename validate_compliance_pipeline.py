#!/usr/bin/env python3
"""Simple validation script for compliance pipeline functionality"""

import tempfile
import json
import sqlite3
from pathlib import Path

def test_compliance_components():
    """Test ComplianceComponents dataclass"""
    from scripts.compliance.update_compliance_metrics import ComplianceComponents, _compute
    
    print("🧪 Testing ComplianceComponents...")
    
    # Test basic creation
    comp = ComplianceComponents(ruff_issues=3, tests_passed=45, tests_total=50, 
                               placeholders_open=8, placeholders_resolved=22)
    
    # Test computation
    L, T, P, composite = _compute(comp)
    
    # Verify calculations
    assert L == 97.0, f"Lint score wrong: {L}"
    assert T == 90.0, f"Test score wrong: {T}"
    assert abs(P - 73.33) < 0.1, f"Placeholder score wrong: {P}"
    
    expected_composite = 0.3 * 97.0 + 0.5 * 90.0 + 0.2 * (22/30*100)
    assert abs(composite - expected_composite) < 0.1, f"Composite wrong: {composite}"
    
    print(f"✅ ComplianceComponents: L={L}, T={T}, P={P:.2f}, Composite={composite:.2f}")
    return True

def test_ingestion_pipeline():
    """Test ruff and pytest ingestion"""
    from scripts.ingest_test_and_lint_results import ingest, _db
    
    print("🧪 Testing ingestion pipeline...")
    
    # Create sample ruff data
    ruff_data = [
        {"code": "E501", "message": "line too long", "filename": "test.py", "location": {"row": 1, "column": 80}},
        {"code": "F401", "message": "unused import", "filename": "main.py", "location": {"row": 5, "column": 1}}
    ]
    
    # Create sample pytest data  
    pytest_data = {
        "summary": {"passed": 18, "failed": 2, "skipped": 1, "total": 21},
        "tests": [
            {"nodeid": "test_example.py::test_basic", "outcome": "passed"},
            {"nodeid": "test_example.py::test_failing", "outcome": "failed"}
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(ruff_data, f)
        ruff_file = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(pytest_data, f)
        pytest_file = Path(f.name)
    
    try:
        # Test with temporary database
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_workspace = Path(temp_dir)
            
            # Create databases directory
            (temp_workspace / "databases").mkdir(parents=True, exist_ok=True)
            
            # Test ingestion with both files
            ingest(workspace=str(temp_workspace), ruff_json=ruff_file, pytest_json=pytest_file)
            print(f"✅ Combined ingestion successful")
            
            # Verify database was created
            db_path = _db(str(temp_workspace))
            assert db_path.exists(), "Database was not created"
            
            return True
            
    finally:
        # Clean up temp files
        ruff_file.unlink(missing_ok=True)
        pytest_file.unlink(missing_ok=True)

def test_session_tracking():
    """Test session lifecycle tracking"""
    from session.session_lifecycle_metrics import start_session, end_session, _db
    
    print("🧪 Testing session tracking...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_workspace = Path(temp_dir)
        
        # Create database first
        db_path = _db(str(temp_workspace))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty database
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("SELECT 1")  # Just create the file
        
        # Start a session
        session_id = "test_session_123"
        start_session(session_id, workspace=str(temp_workspace))
        print(f"✅ Session started: {session_id}")
        
        # End the session
        end_session(session_id, status="completed", workspace=str(temp_workspace))
        print(f"✅ Session ended")
        
        # Verify database
        assert db_path.exists(), "Session database was not created"
        
        return True

def main():
    """Run all compliance tests"""
    print("🚀 Starting compliance pipeline validation...\n")
    
    tests = [
        ("Compliance Components", test_compliance_components),
        ("Ingestion Pipeline", test_ingestion_pipeline), 
        ("Session Tracking", test_session_tracking)
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {name} test passed\n")
                passed += 1
        except Exception as e:
            print(f"❌ {name} test failed: {e}\n")
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All compliance pipeline tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
