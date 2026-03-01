from flask import Flask, request, jsonify

app = Flask(__name__)

MODEL_NAME = "distilgpt2"
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


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_message = _extract_message(data)

    if user_message is None:
        return jsonify({"error": "message is required"}), 400

    try:
        tokenizer, model = _get_model_components()
        inputs = tokenizer(user_message, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=50)
        reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    except (ImportError, OSError, RuntimeError, ValueError):
        return jsonify({"error": "chat model unavailable"}), 503

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
