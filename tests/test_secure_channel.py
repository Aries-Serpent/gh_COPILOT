import sys
from importlib import util
from pathlib import Path
from types import ModuleType

quantum_pkg = ModuleType("quantum")
quantum_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "quantum")]
sys.modules["quantum"] = quantum_pkg

algorithms_pkg = ModuleType("ghc_quantum.algorithms")


class DummyQEC:
    def __init__(self, key=None):
        self.key = key or "k"

    def encrypt_message(self, payload: str) -> str:
        return payload[::-1]

    def decrypt_message(self, encrypted: str) -> str:
        return encrypted[::-1]


algorithms_pkg.QuantumEncryptedCommunication = DummyQEC
sys.modules["ghc_quantum.algorithms"] = algorithms_pkg

spec = util.spec_from_file_location(
    "ghc_quantum.integration.secure_channel",
    Path(__file__).resolve().parents[1] / "quantum" / "integration" / "secure_channel.py",
)
qs = util.module_from_spec(spec)
sys.modules[spec.name] = qs
spec.loader.exec_module(qs)


def test_transmit_uses_secondary_validator(monkeypatch) -> None:
    called = {"files": None}

    def dummy_validate(self, files):
        called["files"] = files
        return True

    monkeypatch.setattr(
        qs.SecondaryCopilotValidator,
        "validate_corrections",
        dummy_validate,
    )

    channel = qs.QuantumSecureChannel()
    result = channel.transmit("hello")

    assert result == "hello"
    assert called["files"] == ["hello"]
