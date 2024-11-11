from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime
from model.report_data import FuelHourCreate

class IncomingCommand(Enum):
    GET_RECENT_HOUR = 1

class RequestPacket(BaseModel):
    command: IncomingCommand
    payload: Optional[dict] = None

class ResponsePacketRecentReportHour(BaseModel):
    command: IncomingCommand
    status: int
    message: str
    payload: Optional[FuelHourCreate] = None