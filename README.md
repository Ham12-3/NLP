# Text Corrector

A web application that corrects grammar and converts text between **British English** and **American English**.

- **Backend** -- Python FastAPI + LanguageTool
- **Frontend** -- Next.js 14 + Tailwind CSS
- **Containerised** -- Docker Compose for one-command startup

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| Java (JRE) | 8+ (required by LanguageTool) |
| Docker (optional) | 20+ |

> **Java is required** because `language-tool-python` runs a local LanguageTool server under the hood.

---

## Quick start with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000
- Health:   http://localhost:8000/health

---

## Run locally (without Docker)

### Backend

**Windows (PowerShell)**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**macOS / Linux**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at http://localhost:3000.

---

## Running tests

```bash
cd backend
pip install -r requirements.txt   # if not already installed
pytest tests/ -v
```

---

## API Reference

### `POST /correct`

Corrects grammar and applies variant spelling.

**Request**

```json
{
  "text": "i like the color of this center",
  "variant": "uk"
}
```

**Response**

```json
{
  "corrected": "I like the colour of this centre.",
  "variant": "uk",
  "changes": [
    { "type": "grammar", "original": "i", "replacement": "I" },
    { "type": "spelling", "original": "color", "replacement": "colour" },
    { "type": "spelling", "original": "center", "replacement": "centre" }
  ]
}
```

### Example `curl` requests

**UK variant**

```bash
curl -X POST http://localhost:8000/correct \
  -H "Content-Type: application/json" \
  -d '{"text": "i like the color of this center", "variant": "uk"}'
```

**US variant**

```bash
curl -X POST http://localhost:8000/correct \
  -H "Content-Type: application/json" \
  -d '{"text": "I like the colour of this centre.", "variant": "us"}'
```

**Empty input (validation error)**

```bash
curl -X POST http://localhost:8000/correct \
  -H "Content-Type: application/json" \
  -d '{"text": "", "variant": "us"}'
```

Returns HTTP 422 with a validation error message.

---

## Project structure

```
NLP/
  backend/
    app/
      __init__.py
      main.py          # FastAPI app, CORS, /correct endpoint
      schemas.py        # Pydantic request/response models
      corrector.py      # Grammar + variant spelling logic
    tests/
      __init__.py
      test_corrector.py # pytest test suite (8+ tests)
    requirements.txt
    Dockerfile
  frontend/
    src/
      app/
        layout.tsx      # Root layout
        page.tsx         # Home page
        globals.css      # Tailwind imports
      components/
        TextCorrector.tsx  # Main UI component
    package.json
    tailwind.config.ts
    Dockerfile
  docker-compose.yml
  README.md
```

---

## Acceptance criteria

| Input | Variant | Expected output |
|-------|---------|-----------------|
| `i like the color of this center` | UK | `I like the colour of this centre.` |
| `I like the colour of this centre.` | US | `I like the color of this center.` |

---

## How it works

1. **Grammar correction** -- LanguageTool (running locally via `language-tool-python`) fixes grammar, capitalisation, and punctuation.
2. **Variant conversion** -- A curated dictionary of US/UK spelling pairs converts words to the selected variant. URLs, names, and numbers are preserved.
3. **Change tracking** -- Every modification is logged with its type (spelling, grammar, punctuation) so the user can see exactly what changed.
