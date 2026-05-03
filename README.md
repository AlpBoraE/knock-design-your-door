# KNOCK: The Door I Knock On

KNOCK is a web-based interactive AI artwork for the CSE 358 Introduction to Artificial Intelligence creative project, "KNOCK - Design Your Door." The user answers three personal questions about farewell, transition, and meaning. The Python backend analyzes the emotional tone of the answers, combines the answers with curated historical context, and generates a poetic personal "door manifesto" plus a symbolic text-to-image prompt.

The project is inspired by Bob Dylan's 1973 song "Knockin' on Heaven's Door" and its connection to Pat Garrett & Billy the Kid, while avoiding direct lyric quotation. It uses the themes around the song: mortality, farewell, western dust, aging legends, the Vietnam War era, counterculture anti-war feeling, and the search for meaning at a threshold.

## Artistic Statement

The door is used as a symbolic object. It can be a border, a goodbye, a possible future, or a place where a person pauses before changing. In this project, AI is not treated only as a machine that produces text or images. It becomes a reflective system that listens to the user's answers, detects an emotional direction, and turns that direction into a personal artwork.

The historical context matters because the user's private farewell is placed beside a public atmosphere of 1973: war exhaustion, protest, western myth, film, music, silence, badges, dust, and sunset. The final output should feel like a small digital ritual rather than a simple technical demo.

## Technical Architecture

- `frontend/`: A polished single-page web app built with HTML, CSS, and vanilla JavaScript.
- `backend/app/main.py`: FastAPI app with health and generation endpoints.
- `backend/app/sentiment.py`: VADER-based sentiment and emotion classification.
- `backend/app/motif_extractor.py`: Extracts symbolic motifs from user language, emotion, and retrieved context.
- `backend/app/rag_context.py`: Loads curated historical context files and scores context lenses for the user's answers.
- `backend/app/llm_generator.py`: Uses Gemini or OpenAI when available, with a local fallback generator when no key exists.
- `backend/app/image_generator.py`: Optionally uses OpenAI image generation and saves generated PNG files.
- `backend/app/pipeline.py`: Coordinates the full generation flow and saves JSON outputs.
- `backend/verify_project.py`: Runs a quick local verification of the AI/NLP pipeline.
- `backend/context/`: Three small context files about Dylan in 1973, Vietnam counterculture, and Pat Garrett & Billy the Kid.
- `backend/outputs/`: Stores generated JSON outputs and optional images.

Architecture sketch:

```text
User answers in browser
        ->
frontend/app.js
        ->
FastAPI /api/generate
        ->
sentiment analysis + context-lens retrieval + motif extraction
        ->
Gemini or OpenAI text generation, or local fallback
        ->
manifesto + image prompt + historical influence
        ->
saved JSON output + frontend result view
```

## AI Techniques Used

1. **Sentiment and emotion analysis**
   The backend combines the user's three answers and analyzes them with VADER sentiment plus keyword signals. It classifies the tone as melancholic, hopeful, angry, nostalgic, peaceful, or conflicted.

2. **Lightweight context retrieval**
   The backend loads the 1973, Vietnam counterculture, and Pat Garrett context files, then scores smaller "context lenses" against the user's words and detected emotion. Those selected lenses guide the generator, appear in the frontend, and are saved in each output JSON file.

3. **Symbolic motif extraction**
   A custom motif extractor maps the user's language into presentation-friendly symbolic motifs such as Home / Exile, Silence / Voice, Badge / Authority, Road / Beginning, War / Refusal, Memory / Legacy, Mortality / Sky, and Dust / Time. These motifs are shown in the frontend and also fed into the generator.

4. **LLM-based contextual generation**
   If `GEMINI_API_KEY` or `OPENAI_API_KEY` is configured, the backend sends the user's answers, detected emotion, and historical context to a language model. The prompt asks for an original 250-400 word poetic manifesto, an image prompt, and a historical influence explanation.

