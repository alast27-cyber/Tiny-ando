from flask import Flask, request, jsonify

app = Flask(__name__)

MODEL_NAME = "distilgpt2"
_tokenizer = None
_model = None


def _get_model_components():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        from transformers import AutoTokenizer, AutoModelForCausalLM

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    return _tokenizer, _model


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    tokenizer, model = _get_model_components()
    inputs = tokenizer(user_message, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=50)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
