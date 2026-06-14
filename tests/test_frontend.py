from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_frontend_index() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Customer Support Agent" in response.text


def test_frontend_asset() -> None:
    response = client.get("/static/app.js")
    assert response.status_code == 200
    assert "sendMessage" in response.text
    assert "loadSessions" in response.text


def test_document_detail_page() -> None:
    response = client.get("/documents/example-document")
    assert response.status_code == 200
    assert "文档详情" in response.text
    assert "/static/document.js" in response.text


def test_document_detail_asset() -> None:
    response = client.get("/static/document.js")
    assert response.status_code == 200
    assert "loadDocument" in response.text
