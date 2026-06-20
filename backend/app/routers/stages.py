from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.stage import OrderStage, StageType, StageStatus
from app.schemas.stage import StageStart, StageFinish, BrigadirAction
from app.schemas.order import StageOut
from app.core.deps import verify_internal_key
from app.services.audit_service import log_action

router = APIRouter(prefix="/stages", tags=["stages"])

STAGE_SEQUENCE = [StageType.cutting, StageType.drilling, StageType.assembling]

ACTIVE_STATUSES = [StageStatus.in_progress, StageStatus.pending_brigadir]

WORKER_ROLES = {
    StageType.cutting: UserRole.cutter,
    StageType.drilling: UserRole.driller,
    StageType.assembling: UserRole.operator,
}

NEXT_ORDER_STATUS = {
    StageType.cutting: OrderStatus.drilling,
    StageType.drilling: OrderStatus.assembling,
    StageType.assembling: OrderStatus.pending_nachalnik,
}


def _get_user_by_telegram(telegram_id: int, db: Session) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return user


@router.get("/my", response_model=List[StageOut])
def my_stages(
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(telegram_id, db)
    stages = (
        db.query(OrderStage)
        .options(joinedload(OrderStage.order), joinedload(OrderStage.worker))
        .filter(
            OrderStage.user_id == user.id,
            OrderStage.status == StageStatus.in_progress,
        )
        .all()
    )
    return stages


@router.get("/available", response_model=List[dict])
def available_orders(
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(telegram_id, db)

    role_to_stage = {
        UserRole.cutter: StageType.cutting,
        UserRole.driller: StageType.drilling,
        UserRole.operator: StageType.assembling,
    }
    role_to_status = {
        UserRole.cutter: [OrderStatus.new, OrderStatus.cutting],
        UserRole.driller: [OrderStatus.drilling],
        UserRole.operator: [OrderStatus.assembling],
    }

    current_stage = role_to_stage.get(user.role)
    allowed_statuses = role_to_status.get(user.role, [])
    if not allowed_statuses or not current_stage:
        return []

    stage_idx = STAGE_SEQUENCE.index(current_stage) if current_stage in STAGE_SEQUENCE else -1
    prev_stage = STAGE_SEQUENCE[stage_idx - 1] if stage_idx > 0 else None

    orders = (
        db.query(Order)
        .options(joinedload(Order.client), joinedload(Order.detail))
        .filter(Order.status.in_(allowed_statuses))
        .all()
    )

    result = []
    for order in orders:
        if prev_stage:
            prev_active = (
                db.query(OrderStage)
                .filter(
                    OrderStage.order_id == order.id,
                    OrderStage.stage == prev_stage,
                    OrderStage.status.in_(ACTIVE_STATUSES),
                )
                .first()
            )
            if prev_active:
                continue

        other_active = (
            db.query(OrderStage)
            .filter(
                OrderStage.order_id == order.id,
                OrderStage.stage == current_stage,
                OrderStage.status.in_(ACTIVE_STATUSES),
                OrderStage.user_id != user.id,
            )
            .first()
        )
        if other_active:
            continue

        own_pending = (
            db.query(OrderStage)
            .filter(
                OrderStage.order_id == order.id,
                OrderStage.user_id == user.id,
                OrderStage.stage == current_stage,
                OrderStage.status == StageStatus.pending_brigadir,
            )
            .first()
        )
        if own_pending:
            continue

        active_stage = (
            db.query(OrderStage)
            .filter(
                OrderStage.order_id == order.id,
                OrderStage.user_id == user.id,
                OrderStage.stage == current_stage,
                OrderStage.status == StageStatus.in_progress,
            )
            .first()
        )

        d = order.detail
        result.append({
            "order_id": order.id,
            "order_no": order.order_no,
            "status": order.status,
            "deadline": str(order.deadline) if order.deadline else None,
            "client_name": order.client.name if order.client else "",
            "furniture_type": d.furniture_type if d else "",
            "height_mm": d.height_mm if d else None,
            "width_mm": d.width_mm if d else None,
            "depth_mm": d.depth_mm if d else None,
            "material": d.material if d else "",
            "color": d.color if d else None,
            "holes": d.holes if d else None,
            "cuts": d.cuts if d else None,
            "notes": d.notes if d else None,
            "has_active_stage": active_stage is not None,
            "active_stage_id": active_stage.id if active_stage else None,
        })
    return result


@router.post("/start", response_model=StageOut)
def start_stage(
    data: StageStart,
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(data.telegram_id, db)
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    STAGE_REQUIRED_ORDER_STATUS = {
        StageType.cutting: [OrderStatus.new, OrderStatus.cutting],
        StageType.drilling: [OrderStatus.drilling],
        StageType.assembling: [OrderStatus.assembling],
    }
    allowed_statuses = STAGE_REQUIRED_ORDER_STATUS.get(data.stage, [])
    if allowed_statuses and order.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Buyurtma bu bosqich uchun tayyor emas: oldingi bosqich hali tasdiqlanmagan",
        )

    existing = db.query(OrderStage).filter(
        OrderStage.order_id == data.order_id,
        OrderStage.stage == data.stage,
        OrderStage.status.in_(ACTIVE_STATUSES),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu bosqich allaqachon boshlangan yoki tasdiqlanishda")

    stage = OrderStage(
        order_id=data.order_id,
        user_id=user.id,
        stage=data.stage,
        started_at=datetime.utcnow(),
        status=StageStatus.in_progress,
    )
    db.add(stage)

    if data.stage == StageType.cutting and order.status == OrderStatus.new:
        order.status = OrderStatus.cutting

    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(stage)
    log_action(db, "stage_start", telegram_id=data.telegram_id, entity_type="stage", entity_id=stage.id)
    return stage


@router.post("/finish")
def finish_stage(
    data: StageFinish,
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(data.telegram_id, db)
    stage = db.query(OrderStage).filter(
        OrderStage.id == data.stage_id,
        OrderStage.user_id == user.id,
    ).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Bosqich topilmadi")
    if stage.status != StageStatus.in_progress:
        raise HTTPException(status_code=400, detail="Bu bosqich allaqachon yakunlangan yoki tasdiqlashda")
    stage.finished_at = datetime.utcnow()
    stage.status = StageStatus.pending_brigadir
    db.commit()
    log_action(db, "stage_finish", telegram_id=data.telegram_id, entity_type="stage", entity_id=stage.id)
    return {"message": "Ish brigadirga tasdiq uchun yuborildi", "stage_id": stage.id}


@router.get("/pending-brigadir", response_model=List[StageOut])
def pending_brigadir(
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(telegram_id, db)
    if user.role != UserRole.brigadir:
        raise HTTPException(status_code=403, detail="Faqat brigadir uchun")
    stages = (
        db.query(OrderStage)
        .options(joinedload(OrderStage.worker), joinedload(OrderStage.order))
        .filter(OrderStage.status == StageStatus.pending_brigadir)
        .all()
    )
    return stages


@router.post("/{stage_id}/brigadir-confirm")
def brigadir_confirm(
    stage_id: int,
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(telegram_id, db)
    if user.role != UserRole.brigadir:
        raise HTTPException(status_code=403, detail="Faqat brigadir tasdiqlashi mumkin")
    stage = db.query(OrderStage).filter(
        OrderStage.id == stage_id,
        OrderStage.status == StageStatus.pending_brigadir,
    ).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Bosqich topilmadi yoki noto'g'ri holat")

    stage.brigadir_id = user.id
    stage.brigadir_confirmed_at = datetime.utcnow()
    stage.status = StageStatus.confirmed

    order = db.query(Order).filter(Order.id == stage.order_id).first()
    next_status = NEXT_ORDER_STATUS.get(stage.stage)
    if next_status and order:
        order.status = next_status
        order.updated_at = datetime.utcnow()

    db.commit()
    log_action(db, "brigadir_confirm", user_id=user.id, entity_type="stage", entity_id=stage_id)

    if next_status == OrderStatus.pending_nachalnik:
        return {"message": "Tasdiqlandi! Barcha bosqichlar yakunlandi, nachalnikka yuborildi."}
    return {"message": "Tasdiqlandi! Keyingi bosqich ochildi."}


@router.post("/{stage_id}/brigadir-reject")
def brigadir_reject(
    stage_id: int,
    data: BrigadirAction,
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    if not data.reject_reason:
        raise HTTPException(status_code=400, detail="Rad etish sababi kiritilishi shart")
    user = _get_user_by_telegram(telegram_id, db)
    if user.role != UserRole.brigadir:
        raise HTTPException(status_code=403, detail="Faqat brigadir rad etishi mumkin")
    stage = db.query(OrderStage).filter(
        OrderStage.id == stage_id,
        OrderStage.status == StageStatus.pending_brigadir,
    ).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Bosqich topilmadi")
    stage.brigadir_id = user.id
    stage.brigadir_reject_reason = data.reject_reason
    stage.status = StageStatus.rejected
    db.commit()
    worker = db.query(User).filter(User.id == stage.user_id).first()
    log_action(db, "brigadir_reject", user_id=user.id, entity_type="stage", entity_id=stage_id, details=data.reject_reason)
    return {
        "message": "Rad etildi",
        "worker_telegram_id": worker.telegram_id if worker else None,
        "reason": data.reject_reason,
    }
