from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Union
from datetime import datetime
from model.report_data import FuelHour

class IncomingCommand(Enum):
    GET_RECENT_HOUR, DELETE_RECENT_HOUR = range(2)

class RequestPacket(BaseModel):
    command: IncomingCommand
    payload: Optional[dict] = None

class ResponsePacketRecentReportHour(BaseModel):
    command: IncomingCommand
    status: int
    message: str
    payload: Optional[List[dict]] = None 