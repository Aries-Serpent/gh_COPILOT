from .collector import collect_and_detect
def _demo_source():
    return {"uptime": 12345, "cpu": 0.15}
def _demo_detector(metrics):
    m = metrics.get("demo", {})
    return {"detector": "demo", "flag": m.get("cpu", 0) > 0.9}
if __name__ == "__main__":
    result = collect_and_detect({"demo": _demo_source}, [_demo_detector])
    print(result)
