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
docker-compose run lando pytest -q
```

### 5. Chat
```powershell
curl -X POST http://localhost:8090/chat -H "Content-Type: application/json" -d "{\"message\": \"Hello Lando!\"}"
```


## Render deployment note

This project depends on `torch`/`transformers`, which currently require a Python version with prebuilt wheels available.
For Render, pin Python to **3.10** using `runtime.txt` (included in this repo) to avoid install failures on Render's default newer Python runtimes.
