def test_dependencies_imports():
    missing = []
    try:
        import tqdm  # noqa: F401
    except Exception as e:
        missing.append(f"tqdm: {e}")
    try:
        import typer  # noqa: F401
    except Exception as e:
        missing.append(f"typer: {e}")
    assert not missing, f"Missing dependencies: {missing}"
