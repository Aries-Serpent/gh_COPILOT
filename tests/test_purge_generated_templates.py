from unified_legacy_cleanup_system import UnifiedLegacyCleanupSystem


def test_purge_generated_templates(tmp_path):
    generated = tmp_path / "generated_templates"
    generated.mkdir()
    old = generated / "template_old.txt"
    new = generated / "template_new.txt"
    old.write_text("old")
    new.write_text("new")
    cleanup = UnifiedLegacyCleanupSystem(workspace_path=tmp_path)
    removed = cleanup.purge_generated_templates(generated, keep=1)
    assert removed == 1
    assert new.exists()
    assert not old.exists()
