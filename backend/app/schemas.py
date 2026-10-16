from datetime import date
from pydantic import BaseModel, Field

class RoomSearchRequest(BaseModel):
    request_date: date
    start_hour: int = Field(ge=0, le=23)
    duration_hours: int = Field(ge=1, le=12)
    required_capacity: int = Field(ge=1, le=1000)
    projector_required: bool = False
    computers_required: bool = False
    accessible_required: bool = False
    power_outlets_required: int = Field(default=0, ge=0, le=100)

