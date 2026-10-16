import os
from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .data_loader import load_all_data
from .schemas import RoomSearchRequest
from .matching_engine import recommend_rooms
from .analytics import build_analytics

app = FastAPI(title="CampusSpace AI API", version="0.1.0", description="Explainable campus room recommendations using supplied synthetic data.")
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").rstrip("/")
app.add_middleware(CORSMiddleware, allow_origins=[frontend_origin, "http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

try:
    DATA = load_all_data()
except Exception as exc:
    DATA = None
    DATA_ERROR = str(exc)
else:
    DATA_ERROR = None

@app.get("/")
def root():
    return {"name": "CampusSpace AI API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    if DATA is None:
        return JSONResponse(status_code=503, content={"status": "error", "message": DATA_ERROR})
    return {"status": "ok", "datasets_loaded": list(DATA.keys())}

def require_data():
    if DATA is None:
        raise HTTPException(status_code=503, detail=f"Dataset loading failed: {DATA_ERROR}")

@app.get("/api/rooms")
def list_rooms():
    require_data()
    return DATA["rooms"].sort_values("room_id").to_dict(orient="records")

@app.post("/api/recommend")
def recommend(payload: RoomSearchRequest):
    require_data()
    try:
        result = recommend_rooms(DATA, payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not process request: {exc}") from exc
    return result

@app.get("/api/analytics")
def analytics():
    require_data()
    return build_analytics(DATA)
