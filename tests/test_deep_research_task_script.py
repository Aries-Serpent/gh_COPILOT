from pathlib import Path


def test_script_contains_now_iso():
    script = Path('deep_research_task.py').read_text(encoding='utf-8')
    assert 'def now_iso' in script
