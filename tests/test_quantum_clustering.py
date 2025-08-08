#!/usr/bin/env python3
# isort: off
import logging
import pytest

pytest.importorskip("qiskit_machine_learning")

<<<<<<< HEAD
from scripts.utilities.quantum_clustering_file_organization import EnterpriseUtility
=======
from quantum_clustering_file_organization import EnterpriseUtility
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
# isort: on

logging.getLogger().setLevel(logging.CRITICAL)


def test_perform_utility_function_clusters(tmp_path):
    for i in range(3):
        (tmp_path / f"file{i}.txt").write_text("data" * (i + 1))
    util = EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function(n_clusters=2) is True
