import pytest

from app.rag.extractors import extract_upload_text


def test_extract_text_file() -> None:
    assert extract_upload_text("note.txt", "hello rag".encode("utf-8")) == "hello rag"


def test_reject_unsupported_file() -> None:
    with pytest.raises(ValueError, match="supported"):
        extract_upload_text("image.png", b"not text")
