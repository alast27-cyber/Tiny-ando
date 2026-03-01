import os

from flask import Flask, request, jsonify

app = Flask(__name__)

MODEL_NAME = os.getenv("MODEL_NAME", "distilgpt2")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "1000"))
_tokenizer = None
_model = None


def _get_model_components():
    """Lazily initialize and cache model dependencies."""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        from transformers import AutoTokenizer, AutoModelForCausalLM

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    return _tokenizer, _model


def _extract_message(payload):
    """Extract and validate a chat message from a JSON payload."""
    if not isinstance(payload, dict):
        return None

    raw_message = payload.get("message")
    if not isinstance(raw_message, str):
        return None

    user_message = raw_message.strip()
    if not user_message:
        return None

    return user_message


def _generate_reply(user_message):
    """Generate a chat reply for a validated message."""
    tokenizer, model = _get_model_components()
    inputs = tokenizer(user_message, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=50)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


@app.route("/", methods=["GET"])
def index():
    return """
    <html>
      <head><title>Tiny-ando API</title></head>
      <body>
        <h1>Tiny-ando API</h1>
        <p>Status: ok</p>
        <ul>
          <li><a href=\"/healthz\">GET /healthz</a></li>
          <li>POST /chat</li>
        </ul>
      </body>
    </html>
    """


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_message = _extract_message(data)

    if user_message is None:
        return jsonify({"error": "message is required"}), 400

    if len(user_message) > MAX_INPUT_CHARS:
        return jsonify({"error": f"message exceeds {MAX_INPUT_CHARS} characters"}), 400

    try:
        reply = _generate_reply(user_message)
    except (ImportError, OSError, RuntimeError, ValueError):
        return jsonify({"error": "chat model unavailable"}), 503

    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