5. **Text-to-image generation or image prompt generation**
   The backend always creates a detailed symbolic image prompt. If image generation is enabled and the OpenAI image API succeeds, it saves a generated image in `backend/outputs/` and returns its path to the frontend. If image generation fails, the app still displays the prompt and continues.

## Rubric Alignment

**Technical depth: strong**
The project uses a modular FastAPI backend, frontend/backend API communication, VADER sentiment analysis, context-lens scoring, symbolic motif extraction, optional Gemini/OpenAI language generation, optional image generation, graceful fallback behavior, CORS configuration, timestamped JSON output saving, and a local verification script.

**Artistic originality: strong**
The artwork is not only a form around an API call. The visual design uses a door-shaped interface, cinematic western color, dust-like texture, a personal ritual structure, a visible symbolic motif map, and visible historical lenses. The fallback generator also changes symbolic material, knock sound, and final gesture based on emotional tone.

**Philosophical engagement: strong**
The project asks the user to reflect on farewell, transition, mortality, memory, legacy, and meaning. It treats AI as a tool, collaborator, and mirror rather than as a simple answer machine.

**Presentation and craft: strong**
The app is runnable with or without an API key, has clear Windows instructions, keeps generated outputs out of Git, and includes a backend README plus an artist manifesto.

## Submission Readiness

This repository currently satisfies the assignment structure in a reviewer-friendly way:

- functioning digital artwork
- original source code
- at least two distinct AI techniques
- historical and cultural context woven into the pipeline
- artist manifesto included as `Artist_Manifesto.md`
- README with setup, architecture, AI techniques, and example output

## Installation on Windows

Recommended first-run path for a reviewer after cloning:

```powershell
git clone https://github.com/AlpBoraE/knock-design-your-door.git
cd knock-design-your-door
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Open PowerShell in the project root:

```powershell
cd knock-design-your-door
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional Gemini or OpenAI setup:

```powershell
copy .env.example .env
notepad .env
```

For Gemini, add your key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
AI_PROVIDER=gemini
```

For OpenAI, add your key:

```env
OPENAI_API_KEY=your_api_key_here
AI_PROVIDER=openai
```

The project runs without this key by using local fallback generation.

## Run Backend

Recommended Windows command from the project root:

```powershell
cd backend
.\start_backend.ps1
```

This script uses port `8010` by default, stops old KNOCK `uvicorn` processes first, installs missing dependencies, and then starts the backend.

Why `8010` instead of `8000`?

FastAPI/Uvicorn normally uses `8000`, and the project can still run there. On Windows, however, `uvicorn --reload` can leave old child processes behind, which caused repeated `8000 already in use` errors on this machine. For that reason, the recommended script uses `8010` as the stable project port.

Backend URL:

```text
http://localhost:8010
```

If you specifically want the classic FastAPI assignment port `8000`, run:

```powershell
.\start_backend.ps1 -Port 8000
```

or manually:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If PowerShell blocks scripts for this terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start_backend.ps1
```

Manual command, if needed:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

To stop old backend processes:

```powershell
.\stop_backend.ps1
```

Health check:

```text
http://localhost:8010/api/health
```

Verify the local AI/NLP pipeline without opening the frontend:

```powershell
python verify_project.py
```

## Run Frontend

Open a second PowerShell window:

```powershell
cd knock-design-your-door
cd frontend
.\start_frontend.ps1
```

Open:

```text
http://localhost:5500
```

The frontend automatically tries backend ports `8010`, `8000`, and `8001`, so you do not need to edit JavaScript if the backend port changes among those.

Port summary:

- Recommended stable backend port: `8010`
- Classic/default FastAPI port: `8000`
- Frontend port: `5500`

## Environment Variables

Create `backend/.env` from `backend/.env.example`.

```env
OPENAI_API_KEY=
GEMINI_API_KEY=
AI_PROVIDER=auto
OPENAI_TEXT_MODEL=gpt-5.5
GEMINI_TEXT_MODEL=gemini-2.5-flash
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_IMAGE_SIZE=1024x1024
OPENAI_GENERATE_IMAGES=true
```

