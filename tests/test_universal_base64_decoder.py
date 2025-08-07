import base64
import io
from pathlib import Path
import zipfile

from universal_base64_decoder import analyze_base64_content

def test_analyze_base64_detects_zip(tmp_path, monkeypatch):
    """`analyze_base64_content` should classify ZIP archives correctly."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("hello.txt", "hello")
    b64 = base64.b64encode(buf.getvalue()).decode()

    monkeypatch.chdir(tmp_path)
    result = analyze_base64_content(b64)

    assert result["success"] is True
    assert result["file_type"] == "ZIP Archive"
    assert Path(result["output_file"]).exists()
