from app.main import app, MAX_INPUT_CHARS


def test_index_route():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert "Tiny-ando API" in response.get_data(as_text=True)
    assert "/healthz" in response.get_data(as_text=True)
    assert "/chat" in response.get_data(as_text=True)


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


def test_chat_rejects_overly_long_message():
    client = app.test_client()
    response = client.post("/chat", json={"message": "x" * (MAX_INPUT_CHARS + 1)})
    assert response.status_code == 400
    assert response.json == {"error": f"message exceeds {MAX_INPUT_CHARS} characters"}


def test_chat_returns_503_if_model_unavailable(monkeypatch):
    client = app.test_client()

    def _boom(_):
        raise RuntimeError("model init failed")

    monkeypatch.setattr("app.main._generate_reply", _boom)

    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 503
    assert response.json == {"error": "chat model unavailable"}


def test_chat_returns_generated_reply(monkeypatch):
    client = app.test_client()

    monkeypatch.setattr("app.main._generate_reply", lambda _: "hi from lando")

    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json == {"reply": "hi from lando"}
