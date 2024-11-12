from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Union

class IncomingCommand(Enum):
    GET_RECENT_HOUR, DELETE_RECENT_HOUR = range(2)

class ResponseStatus(Enum):
    SUCCESS, BAD_REQUEST = range(2)

class RequestPacket(BaseModel):
    command: IncomingCommand
    payload: Optional[dict] = None

class ResponsePacketRecentReportHour(BaseModel):
    command: IncomingCommand
    status: ResponseStatus
    message: str
    payload: Optional[List[dict]] = None 