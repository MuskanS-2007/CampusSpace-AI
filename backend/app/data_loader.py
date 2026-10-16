from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

FILES = {
    "rooms": "rooms.csv",
    "schedules": "class_schedule.csv",
    "requests": "room_requests.csv",
    "events": "events.csv",
}
EXPECTED_COLUMNS = {
    "rooms": {"room_id", "building", "floor", "room_type", "capacity", "projector", "computers", "accessible", "power_outlets"},
    "schedules": {"schedule_id", "room_id", "course_code", "weekday", "start_hour", "duration_hours", "expected_attendance", "department"},
    "requests": {"request_id", "request_date", "start_hour", "duration_hours", "required_capacity", "projector_required", "computers_required", "purpose", "status"},
    "events": {"event_id", "room_id", "event_type", "start_time", "duration_hours", "expected_attendance", "actual_attendance"},
}

def load_dataset(key: str) -> pd.DataFrame:
    if key not in FILES:
        raise ValueError(f"Unknown dataset key: {key}")
    path = DATA_DIR / FILES[key]
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Keep the supplied CSV files in backend/data/.")
    frame = pd.read_csv(path)
    missing = EXPECTED_COLUMNS[key] - set(frame.columns)
    if missing:
        raise ValueError(f"{FILES[key]} missing required columns: {sorted(missing)}")
    return frame

def load_all_data() -> dict[str, pd.DataFrame]:
    return {key: load_dataset(key) for key in FILES}

if __name__ == "__main__":
    for key, frame in load_all_data().items():
        print(f"{FILES[key]}: {len(frame):,} rows × {len(frame.columns)} columns")
        print(f"  missing cells: {int(frame.isna().sum().sum())}; duplicate rows: {int(frame.duplicated().sum())}")
