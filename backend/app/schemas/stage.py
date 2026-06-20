from typing import Optional
from pydantic import BaseModel
from app.models.stage import StageType


class StageStart(BaseModel):
    order_id: int
    stage: StageType
    telegram_id: int


class StageFinish(BaseModel):
    stage_id: int
    telegram_id: int


class BrigadirAction(BaseModel):
    reject_reason: Optional[str] = None
