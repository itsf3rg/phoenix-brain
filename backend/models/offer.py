from pydantic import BaseModel
from typing import Optional

class RideOffer(BaseModel):
    id: str
    platform: str = "uber"
    fare: float
    pickup_miles: float
    trip_miles: float
    total_miles: float
    pickup_minutes: int
    trip_minutes: Optional[int] = None
    total_minutes: int
    is_silent: bool = False
    raw_text: Optional[str] = None
