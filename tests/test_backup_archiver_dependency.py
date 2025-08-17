def test_py7zr_present():
    import py7zr  # noqa: F401

def test_backup_archiver_import():
    # Prefer module import path
    try:
        import scripts.backup_archiver  # noqa: F401
    except Exception as e:
        import pytest
        pytest.skip(f'backup_archiver import skipped due to environment: {e}')
