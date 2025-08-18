from pathlib import Path
import types, sys, json, importlib.util

spec = importlib.util.spec_from_file_location("fastapi", Path("src/fastapi/__init__.py"))
fastapi_stub = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(fastapi_stub)
sys.modules["fastapi"] = fastapi_stub

pydantic_stub = types.ModuleType("pydantic")

class _BaseModel:
    def __init__(self, **data):
        self.__dict__.update(data)

    def model_dump(self):
        return self.__dict__

    def model_dump_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def model_validate_json(cls, s):
        return cls(**json.loads(s))

def Field(default=None, **kwargs):
    return default

pydantic_stub.BaseModel = _BaseModel
pydantic_stub.Field = Field
sys.modules["pydantic"] = pydantic_stub

from src.gh_copilot.api import api_ingest


def test_api_ingest(monkeypatch, tmp_path):
    called = {}

    def fake_ingest(workspace: Path, har_dir: Path | None = None) -> None:  # pragma: no cover - stub
        called["workspace"] = workspace

    monkeypatch.setattr(
        "scripts.database.har_ingestor.ingest_har_entries", fake_ingest
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    resp = api_ingest("har")
    assert resp == {"ok": True}
    assert Path(called["workspace"]) == tmp_path
