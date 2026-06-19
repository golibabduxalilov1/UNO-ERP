import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class StageType(str, enum.Enum):
    cutting = "cutting"
    drilling = "drilling"
    assembling = "assembling"
    quality_check = "quality_check"


class StageStatus(str, enum.Enum):
    in_progress = "in_progress"
    pending_brigadir = "pending_brigadir"
    pending_nachalnik = "pending_nachalnik"
    confirmed = "confirmed"
    rejected = "rejected"


class OrderStage(Base):
    __tablename__ = "order_stages"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stage = Column(Enum(StageType), nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    status = Column(Enum(StageStatus), default=StageStatus.in_progress)

    brigadir_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    brigadir_confirmed_at = Column(DateTime, nullable=True)
    brigadir_reject_reason = Column(Text, nullable=True)

    nachalnik_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    nachalnik_confirmed_at = Column(DateTime, nullable=True)
    nachalnik_reject_reason = Column(Text, nullable=True)

    order = relationship("Order", back_populates="stages")
    worker = relationship("User", foreign_keys=[user_id])
    brigadir = relationship("User", foreign_keys=[brigadir_id])
    nachalnik = relationship("User", foreign_keys=[nachalnik_id])
