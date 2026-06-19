"""Bot uchun maxsus internal endpointlar."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.client import Client
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderOut
from app.schemas.client import ClientCreate, ClientOut
from app.core.deps import verify_internal_key
from app.services.order_service import generate_order_no
from app.services.audit_service import log_action
from app.models.order import OrderDetail
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter(prefix="/orders/internal", tags=["bot-internal"])


class BotOrderDetailCreate(BaseModel):
    furniture_type: str
    height_mm: int
    width_mm: int
    depth_mm: int
    holes: Optional[str] = None
    cuts: Optional[str] = None
    material: str
    color: Optional[str] = None
    notes: Optional[str] = None


class BotOrderCreate(BaseModel):
    client_id: int
    deadline: Optional[date] = None
    detail: BotOrderDetailCreate
    telegram_id: int


@router.post("/create")
def bot_create_order(
    data: BotOrderCreate,
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = db.query(User).filter(User.telegram_id == data.telegram_id, User.is_active == True).first()
    if not user or user.role not in [UserRole.admin, UserRole.manager]:
        raise HTTPException(status_code=403, detail="Buyurtma faqat menejer/admin kirita oladi")
    client = db.query(Client).filter(Client.id == data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    order_no = generate_order_no(db)
    order = Order(
        order_no=order_no,
        client_id=data.client_id,
        deadline=data.deadline,
        created_by=user.id,
    )
    db.add(order)
    db.flush()
    detail = OrderDetail(order_id=order.id, **data.detail.model_dump())
    db.add(detail)
    db.commit()
    db.refresh(order)
    log_action(db, "bot_create_order", user_id=user.id, entity_type="order", entity_id=order.id, details=order_no)
    return {"order_no": order.order_no, "order_id": order.id}
