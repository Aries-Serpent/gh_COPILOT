
def test_imports_smoke():
    import importlib
    for m in ["src.quantum.shim", "perf.samplers.basic"]:
        importlib.import_module(m)
