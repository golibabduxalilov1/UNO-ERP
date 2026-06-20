from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.delivery import Delivery
from app.schemas.delivery import DeliverRequest, DeliveryOut
from app.core.deps import require_roles, verify_internal_key
from app.services.audit_service import log_action

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("/ready")
def ready_orders(
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = db.query(User).filter(User.telegram_id == telegram_id, User.is_active == True).first()
    if not user or user.role != UserRole.driver:
        raise HTTPException(status_code=403, detail="Faqat haydovchi uchun")
    orders = (
        db.query(Order)
        .options(joinedload(Order.client), joinedload(Order.detail))
        .filter(Order.status == OrderStatus.ready)
        .all()
    )
    result = []
    for o in orders:
        result.append({
            "order_id": o.id,
            "order_no": o.order_no,
            "client_name": o.client.name if o.client else "",
            "client_address": o.client.address if o.client else "",
            "client_phone": o.client.phone if o.client else "",
            "furniture_type": o.detail.furniture_type if o.detail else "",
            "deadline": str(o.deadline) if o.deadline else None,
        })
    return result


@router.post("/deliver")
def deliver_order(
    data: DeliverRequest,
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = db.query(User).filter(User.telegram_id == data.telegram_id, User.is_active == True).first()
    if not user or user.role != UserRole.driver:
        raise HTTPException(status_code=403, detail="Faqat haydovchi yetkazib berishi mumkin")
    order = db.query(Order).filter(Order.id == data.order_id, Order.status == OrderStatus.ready).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi yoki tayyor emas")
    existing = db.query(Delivery).filter(Delivery.order_id == data.order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu buyurtma allaqachon yetkazilgan")
    delivery = Delivery(
        order_id=data.order_id,
        driver_id=user.id,
        delivered_at=datetime.utcnow(),
        notes=data.notes,
    )
    db.add(delivery)
    order.status = OrderStatus.delivered
    order.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, "deliver_order", user_id=user.id, entity_type="order", entity_id=data.order_id)
    return {"message": "Yetkazib berish qayd etildi", "order_no": order.order_no}


@router.get("", response_model=List[DeliveryOut])
def list_deliveries(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles([UserRole.admin, UserRole.nachalnik, UserRole.director])),
):
    return db.query(Delivery).order_by(Delivery.delivered_at.desc()).limit(100).all()
