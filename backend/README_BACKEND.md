# Backend README

This backend powers the AI pipeline for **KNOCK: The Door I Knock On**.

## What It Does

1. Accepts three personal answers from the frontend.
2. Combines the answers into one reflection.
3. Detects emotional tone with VADER sentiment and keyword analysis.
4. Loads curated context about Dylan in 1973, Vietnam counterculture, and Pat Garrett & Billy the Kid.
5. Scores smaller context lenses to connect the user's words with the most relevant historical material.
6. Extracts symbolic motifs such as Road / Beginning, Silence / Voice, Badge / Authority, and Mortality / Sky.
7. Generates a poetic manifesto, symbolic image prompt, and historical influence explanation with Gemini, OpenAI, or the local fallback.
8. Optionally generates an image with OpenAI if an OpenAI API key is configured.
9. Saves each result as a timestamped JSON file in `outputs/`.

## Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional:

```powershell
copy .env.example .env
```

Then edit `.env` and add either `GEMINI_API_KEY` or `OPENAI_API_KEY`.

## Run

Recommended:

```powershell
.\start_backend.ps1
```

The starter script uses port `8010` and stops old `uvicorn` processes before starting a new one.

Why `8010`?

The normal FastAPI/Uvicorn default is `8000`, and the backend supports it. This project uses `8010` in the starter script because Windows reload processes previously left `8000` occupied. To use `8000` instead:

```powershell
.\start_backend.ps1 -Port 8000
```

Manual:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Classic FastAPI command:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://localhost:8010/api/health
```

Verify the local pipeline:

```powershell
python verify_project.py
```

Stop backend processes:

```powershell
.\stop_backend.ps1
```

## Endpoints

### GET `/api/health`

Returns:

```json
{
  "status": "ok",
  "project": "KNOCK: The Door I Knock On",
  "ai_configured": false,
  "openai_configured": false,
  "gemini_configured": false,
  "text_provider": "local"
}
```

### POST `/api/generate`

Input:

```json
{
  "leave_behind": "a place I called home",
  "threshold": "graduation and uncertainty",
  "hope_to_hear": "that I can begin again"
}
```

Returns:

```json
{
  "emotion": {
    "dominant_emotion": "hopeful",
    "score": 0.78,
    "description": "..."
  },
  "motifs": [
    {
      "name": "Road / Beginning",
      "symbol": "a road continuing beyond a sunset door",
      "meaning": "...",
      "score": 2.8
    }
  ],
  "context_lenses": [
    {
      "source": "vietnam_counterculture",
      "title": "Vietnam-era protest atmosphere",
      "summary": "...",
      "matched_terms": ["peace"],
      "relevance": 2.25
    }
  ],
  "manifesto_text": "...",
  "image_prompt": "...",
  "historical_influence": "...",
  "image_url_or_path": null
}
```

## Offline Fallback

If both `GEMINI_API_KEY` and `OPENAI_API_KEY` are missing, or the selected API call fails, the backend uses a local generator. The local path still provides:

- emotional tone
- symbolic motifs
- selected historical context lenses
- poetic manifesto
- symbolic image prompt
- historical influence explanation
- saved JSON output

The fallback still uses the detected emotion and selected historical lenses, so the project remains more than a static template.

## CORS

The backend allows requests from:

- `http://localhost:5500`
- `http://127.0.0.1:5500`
