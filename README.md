# Tiny-ando API

Flask API with two endpoints:
- `GET /healthz`
- `POST /chat`

## Local run
```bash
pip install -r requirements-dev.txt
python app/main.py
```

## Test
```bash
pytest -q
```

## Vercel deployment
This repo is configured for Vercel Python runtime using `api/index.py` and `vercel.json`.

Notes:
- Python is pinned to 3.12 for Vercel compatibility (`.python-version`, `runtime.txt`).
- The `/chat` endpoint lazy-loads model dependencies and will return `503` if model packages are unavailable in the deployment environment.
