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


## Vercel troubleshooting
If Vercel logs show `npm install` / `vite build` or TypeScript errors (for example files like `*.tsx`), then Vercel is building the wrong project.

For this repo, expected Vercel behavior is Python build using `vercel.json` and `api/index.py`.

Checklist:
- Vercel project must point to Git repo: `alast27-cyber/Tiny-ando`
- Production branch should be `main`
- Root Directory should be repo root (`/`)
- Framework Preset should be **Other** (or no framework)
- Build Command should be empty (let `@vercel/python` handle build)
- Output Directory should be empty
