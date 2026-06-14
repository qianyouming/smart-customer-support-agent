from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_and_retrieve() -> None:
    response = client.post(
        "/api/files",
        files={"file": ("agent.txt", b"RAG retrieves relevant context before generation.", "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["chunks_created"] == 1

    chat_response = client.post(
        "/api/chat",
        json={"message": "根据上传文档回答：RAG 是什么？", "session_id": "retrieval-test"},
    )
    assert chat_response.status_code == 200
    body = chat_response.json()
    assert any(tool["tool_name"] == "retrieval" for tool in body["used_tools"])
    assert body["citations"]


def test_document_detail_contains_chunks() -> None:
    response = client.post(
        "/api/files",
        files={"file": ("detail.txt", b"Knowledge base detail content.", "text/plain")},
    )
    assert response.status_code == 200
    document_id = response.json()["document_id"]

    detail_response = client.get(f"/api/files/{document_id}")
    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["filename"] == "detail.txt"
    assert body["chunks_count"] == 1
    assert body["chunks"][0]["content"] == "Knowledge base detail content."


def test_delete_document() -> None:
    response = client.post(
        "/api/files",
        files={"file": ("delete-me.txt", b"temporary support policy", "text/plain")},
    )
    assert response.status_code == 200
    document_id = response.json()["document_id"]

    delete_response = client.delete(f"/api/files/{document_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}
