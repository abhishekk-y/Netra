from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional
from datetime import datetime

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class TimeRange(BaseModel):
    start_time: datetime
    end_time: datetime

class FilterParams(BaseModel):
    field: str
    operator: str  # eq, ne, gt, lt, in, contains
    value: str

class SortParams(BaseModel):
    field: str
    order: str = Field("asc", pattern="^(asc|desc)$")
