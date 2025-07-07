import os
import tempfile
import time
import sqlite3
import signal
import logging

import pytest

from final_enterprise_orchestrator import FinalEnterpriseOrchestrator


def create_dummy_service_script(path, sleep_time=5):
    with open(path, 'w') as f:
        f.write(f"import time\n" 
                f"time.sleep({sleep_time})\n")


def test_start_service_success_and_health(caplog):
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, 'service.py')
        create_dummy_service_script(script_path)

        orch = FinalEnterpriseOrchestrator(workspace_root=tmpdir)
        with caplog.at_level(logging.INFO):
            started = orch.start_service('DummyService', script_path, cwd=tmpdir)
        try:
            assert started is True
            assert 'DummyService' in orch.services
            healthy = orch.check_service_health('DummyService')
            assert healthy is True
            assert any('DummyService started successfully' in r.message for r in caplog.records)
        finally:
            proc = orch.services['DummyService']['process']
            proc.terminate()
            proc.wait()


def test_start_service_failure(caplog):
    with tempfile.TemporaryDirectory() as tmpdir:
        orch = FinalEnterpriseOrchestrator(workspace_root=tmpdir)
        with caplog.at_level(logging.INFO):
            started = orch.start_service('MissingService', os.path.join(tmpdir, 'nope.py'))
        assert started is False
        assert any('Failed to start MissingService' in r.message for r in caplog.records)


def test_count_healthy_databases():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_dir = os.path.join(tmpdir, 'databases')
        os.mkdir(db_dir)
        # create a valid db with content
        conn = sqlite3.connect(os.path.join(db_dir, 'a.db'))
        conn.execute('CREATE TABLE t(id INTEGER)')
        conn.commit()
        conn.close()
        # empty file should not count
        open(os.path.join(db_dir, 'empty.db'), 'w').close()

        orch = FinalEnterpriseOrchestrator(workspace_root=tmpdir)
        count = orch._count_healthy_databases()
        assert count == 1


def test_count_healthy_databases_missing_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        orch = FinalEnterpriseOrchestrator(workspace_root=tmpdir)
        count = orch._count_healthy_databases()
        assert count == 0
