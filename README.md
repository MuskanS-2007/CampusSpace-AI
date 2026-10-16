# CampusSpace AI

**Explainable campus-room recommendations for DATATHON 2026 — Track 2: “The Campus Has Space. Students Don’t.”**

CampusSpace AI helps students, study groups, club coordinators, and campus staff find rooms that fit their session requirements. Users enter a date, time, duration, capacity, and required facilities. The app filters unsuitable rooms, checks the supplied class and event records for conflicts, ranks the remaining rooms, and explains why they match.

> **Prototype/data note:** The supplied dataset is synthetic educational data, not a live campus booking system. “No conflict found” means no overlap was detected in the records supplied; it does not guarantee real-world availability. The fit score is a rule-based heuristic, not an ML probability.

## Problem and target users

Choosing a room requires checking multiple constraints together: capacity, equipment, accessibility, and whether a class or recorded event overlaps with the requested time. Manual checking can be slow and makes rooms difficult to compare consistently.

**Target users**
- Students and study groups
- Club and event coordinators
- Faculty and campus administrators

## Key features

- Search by date, start time, duration, and required capacity.
- Optional mandatory requirements for projector, computers, accessibility, and minimum power outlets.
- Filter out rooms that fail mandatory requirements.
- Check recurring class schedules and date-specific event records for detected conflicts.
- Rank remaining rooms using a transparent, rule-based fit score.
- Show room details and explanations for recommendations.
- Display descriptive charts based on the supplied dataset.
- Provide interactive API documentation through FastAPI's `/docs` page.

## How the room recommendation works

1. **Input:** The user enters the session requirements.
2. **Filter:** Rooms that are too small or do not satisfy mandatory facilities are removed.
3. **Conflict check:** The backend checks overlapping class schedule records and date-specific event records for each candidate room.
4. **Rank:** Remaining candidates are ranked using a rule-based heuristic.
5. **Explain:** The response includes room details, a fit score, and reasons for the recommendation.

The score helps compare candidates within this prototype. It is not a probability that the room is available or that an event will succeed.

## Dataset

The project uses the four CSV files supplied for the datathon under `backend/data/`.

| File | Records | Used for |
|---|---:|---|
| `rooms.csv` | 120 | Room IDs, building, floor, type, capacity, and facilities |
| `class_schedule.csv` | 5,000 | Recurring class time, room, duration, and expected attendance records |
| `room_requests.csv` | 5,000 | Request features and status labels; demand/analytics context |
| `events.csv` | 1,800 | Room-linked events, timestamps, duration, expected attendance, and actual attendance |

**Relationships and assumptions**
- `rooms.room_id` connects room information to `class_schedule.room_id` and `events.room_id`.
- Requests do not have a guaranteed assigned room, so request records are not treated as confirmed room assignments.
- Class schedule records use weekday/time fields; event records use specific timestamps.
- The dataset is synthetic. Outputs reflect only the records supplied with the challenge.

## Machine-learning experiments

The script `backend/train_all_models.py` trains and compares five regression algorithms for the experimental target `actual_attendance` from `events.csv`:

- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor
- Extra Trees Regressor
- Gradient Boosting Regressor

The script compares models using five-fold cross-validation on the training set and evaluates the selected pipeline on held-out test data. It saves the selected pipeline and evaluation files in `backend/train_all_models.py/`.

**Recorded evaluation:** Linear Regression had the lowest cross-validation MAE (**34.274 attendees**). On the held-out test set, its MAE was **35.211**, compared with **35.443** for the baseline, an improvement of approximately **0.66%**. The test R² was **−0.0024**. This is only a marginal improvement and does not demonstrate useful attendance-prediction performance.

Therefore, the attendance model is documented as an experiment and **is not used to generate room recommendations**. The current room finder uses rule-based matching and ranking. This avoids presenting an insufficiently predictive model as reliable.

To reproduce the experiment from the `backend` directory on Windows:

```powershell
.\.venv\Scripts\python.exe train_all_models.py
```

The script generates:
- `models/best_attendance_model.joblib`
- `models/model_evaluation.json`
- `models/model_comparison.csv`

## Technology stack

- **Frontend:** React, Vite, Recharts, Lucide React
- **Backend:** Python, FastAPI, Uvicorn
- **Data processing:** Pandas, NumPy
- **ML experiments:** scikit-learn, joblib
- **Data format:** CSV

## Project structure

