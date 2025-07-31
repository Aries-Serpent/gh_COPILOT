#!/usr/bin/env python3
import logging
import os

from scripts.utilities.quantum_clustering_file_organization import EnterpriseUtility


def test_quantum_clustering(tmp_path, caplog):
    # Small files
    small1 = tmp_path / "small1.txt"
    small1.write_text("a")
    os.utime(small1, (1, 1))

    small2 = tmp_path / "small2.txt"
    small2.write_text("b")
    os.utime(small2, (1, 1))

    # Large files
    large1 = tmp_path / "large1.txt"
    large1.write_text("x" * 1000)
    os.utime(large1, (100, 100))

    large2 = tmp_path / "large2.txt"
    large2.write_text("y" * 1000)
    os.utime(large2, (100, 100))

    util = EnterpriseUtility(tmp_path)
    with caplog.at_level(logging.INFO):
        assert util.perform_utility_function(n_clusters=2) is True

    labels = {}
    for record in caplog.records:
        msg = record.getMessage()
        if msg.startswith("[INFO]") and "cluster" in msg:
            name, label = msg.split()[1], msg.split()[-1]
            labels[name.rstrip(":")] = int(label)

    assert len(labels) == 4
    assert len(set(labels.values())) == 2
