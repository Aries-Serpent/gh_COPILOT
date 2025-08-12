from pathlib import Path
import sys
from importlib import util
from types import ModuleType, SimpleNamespace

# Stub minimal sklearn dependency to avoid heavy install
sklearn = ModuleType("sklearn")
feature_extraction = ModuleType("sklearn.feature_extraction")
text = ModuleType("sklearn.feature_extraction.text")


class DummyVectorizer:
    def __init__(self, *args, **kwargs):
        pass

    def fit_transform(self, texts):
        return SimpleNamespace(toarray=lambda: [[0.0]])

    def get_feature_names_out(self):
        return ["dummy"]


text.TfidfVectorizer = DummyVectorizer
feature_extraction.text = text
sklearn.feature_extraction = feature_extraction
sys.modules["sklearn"] = sklearn
sys.modules["sklearn.feature_extraction"] = feature_extraction
sys.modules["sklearn.feature_extraction.text"] = text

quantum_pkg = ModuleType("quantum")
quantum_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "quantum")]
sys.modules["quantum"] = quantum_pkg

utils_pkg = ModuleType("quantum.utils")
backend_provider = ModuleType("quantum.utils.backend_provider")


def get_backend(*args, **kwargs):
    return None


backend_provider.get_backend = get_backend
utils_pkg.backend_provider = backend_provider
sys.modules["quantum.utils"] = utils_pkg
sys.modules["quantum.utils.backend_provider"] = backend_provider

spec = util.spec_from_file_location(
    "quantum.quantum_compliance_engine",
    Path(__file__).resolve().parents[1] / "quantum" / "quantum_compliance_engine.py",
)
qce = util.module_from_spec(spec)
sys.modules[spec.name] = qce
spec.loader.exec_module(qce)


def test_secondary_validator_invoked(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "sample.txt"
    target.write_text("quantum compliance")

    called = {"files": None}

    def dummy_validate(self, files):
        called["files"] = files
        return True

    monkeypatch.setattr(
        qce.SecondaryCopilotValidator,
        "validate_corrections",
        dummy_validate,
    )

    monkeypatch.setattr(qce, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(qce, "validate_environment_root", lambda: None)

    engine = qce.QuantumComplianceEngine(tmp_path)
    engine.score(target, ["quantum"])

    assert called["files"] == [str(target)]