```text
campusspace-ai/
├── README.md
├── docs/
│   └── screenshots/
│       ├── 01-room-search-and-top-results.png
│       ├── 02-room-recommendations-details.png
│       └── 03-campus-insights-dashboard.jpeg
├── backend/
│   ├── app/
│   │   ├── analytics.py
│   │   ├── data_loader.py
│   │   ├── main.py
│   │   ├── matching_engine.py
│   │   └── schemas.py
│   ├── data/
│   │   ├── rooms.csv
│   │   ├── class_schedule.csv
│   │   ├── room_requests.csv
│   │   └── events.csv
│   ├── models/                 # Training outputs
│   ├── train_all_models.py     # ML comparison and evaluation
│   ├── requirements.txt
│   └── render.yaml
|   |__ train_all_models.py
└── frontend/
    ├── src/
    ├── .env.example
    └── package.json
```

## User Input and Website Output

### 1. User input and top recommendations

The example below uses the actual working prototype. The user requests a room for **30 people**, on **16 October 2026 at 10:00**, for **1 hour**, with a **projector required**. Computers and accessibility are not selected as mandatory requirements, and no minimum power outlet count is set.

![CampusSpace AI search form and top recommendations](docs/screenshots/01-room-search-and-top-results.png)

### 2. More recommendation results and the availability note

The result list shows room IDs, capacities, room types, fit scores, and expandable explanations. The interface also explains that availability is estimated from the supplied synthetic records and is not a live booking guarantee.

![CampusSpace AI additional room recommendations](docs/screenshots/02-room-recommendations-details.png)

### Sample output from this captured search

The interface reported **26 suitable rooms found**. These are examples visible in the screenshot; results may change when inputs change.

| Rank shown | Room | Room details | Capacity | Fit score |
|---:|---|---|---:|---:|
| 1 | `R069` | North Building · Floor 4 · Study room | 33 | 93.5 |
| 2 | `R040` | Central Building · Floor 4 · Classroom | 47 | 86.5 |
| 3 | `R015` | South Building · Floor 4 · Classroom | 61 | 79.5 |
| 4 | `R011` | West Building · Floor 1 · Classroom | 67 | 76.5 |
| 5 | `R027` | East Building · Floor 5 · Lab | 73 | 73.5 |
| 6 | `R066` | North Building · Floor 1 · Lab | 77 | 71.5 |

The explanations for `R069` state that the room has 33 seats for 30 people, no overlapping class or event was found in the supplied records for that time, and the requested projector is available. The same screenshot shows that the room also has computers and an accessibility attribute.

### 3. Campus insights dashboard

The dashboard summarizes the supplied dataset, including the distribution of room types and request demand by start hour. These charts describe the synthetic dataset and do not establish real-world campus occupancy.

![CampusSpace AI campus insights dashboard](docs/screenshots/03-campus-insights-dashboard.jpeg)

### Example API input

The frontend sends a request with the selected requirements to the backend. A representative request body is shown below; returned rooms and scores depend on the current dataset and search criteria.

```json
{
  "request_date": "2026-10-16",
  "start_hour": 10,
  "duration_hours": 1,
  "required_capacity": 30,
  "projector_required": true,
  "computers_required": false,
  "accessible_required": false,
  "power_outlets_required": 0
}
```


## Run locally on Windows

### 1. Start the backend

Open PowerShell in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000`  
Interactive API docs: `http://127.0.0.1:8000/docs`

Keep the backend terminal running.

### 2. Start the frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`). The frontend reads `VITE_API_BASE_URL`; the local default is `http://127.0.0.1:8000`. See `frontend/.env.example`.

### 3. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API information |
| `GET` | `/health` | Checks that datasets loaded |
| `GET` | `/api/rooms` | Lists room records |
| `POST` | `/api/recommend` | Returns room matches for a search request |
| `GET` | `/api/analytics` | Returns dataset summary and chart data |

The easiest way to try the endpoints is `http://127.0.0.1:8000/docs`.

A successful response includes the matching rooms and the reasons for each recommendation. Returned room numbers and scores depend on the request and supplied dataset.

## Deployment configuration

The repository includes `backend/render.yaml` for the FastAPI service. The intended setup is:

- **Backend:** Render; root directory `backend`; install `requirements.txt`; run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend:** Vercel; root directory `frontend`; set `VITE_API_BASE_URL` to the deployed backend URL.
- Set the backend's `FRONTEND_ORIGIN` environment variable to the deployed frontend origin.

Describe deployment as complete only after the public frontend and backend have been deployed and tested. The project can currently be run locally using the instructions above.

## Limitations and next steps

- Dataset contents are synthetic and may not reflect real campus bookings.
- A conflict cannot be detected if it is absent from the supplied records.
- The fit score is a heuristic, not a trained model probability.
- The attendance prediction model currently does not meaningfully beat its baseline and is not used by the room recommendation engine.

**Next steps:** test conflict logic with edge cases, add automated tests, validate with realistic campus data, and revisit ML when a predictive target and features demonstrate reliable value.
