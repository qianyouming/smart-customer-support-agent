"""Tests for health and core chat behavior."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_calculator() -> None:
    response = client.post("/api/chat", json={"message": "23 * 47 等于多少？", "session_id": "test"})
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "test"
    assert body["used_tools"][0]["tool_name"] == "calculator"
    assert body["need_human"] is False


def test_chat_handoff_when_evidence_missing() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "根据上传文档回答：一个完全不存在的问题是什么？", "session_id": "handoff-test"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["need_human"] is True
    assert body["handoff_reason"]