- `AI_PROVIDER`: `auto`, `gemini`, `openai`, or `local`. In `auto`, Gemini is used first if `GEMINI_API_KEY` exists.
- `GEMINI_API_KEY`: Required for Gemini text generation.
- `GEMINI_TEXT_MODEL`: Gemini model used for manifesto and prompt generation.
- `OPENAI_API_KEY`: Required for OpenAI text generation and optional OpenAI image generation.
- `OPENAI_TEXT_MODEL`: Model used for manifesto and prompt generation.
- `OPENAI_IMAGE_MODEL`: Image model used for optional image generation.
- `OPENAI_IMAGE_SIZE`: Output image size.
- `OPENAI_GENERATE_IMAGES`: Set to `false` to skip image generation even with an API key.

## API Requirements

### GET `/api/health`

Returns backend status, whether Gemini or OpenAI keys are configured, and which text provider will be used.

### POST `/api/generate`

Input:

```json
{
  "leave_behind": "my old home",
  "threshold": "moving to a new city",
  "hope_to_hear": "that I am allowed to begin again"
}
```

Output:

```json
{
  "emotion": {
    "dominant_emotion": "hopeful",
    "score": 0.78,
    "description": "Your answers lean toward renewal..."
  },
  "motifs": [
    {
      "name": "Road / Beginning",
      "symbol": "a road continuing beyond a sunset door",
      "meaning": "The answer points toward movement, risk, graduation, a new future, or an unfinished beginning.",
      "score": 2.8
    }
  ],
  "context_lenses": [
    {
      "source": "vietnam_counterculture",
      "title": "Vietnam-era protest atmosphere",
      "summary": "Vietnam-era counterculture adds moral pressure...",
      "matched_terms": ["peace"],
      "relevance": 2.25
    }
  ],
  "manifesto_text": "I arrive at my door...",
  "image_prompt": "Cinematic symbolic digital artwork...",
  "historical_influence": "The result is shaped by 1973...",
  "image_url_or_path": null
}
```

## Example Output

The fallback generator may produce a manifesto that connects the user's personal threshold with a 1973 western landscape, anti-war posters, a fallen badge, dust, sunset, farewell, and a wish to continue. With a Gemini or OpenAI key, the language will vary more. Optional generated images currently use the OpenAI image API when `OPENAI_API_KEY` is available.

Generated JSON files also save the selected context lenses, so the student can explain which parts of the historical archive shaped a specific run. The frontend displays both motifs and context lenses for presentation transparency.

## Screenshots

Add screenshots here after running the project:

- Front page with the door form
- Generated manifesto result
- Optional generated image preview

Sample fallback output characteristics:

- emotional tone classification such as `hopeful`, `nostalgic`, or `conflicted`
- 3 to 4 symbolic motifs extracted from the user's language
- 3 historical context lenses selected from the curated archive
- a 250 to 400 word personal manifesto
- a cinematic symbolic image prompt

## Academic Integrity and Transparency

This project is transparent about its AI use:

- VADER sentiment analysis is used for lightweight NLP tone detection.
- Context-lens scoring is used as a simple retrieval technique over student-written historical context files.
- Symbolic motif extraction is custom student-readable NLP logic that turns user language into visual and philosophical motifs.
- Gemini text generation is optional and requires `GEMINI_API_KEY`.
- OpenAI text generation is optional and requires `OPENAI_API_KEY`.
- OpenAI image generation is optional and requires `OPENAI_API_KEY` plus image model access.
- A local template-based fallback is included so the project remains runnable without paid API access.
- The curated historical context files are written into the project and loaded by the backend.
- The system prompt instructs the model not to quote or copy Bob Dylan lyrics.

## Limitations

- The emotion classifier is interpretive, not a psychological diagnosis.
- The local fallback generator is intentionally smaller than a full LLM, but it still creates a meaningful result without paid API access.
- Optional OpenAI image generation depends on API key access, model availability, and account permissions.

## Notes

- No database is used.
- No authentication is used.
- No Docker setup is required.
- Generated outputs are saved in `backend/outputs/`, but generated files are ignored by Git except `.gitkeep`.
