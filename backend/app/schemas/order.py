from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel
from app.models.order import OrderStatus
from app.schemas.client import ClientOut
from app.schemas.user import UserOut


class OrderDetailCreate(BaseModel):
    furniture_type: str
    height_mm: int
    width_mm: int
    depth_mm: int
    holes: Optional[str] = None
    cuts: Optional[str] = None
    material: str
    color: Optional[str] = None
    notes: Optional[str] = None


class OrderDetailOut(BaseModel):
    id: int
    furniture_type: str
    height_mm: int
    width_mm: int
    depth_mm: int
    holes: Optional[str]
    cuts: Optional[str]
    material: str
    color: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    client_id: int
    deadline: Optional[date] = None
    detail: OrderDetailCreate


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    deadline: Optional[date] = None
    furniture_type: Optional[str] = None
    height_mm: Optional[int] = None
    width_mm: Optional[int] = None
    depth_mm: Optional[int] = None
    material: Optional[str] = None
    color: Optional[str] = None
    holes: Optional[str] = None
    cuts: Optional[str] = None
    notes: Optional[str] = None


class StageOut(BaseModel):
    id: int
    order_id: int
    user_id: int
    stage: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    status: str
    brigadir_id: Optional[int]
    brigadir_confirmed_at: Optional[datetime]
    brigadir_reject_reason: Optional[str]
    worker: Optional[UserOut] = None
    brigadir: Optional[UserOut] = None

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    order_no: str
    client_id: int
    status: OrderStatus
    deadline: Optional[date]
    created_by: int
    created_at: datetime
    updated_at: datetime
    client: Optional[ClientOut] = None
    creator: Optional[UserOut] = None
    detail: Optional[OrderDetailOut] = None
    stages: Optional[List[StageOut]] = []

    class Config:
        from_attributes = True


class OrderListOut(BaseModel):
    id: int
    order_no: str
    status: OrderStatus
    active_stage_status: Optional[str] = None
    deadline: Optional[date]
    created_at: datetime
    updated_at: datetime
    client: Optional[ClientOut] = None

    class Config:
        from_attributes = True
