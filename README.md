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
