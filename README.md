# Lando Final Bundle (CPU)

This is the lightweight CPU-only Docker bundle for **Lando**.

## 🚀 Usage (Windows PowerShell)

### 1. Build fresh
```powershell
docker-compose build --no-cache
```

### 2. Start chatbot API
```powershell
docker-compose up
```

Now visit:  
👉 http://localhost:8090/healthz

### 3. Train (stub)
```powershell
docker-compose run lando python app/train.py
```

### 4. Run tests
```powershell
docker-compose run lando pip install -r requirements-dev.txt
docker-compose run lando pytest -q
```

### 5. Chat
```powershell
curl -X POST http://localhost:8090/chat -H "Content-Type: application/json" -d "{\"message\": \"Hello Lando!\"}"
```


## Render deployment note

This project depends on `torch`/`transformers`, which currently require a Python version with prebuilt wheels available.
For Render, pin Python to **3.10** using `runtime.txt` (included in this repo) to avoid install failures on Render's default newer Python runtimes.
If Render still detects 3.14, add `.python-version` and set `PYTHON_VERSION=3.10.14` (included via `render.yaml`).


### Runtime environment variables

- `PORT`: web server port (defaults to `8080`; Render sets this automatically).
- `MODEL_NAME`: Hugging Face model id to load (defaults to `distilgpt2`).
- `MAX_INPUT_CHARS`: maximum accepted `message` length for `/chat` (defaults to `1000`).


## Render quick setup

1. Ensure `runtime.txt` is present (Python 3.10 pin).
2. Use `pip install -r requirements.txt` as the build command.
3. Use `gunicorn --bind 0.0.0.0:$PORT app.main:app` as the start command.
4. Set health check path to `/healthz`.

You can also deploy using `render.yaml` included in this repo.


## Render troubleshooting

If you see this error:

- `Empty build command; skipping build`
- `Publish directory dish does not exist`

then the service was created as a **Static Site**. This repo is a Flask API and must be deployed as a **Web Service**.

Fix:
1. In Render, create/select a **Web Service** (not Static Site).
2. Use the included `render.yaml` blueprint, or set:
   - Build command: `./scripts/render-build.sh`
   - Start command: `./scripts/render-start.sh`
3. Keep Python pinned to `3.10.14` (`runtime.txt`, `.python-version`, and `PYTHON_VERSION` env var are included).


On Render, this project installs **CPU-only PyTorch wheels** from `https://download.pytorch.org/whl/cpu` to avoid downloading CUDA packages and reduce build size/time.


Render uses a direct CPU torch wheel URL in `requirements.txt` to prevent CUDA dependency downloads during deploy.


After updating deployment files, trigger a **manual redeploy** in Render so it uses the latest commit.
