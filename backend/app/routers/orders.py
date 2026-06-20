from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderDetail, OrderStatus
from app.models.client import Client
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut, OrderListOut
from app.core.deps import require_roles, verify_internal_key
from app.services.order_service import generate_order_no, can_transition
from app.services.audit_service import log_action

router = APIRouter(prefix="/orders", tags=["orders"])

MANAGER_ROLES = [UserRole.admin]
VIEW_ROLES = [UserRole.admin, UserRole.nachalnik, UserRole.director, UserRole.brigadir]


@router.post("", response_model=OrderOut)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(MANAGER_ROLES)),
):
    client = db.query(Client).filter(Client.id == data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    order_no = generate_order_no(db)
    order = Order(
        order_no=order_no,
        client_id=data.client_id,
        deadline=data.deadline,
        created_by=current_user.id,
    )
    db.add(order)
    db.flush()
    detail = OrderDetail(order_id=order.id, **data.detail.model_dump())
    db.add(detail)
    db.commit()
    db.refresh(order)
    log_action(db, "create_order", user_id=current_user.id, entity_type="order", entity_id=order.id, details=order_no)
    return _load_order(db, order.id)


@router.get("", response_model=List[OrderListOut])
def list_orders(
    status: Optional[OrderStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    client_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(VIEW_ROLES)),
):
    from app.models.stage import OrderStage
    q = db.query(Order).options(joinedload(Order.client), joinedload(Order.stages))
    if status:
        q = q.filter(Order.status == status)
    if from_date:
        q = q.filter(Order.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        q = q.filter(Order.created_at <= datetime.combine(to_date, datetime.max.time()))
    if client_id:
        q = q.filter(Order.client_id == client_id)
    if search:
        q = q.join(Client, isouter=True).filter(
            Order.order_no.ilike(f"%{search}%") | Client.name.ilike(f"%{search}%")
        )
    return q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/internal/list", response_model=List[OrderListOut])
def list_orders_internal(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    q = db.query(Order).options(joinedload(Order.client))
    if status:
        q = q.filter(Order.status == status)
    return q.order_by(Order.created_at.desc()).limit(100).all()


@router.get("/internal/pending-nachalnik")
def pending_nachalnik_orders(
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    from app.models.stage import OrderStage
    from app.models.user import UserRole
    user = db.query(User).filter(User.telegram_id == telegram_id, User.is_active == True).first()
    if not user or user.role != UserRole.nachalnik:
        raise HTTPException(status_code=403, detail="Faqat nachalnik uchun")
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.client),
            joinedload(Order.detail),
            joinedload(Order.stages).joinedload(OrderStage.worker),
            joinedload(Order.stages).joinedload(OrderStage.brigadir),
        )
        .filter(Order.status == OrderStatus.pending_nachalnik)
        .order_by(Order.updated_at.asc())
        .all()
    )
    result = []
    for o in orders:
        stages_info = []
        for s in (o.stages or []):
            stages_info.append({
                "stage": s.stage,
                "worker_name": s.worker.full_name if s.worker else None,
                "started_at": str(s.started_at) if s.started_at else None,
                "finished_at": str(s.finished_at) if s.finished_at else None,
                "brigadir_name": s.brigadir.full_name if s.brigadir else None,
                "brigadir_confirmed_at": str(s.brigadir_confirmed_at) if s.brigadir_confirmed_at else None,
                "status": s.status,
            })
        d = o.detail
        result.append({
            "order_id": o.id,
            "order_no": o.order_no,
            "client_name": o.client.name if o.client else "",
            "deadline": str(o.deadline) if o.deadline else None,
            "furniture_type": d.furniture_type if d else "",
            "height_mm": d.height_mm if d else None,
            "width_mm": d.width_mm if d else None,
            "depth_mm": d.depth_mm if d else None,
            "material": d.material if d else "",
            "color": d.color if d else None,
            "notes": d.notes if d else None,
            "stages": stages_info,
        })
    return result


@router.post("/internal/{order_id}/nachalnik-confirm")
def nachalnik_confirm_order(
    order_id: int,
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    from app.models.user import UserRole
    user = db.query(User).filter(User.telegram_id == telegram_id, User.is_active == True).first()
    if not user or user.role != UserRole.nachalnik:
        raise HTTPException(status_code=403, detail="Faqat nachalnik tasdiqlashi mumkin")
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.status == OrderStatus.pending_nachalnik,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi yoki noto'g'ri holat")
    order.nachalnik_id = user.id
    order.nachalnik_confirmed_at = datetime.utcnow()
    order.status = OrderStatus.ready
    order.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, "nachalnik_confirm_order", user_id=user.id, entity_type="order", entity_id=order_id)
    return {"message": "Tasdiqlandi! Buyurtma haydovchiga yuborildi.", "order_no": order.order_no}


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(VIEW_ROLES)),
):
    order = _load_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return order


