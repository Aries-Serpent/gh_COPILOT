"""Tests for template clustering and cleanup."""

from pathlib import Path

from unified_script_generation_system import EnterpriseUtility


def test_cluster_templates_removes_duplicates(tmp_path: Path) -> None:
    """Duplicates in a cluster are removed by cleanup routine."""

    t1 = tmp_path / "template1.txt"
    t2 = tmp_path / "template2.txt"
    content = "Hello {name}\n"
    t1.write_text(content)
    t2.write_text(content)

    utility = EnterpriseUtility(workspace_path=str(tmp_path))
    clusters = utility.cluster_templates([t1, t2], n_clusters=1)

    assert 0 in clusters
    assert len(clusters[0]) == 1
    assert not t2.exists()

