import enterprise_modules.file_utils as fu


def test_read_file_with_encoding_detection_without_chardet(monkeypatch, tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(fu, "chardet", None)
    content, status = fu.read_file_with_encoding_detection(str(sample))
    assert content == "hello"
    assert status == "SUCCESS_FALLBACK_utf-8"