@router.get("/by-no/{order_no}", response_model=OrderOut)
def get_order_by_no(
    order_no: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(VIEW_ROLES)),
):
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return _load_order(db, order.id)


@router.get("/internal/by-no/{order_no}", response_model=OrderOut)
def get_order_by_no_internal(
    order_no: str,
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return _load_order(db, order.id)


@router.patch("/{order_id}", response_model=OrderOut)
def update_order(
    order_id: int,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(MANAGER_ROLES)),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    if data.status and not can_transition(order.status, data.status):
        raise HTTPException(status_code=400, detail=f"'{order.status}' dan '{data.status}' ga o'tish mumkin emas")
    if data.status:
        order.status = data.status
        if data.status == OrderStatus.cancelled:
            from app.models.stage import OrderStage, StageStatus
            db.query(OrderStage).filter(
                OrderStage.order_id == order_id,
                OrderStage.status.in_([StageStatus.in_progress, StageStatus.pending_brigadir])
            ).update({"status": StageStatus.rejected}, synchronize_session=False)
    if data.deadline is not None:
        order.deadline = data.deadline
    detail_fields = ['furniture_type', 'height_mm', 'width_mm', 'depth_mm', 'material', 'color', 'holes', 'cuts', 'notes']
    detail_data = {f: getattr(data, f) for f in detail_fields if getattr(data, f) is not None}
    if detail_data:
        detail = db.query(OrderDetail).filter(OrderDetail.order_id == order_id).first()
        if detail:
            for k, v in detail_data.items():
                setattr(detail, k, v)
    order.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, "update_order", user_id=current_user.id, entity_type="order", entity_id=order.id, details=f"status: {data.status}")
    return _load_order(db, order.id)


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.admin])),
):
    from app.models.stage import OrderStage
    from app.models.delivery import Delivery
    from app.models.audit import AuditLog

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    if order.status not in [OrderStatus.new, OrderStatus.cancelled]:
        raise HTTPException(status_code=400, detail="Faqat yangi yoki bekor qilingan buyurtmani o'chirish mumkin")
    order_no = order.order_no
    db.query(OrderStage).filter(OrderStage.order_id == order_id).delete()
    db.query(Delivery).filter(Delivery.order_id == order_id).delete()
    db.query(OrderDetail).filter(OrderDetail.order_id == order_id).delete()
    db.query(AuditLog).filter(AuditLog.entity_type == "order", AuditLog.entity_id == order_id).delete()
    db.delete(order)
    log_action(db, "delete_order", user_id=current_user.id, entity_type="order", entity_id=order_id, details=order_no)
    db.commit()
    return {"message": "Buyurtma o'chirildi"}


def _load_order(db: Session, order_id: int):
    return (
        db.query(Order)
        .options(
            joinedload(Order.client),
            joinedload(Order.creator),
            joinedload(Order.detail),
            joinedload(Order.stages),
        )
        .filter(Order.id == order_id)
        .first()
    )
