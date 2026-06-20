import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class OrderStatus(str, enum.Enum):
    new = "new"
    cutting = "cutting"
    drilling = "drilling"
    assembling = "assembling"
    pending_nachalnik = "pending_nachalnik"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(20), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.new, nullable=False)
    deadline = Column(Date, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    nachalnik_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    nachalnik_confirmed_at = Column(DateTime, nullable=True)

    client = relationship("Client", backref="orders")
    creator = relationship("User", foreign_keys=[created_by], backref="created_orders")
    nachalnik = relationship("User", foreign_keys=[nachalnik_id])
    detail = relationship("OrderDetail", back_populates="order", uselist=False)
    stages = relationship("OrderStage", back_populates="order", order_by="OrderStage.id")

    @property
    def active_stage_status(self):
        for s in (self.stages or []):
            if s.status == 'pending_brigadir':
                return 'pending_brigadir'
        return None


class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False, index=True)
    furniture_type = Column(String(100), nullable=False)
    height_mm = Column(Integer, nullable=False)
    width_mm = Column(Integer, nullable=False)
    depth_mm = Column(Integer, nullable=False)
    holes = Column(Text, nullable=True)
    cuts = Column(Text, nullable=True)
    material = Column(String(100), nullable=False)
    color = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    order = relationship("Order", back_populates="detail")
