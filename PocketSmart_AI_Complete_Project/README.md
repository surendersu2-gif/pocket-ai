# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application implementing the supplied project specification: Home Interior, Party, and Jewelry budget planners; authentication; session/history endpoints; Gemini-powered recommendation generation; multimodal outfit analysis; and deterministic fallback recommendations.

## Important implementation note
The supplied document mixes Flask and FastAPI in different sections. The later architecture, milestones, route list, Jinja2 UI, JWT/session APIs, and `main.py` section consistently describe FastAPI, so this implementation uses **FastAPI** throughout. The document also allows mocked/simulated marketplace sourcing, so the catalog in `app/services/catalog.py` is deliberately a safe local adapter rather than a scraper.

The document names Gemini 1.5 Flash Pro. Gemini model availability changes over time, so the actual model is configurable through `GEMINI_MODEL`; the example defaults to `gemini-2.5-flash`. Set it to another model available to your API key if needed.

## Features
- Registration/login/logout with JWT and HTTP-only cookie
- SQLite persistence through SQLAlchemy
- `/generate-home`, `/generate-party`, `/generate-jewelry`
- `/token` accepts the same JSON credentials as `/login` and returns a JWT
- `/session-info`, `/session-data`, `/history`, `/recommendations-details/{id}`
- Gemini JSON recommendation generation using the candidate catalog
- Optional JPG/PNG/WEBP outfit image for jewelry planner
- Automatic fallback when Gemini is not configured or unavailable
- Responsive Jinja2 frontend
- API health endpoint and pytest test

## 1. VS Code setup
1. Install Python 3.11+ and VS Code.
2. Open this project folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:
   - Windows: `py -m venv .venv`
   - macOS/Linux: `python3 -m venv .venv`
5. Activate it:
   - Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
   - Windows CMD: `.venv\\Scripts\\activate.bat`
   - macOS/Linux: `source .venv/bin/activate`
6. Install dependencies: `pip install -r requirements.txt`
7. Copy `.env.example` to `.env`.

## 2. Gemini setup
Create a Gemini API key in Google AI Studio, then put it in `.env`:

`GEMINI_API_KEY=your_key_here`

You can change `GEMINI_MODEL` without changing code. If the key is blank, the app still runs using the local deterministic recommendation engine.

## 3. Run
```bash
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000`.

API documentation: `http://127.0.0.1:8000/docs`

## 4. Test
```bash
pytest -q
```
Health check: `http://127.0.0.1:8000/api/health`

## 5. Recommended manual test
1. Register an account.
2. Open Home Planner, enter a budget and at least one room item.
3. Generate the plan and verify total + remaining budget.
4. Open Party Planner and test a small guest count.
5. Open Jewelry Planner and upload a JPG/PNG/WEBP outfit image.
6. Open History and confirm saved plans appear.
7. Remove `GEMINI_API_KEY`, restart, and confirm fallback recommendations still render.

## Project tree
```text
pocketsmart_ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth.py
│   ├── models/
│   │   ├── db_models.py
│   │   └── schemas.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── planners.py
│   │   └── session.py
│   ├── services/
│   │   ├── catalog.py
│   │   └── recommendation.py
│   ├── templates/
│   └── static/
├── tests/test_api.py
├── requirements.txt
├── .env.example
└── README.md
```
