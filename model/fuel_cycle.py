from pydantic import BaseModel
from datetime import datetime

class FuelCycleEfficiency(BaseModel):
    id: int
    imei: str
    distance: float
    fuel: float
    fuel_efficiency: float
    timestamp_first: datetime
    timestamp_last: datetime
    created_at: datetime
    updated_at: datetime

class FuelCycleCreate(BaseModel):
    imei: str
    distance: float
    fuel: float
    fuel_efficiency: float
    timestamp_first: datetime
    timestamp_last: datetime

