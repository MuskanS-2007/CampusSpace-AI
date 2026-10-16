from datetime import date, datetime, timedelta
import pandas as pd

WEEKDAY_MAP = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

def _overlaps(start_a: float, end_a: float, start_b: float, end_b: float) -> bool:
    return start_a < end_b and start_b < end_a

def recommend_rooms(data: dict, request: dict) -> dict:
    rooms = data["rooms"].copy()
    schedules = data["schedules"].copy()
    events = data["events"].copy()

    req_date = request["request_date"]
    if isinstance(req_date, str):
        req_date = date.fromisoformat(req_date)
    start = int(request["start_hour"])
    duration = int(request["duration_hours"])
    end = start + duration
    required_capacity = int(request["required_capacity"])
    weekday = req_date.strftime("%a").lower()

    # First enforce hard constraints; do not rank rooms that fail them.
    candidates = rooms[rooms["capacity"] >= required_capacity].copy()
    if request.get("projector_required"):
        candidates = candidates[candidates["projector"].astype(int) == 1]
    if request.get("computers_required"):
        candidates = candidates[candidates["computers"].astype(int) == 1]
    if request.get("accessible_required"):
        candidates = candidates[candidates["accessible"].astype(int) == 1]
    outlets = int(request.get("power_outlets_required", 0))
    candidates = candidates[candidates["power_outlets"].astype(int) >= outlets]

    results = []
    for room in candidates.to_dict(orient="records"):
        room_id = room["room_id"]
        conflicts = []
        room_sched = schedules[schedules["room_id"] == room_id]
        for row in room_sched.to_dict(orient="records"):
            sched_day = str(row["weekday"]).strip().lower()[:3]
            sched_start = float(row["start_hour"])
            sched_end = sched_start + float(row["duration_hours"])
            if sched_day == weekday[:3] and _overlaps(start, end, sched_start, sched_end):
                conflicts.append({"type": "class", "description": f"{row['course_code']} ({row['weekday']} {sched_start:g}:00–{sched_end:g}:00)"})

        room_events = events[events["room_id"] == room_id].copy()
        if not room_events.empty:
            parsed = pd.to_datetime(room_events["start_time"], errors="coerce")
            for (_, row), event_dt in zip(room_events.iterrows(), parsed):
                if pd.isna(event_dt) or event_dt.date() != req_date:
                    continue
                event_start = event_dt.hour + event_dt.minute / 60
                event_end = event_start + float(row["duration_hours"])
                if _overlaps(start, end, event_start, event_end):
                    conflicts.append({"type": "event", "description": f"{row['event_type']} ({event_start:g}:00–{event_end:g}:00)"})

        if conflicts:
            continue

        # Transparent heuristic score; this is not a trained ML probability.
        spare_capacity = int(room["capacity"]) - required_capacity
        capacity_score = max(0, 30 - spare_capacity * 0.5)
        facility_score = 20
        if request.get("projector_required") and int(room["projector"]) == 1:
            facility_score += 10
        if request.get("computers_required") and int(room["computers"]) == 1:
            facility_score += 10
        if request.get("accessible_required") and int(room["accessible"]) == 1:
            facility_score += 5
        score = round(min(100, 50 + capacity_score + facility_score / 2), 1)
        reasons = [f"Capacity fits: {room['capacity']} seats for {required_capacity} people.", "No overlapping class or event was found in the supplied records for this time."]
        if int(room["projector"]) == 1:
            reasons.append("Projector available.")
        if int(room["computers"]) == 1:
            reasons.append("Computers available.")
        if int(room["accessible"]) == 1:
            reasons.append("Accessibility attribute is available.")
        results.append({
            "room_id": room_id, "building": room["building"], "floor": int(room["floor"]),
            "room_type": room["room_type"], "capacity": int(room["capacity"]),
            "projector": bool(room["projector"]), "computers": bool(room["computers"]),
            "accessible": bool(room["accessible"]), "power_outlets": int(room["power_outlets"]),
            "suitability_score": score, "reasons": reasons,
        })

    results.sort(key=lambda r: (-r["suitability_score"], r["capacity"] - required_capacity, r["room_id"]))
    return {
        "request": {**request, "request_date": req_date.isoformat(), "end_hour": end},
        "matches": results[:20], "total_matches": len(results),
        "note": "Availability is estimated from the supplied synthetic schedule/event records; it is not a live booking guarantee. Suitability score is a rule-based heuristic, not an ML probability.",
    }
