from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClientCreate(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ClientOut(BaseModel):
    id: int
    name: str
    phone: str
    address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
