from pydantic import BaseModel
from datetime import datetime

class FuelTimescale(BaseModel):
    imei: str
    timestamp: datetime
    latitude: int
    longitude: int
    altitude: int
    heading: int
    voltage: int
    speed: int
    distance_total: float
    fuel: float
    power_status: bool
    operating_status: bool
    device_status: bool
    calculation_cycle_status: bool
    calculation_hour_status: bool
    expired_date: datetime