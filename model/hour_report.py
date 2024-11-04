from pydantic import BaseModel
from datetime import datetime

class FuelHourEfficiency(BaseModel):
    id: int
    imei: str
    distance: float
    fuel: float
    fuel_efficiency: float
    operating_time: int
    timestamp: datetime
    sampling_time: int
    created_at: datetime
    updated_at: datetime

class FuelHourCreate(BaseModel):
    imei: str
    distance: float
    fuel: float
    fuel_efficiency: float
    operating_time: int
    timestamp: datetime
    sampling_time: int