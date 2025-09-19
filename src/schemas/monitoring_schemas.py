from datetime import datetime

from pydantic import BaseModel
from typing import Literal


class Interval:
    def __init__(self, start: datetime, end: datetime, x_offset: int):
        self.start: datetime = start
        self.end: datetime = end
        self.day: str = f"{self.start.day:0>2}/{self.start.month:0>2}"
        self.hour: str = f"{self.start.hour:0>2}:{self.start.minute:0>2}"
        self.x_offset: int = x_offset


GraphType = Literal["VOLUME", "LATENCY"]


class GraphInput(BaseModel):
    service_name: str
    last_hours: int
    graph_type: GraphType


class RouteGraphInput(GraphInput):
    route_name: str


class RequestInput(BaseModel):
    timestamp: datetime
    response_time: float
    response_code: str


class AddRequestInput(BaseModel):
    service_name: str
    route_name: str
    request: RequestInput


class AddServiceInput(BaseModel):
    service_name: str
    channel_id: int

