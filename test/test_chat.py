from app.main import app


def test_healthz():
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_chat_requires_message():
    client = app.test_client()

    response = client.post("/chat", json={})
    assert response.status_code == 400
    assert response.json == {"error": "message is required"}

    response = client.post("/chat", json={"message": "   "})
    assert response.status_code == 400
    assert response.json == {"error": "message is required"}

    response = client.post("/chat", json={"message": 123})
    assert response.status_code == 400
    assert response.json == {"error": "message is required"}


def test_chat_rejects_non_object_json_payload():
    client = app.test_client()

    response = client.post("/chat", json=["hello"])
    assert response.status_code == 400
    assert response.json == {"error": "message is required"}


def test_chat_returns_503_if_model_unavailable(monkeypatch):
    client = app.test_client()

    def _boom():
        raise RuntimeError("model init failed")

    monkeypatch.setattr("app.main._get_model_components", _boom)

    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 503
    assert response.json == {"error": "chat model unavailable"}
