import tempfile
from pathlib import Path

import pytest

from web_gui.certificates import certificate_manager as cm
from web_gui.certificates import quantum_crypto as qc
from web_gui.certificates import ssl_config
from hashlib import sha3_256


def test_load_certificate_and_key_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        cert_path = Path(tmp) / "cert.pem"
        key_path = Path(tmp) / "key.pem"
        cert_path.write_text("cert")
        key_path.write_text("key")
        assert cm.load_certificate(str(cert_path)) == b"cert"
        assert cm.load_private_key(str(key_path)) == b"key"


def test_load_certificate_missing():
    with pytest.raises(FileNotFoundError):
        cm.load_certificate("missing.pem")


def test_create_ssl_context_missing_files():
    with pytest.raises(FileNotFoundError):
        ssl_config.create_ssl_context("missing.crt", "missing.key")


def test_quantum_safe_hash_and_key_generation():
    data = b"hello"
    assert qc.quantum_safe_hash(data) == sha3_256(data).hexdigest()
    key = qc.generate_quantum_safe_key(16)
    assert isinstance(key, bytes)
    assert len(key) == 16
