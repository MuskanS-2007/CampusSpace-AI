# CampusSpace AI

**Explainable campus-room recommendations** for DATATHON Track 2.

This starter project includes the supplied synthetic dataset, a FastAPI backend, a React + Vite frontend, and a rule-based room matching engine. The ML training step is intentionally kept separate so we can inspect the data and choose a defensible target before training.

> Dataset caveat: these files are synthetic educational data, not a live campus booking system. Results indicate conflicts found in the supplied records only; they do not guarantee real-world availability.

## Stack
- Frontend: React + Vite
- Backend: Python, FastAPI, pandas
- Planned ML: scikit-learn after target/feature audit
- Deployment: Vercel (frontend), Render (backend)

## 1. Backend setup (Windows PowerShell)
Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.data_loader
uvicorn app.main:app --reload
```

Backend API: http://127.0.0.1:8000  
Interactive API docs: http://127.0.0.1:8000/docs

If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` only for that terminal session, then activate again; alternatively run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m uvicorn app.main:app --reload` without activation.

## 2. Frontend setup
Open a second terminal in the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (usually http://localhost:5173).

The frontend uses `VITE_API_BASE_URL`; the default is `http://127.0.0.1:8000`. See `frontend/.env.example`.

## What works now
- Dataset loading and basic validation
- Room search by date, time, duration, capacity, projector, and computers
- Checks room capacity and facilities
- Checks recurring class schedule by weekday and date-specific event conflicts
- Ranks matching rooms with transparent rule-based scores
- Admin summary charts based on the supplied records
- API health and documentation endpoints

## Known limitations
- The dataset has no guaranteed room assignment for requests. The recommendation engine matches requests to rooms; it does not learn a confirmed booking outcome.
- The schedule file has weekday/time fields and the events file has specific timestamps. The app combines these checks but cannot verify real-world bookings.
- The scoring value is a heuristic suitability score, not an ML probability.
- Event records cover the dates contained in the dataset. An unrecorded event cannot be detected.
- The ML model has not yet been trained. We will audit potential target leakage and label quality before selecting a model.

## Deployment outline
1. Push this project to a GitHub repository.
2. Deploy `backend` as a Render Python web service. Build command: `pip install -r requirements.txt`; start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set the root directory to `backend`.
3. Deploy `frontend` on Vercel with root directory `frontend`. Add `VITE_API_BASE_URL` set to your deployed Render service URL (no trailing slash).
4. Set Render environment variable `FRONTEND_ORIGIN` to the deployed Vercel URL. For local use it defaults to localhost:5173.
5. Redeploy after changing environment variables.

## Data
The original `README.txt` and all four supplied CSVs are included in `backend/data/`.
