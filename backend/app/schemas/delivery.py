from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DeliverRequest(BaseModel):
    order_id: int
    telegram_id: int
    notes: Optional[str] = None


class DeliveryOut(BaseModel):
    id: int
    order_id: int
    driver_id: int
    delivered_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True
