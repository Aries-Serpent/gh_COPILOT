from typing import Any, Dict, Iterable, Callable

def collect_metrics(sources: Dict[str, Callable[[], Dict[str, Any]]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name, fn in sources.items():
        try:
            out[name] = fn()
        except Exception as e:
            out[name] = {"error": str(e)}
    return out

def detect_anomalies(metrics: Dict[str, Any], detectors: Iterable[Callable[[Dict[str, Any]], Dict[str, Any]]]):
    results = []
    for det in detectors:
        try:
            results.append(det(metrics))
        except Exception as e:
            results.append({"detector": getattr(det, '__name__', 'unknown'), "error": str(e)})
    return results

def collect_and_detect(sources: Dict[str, Callable[[], Dict[str, Any]]],
                       detectors: Iterable[Callable[[Dict[str, Any]], Dict[str, Any]]]):
    metrics = collect_metrics(sources)
    anomalies = detect_anomalies(metrics, detectors)
    return {"metrics": metrics, "anomalies": anomalies}
