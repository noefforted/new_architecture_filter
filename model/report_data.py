from pydantic import BaseModel
from prisma import types, models

ApiKey = models.api_key
ApiKeyCreate = types.api_keyCreateInput

Vehicle = models.vehicle
VehicleCreate = types.vehicleCreateInput

FuelCycle = models.fuel_cycle
FuelCycleCreate = types.fuel_cycleCreateInput

FuelHour = models.fuel_report_hour
FuelHourCreate = types.fuel_report_hourCreateInput

