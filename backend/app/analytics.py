import pandas as pd

def build_analytics(data: dict) -> dict:
    rooms, schedules, requests, events = (data[k] for k in ("rooms", "schedules", "requests", "events"))
    room_types = rooms.groupby("room_type").size().sort_values(ascending=False)
    weekdays = schedules.groupby("weekday").size().sort_values(ascending=False)
    statuses = requests.groupby("status").size().sort_values(ascending=False)
    demand = requests.groupby("start_hour").size().sort_index()
    return {
        "summary": {
            "room_count": int(len(rooms)), "class_schedule_count": int(len(schedules)),
            "request_count": int(len(requests)), "event_count": int(len(events)),
            "average_capacity": round(float(rooms["capacity"].mean()), 1),
            "rooms_with_projector": int((rooms["projector"].astype(int) == 1).sum()),
            "rooms_with_computers": int((rooms["computers"].astype(int) == 1).sum()),
        },
        "room_types": [{"name": str(k), "value": int(v)} for k, v in room_types.items()],
        "schedule_weekdays": [{"name": str(k), "value": int(v)} for k, v in weekdays.items()],
        "request_statuses": [{"name": str(k), "value": int(v)} for k, v in statuses.items()],
        "demand_by_hour": [{"hour": int(k), "requests": int(v)} for k, v in demand.items()],
        "data_note": "All statistics describe the supplied synthetic educational dataset, not a real campus.",
    }
