from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_session_list_and_messages() -> None:
    session_id = "user-session-api"
    response = client.post("/api/chat", json={"message": "退款周期是多久？", "session_id": session_id})
    assert response.status_code == 200

    sessions = client.get("/api/sessions")
    assert sessions.status_code == 200
    assert any(item["session_id"] == session_id for item in sessions.json())

    messages = client.get(f"/api/sessions/{session_id}/messages")
    assert messages.status_code == 200
    body = messages.json()
    assert any(item["role"] == "user" for item in body)
    assert any(item["role"] == "assistant" for item in body)


def test_test_sessions_are_hidden() -> None:
    response = client.post("/api/chat", json={"message": "退款周期是多久？", "session_id": "test-hidden"})
    assert response.status_code == 200

    sessions = client.get("/api/sessions")
    assert sessions.status_code == 200
    assert all(item["session_id"] != "test-hidden" for item in sessions.json())


def test_rename_session() -> None:
    session_id = "user-rename-session"
    client.post("/api/chat", json={"message": "退款周期是多久？", "session_id": session_id})

    response = client.patch(f"/api/sessions/{session_id}", json={"title": "退款咨询"})
    assert response.status_code == 200
    assert response.json()["title"] == "退款咨询"


def test_delete_session() -> None:
    session_id = "user-delete-session"
    client.post("/api/chat", json={"message": "退款周期是多久？", "session_id": session_id})

    delete_response = client.delete(f"/api/sessions/{session_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}

    sessions = client.get("/api/sessions")
    assert sessions.status_code == 200
    assert all(item["session_id"] != session_id for item in sessions.json())
