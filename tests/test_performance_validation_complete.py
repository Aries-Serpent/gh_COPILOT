from performance_validation_complete import benchmark


def test_benchmark_runs():
    results = benchmark()
    assert set(results.keys()) >= {"grover_time", "kmeans_time",
                                   "qnn_time", "template_time", "flake8_time"}
    for value in results.values():
        assert value >= 0
