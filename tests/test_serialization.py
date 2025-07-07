from datetime import datetime
from enterprise_json_serialization_fix import EnterpriseJSONSerializer


def test_round_trip_datetime():
    serializer = EnterpriseJSONSerializer(workspace_path='.')
    data = {'time': datetime(2021, 1, 1, 12, 0)}
    dumped = serializer.safe_json_dumps(data)
    loaded = serializer.safe_json_loads(dumped)
    assert isinstance(loaded['time'], datetime)
    assert loaded['time'] == data['time']
