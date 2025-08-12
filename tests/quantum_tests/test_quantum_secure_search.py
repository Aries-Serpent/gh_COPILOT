import json
import sqlite3
from pathlib import Path

from ghc_quantum.algorithms import QuantumEncryptedCommunication
from ghc_quantum.quantum_database_search import quantum_secure_search


def test_encryption_round_trip():
    engine = QuantumEncryptedCommunication("secret")
    message = "hello"
    encrypted = engine.encrypt_message(message)
    assert encrypted != message
    assert engine.decrypt_message(encrypted) == message


def test_quantum_secure_search(tmp_path: Path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE items(id INTEGER, value TEXT)")
    conn.execute("INSERT INTO items VALUES(1, 'alpha')")
    conn.commit()
    conn.close()

    encrypted_rows = quantum_secure_search("SELECT value FROM items", db_path=db_path, key="key")
    assert encrypted_rows
    engine = QuantumEncryptedCommunication("key")
    decrypted = [json.loads(engine.decrypt_message(row)) for row in encrypted_rows]
    assert decrypted == [{"value": "alpha"}]
