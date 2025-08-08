#!/usr/bin/env python3
from datetime import datetime
from copilot.core.enterprise_json_serialization_fix import EnterpriseJSONSerializer
<<<<<<< HEAD
=======
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_round_trip_datetime(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    serializer = EnterpriseJSONSerializer()
<<<<<<< HEAD
    data = {"time": datetime(2021, 1, 1, 12, 0)}
    dumped = serializer.safe_json_dumps(data)
    loaded = serializer.safe_json_loads(dumped)
    assert isinstance(loaded["time"], datetime)
    assert loaded["time"] == data["time"]
=======
    data = {'time': datetime(2021, 1, 1, 12, 0)}
    dumped = serializer.safe_json_dumps(data)
    loaded = serializer.safe_json_loads(dumped)
    assert isinstance(loaded['time'], datetime)
    assert loaded['time'] == data['time']
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
