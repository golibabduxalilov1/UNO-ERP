from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.stage import OrderStage, StageType, StageStatus
from app.schemas.stage import StageStart, StageFinish, BrigadirAction, NachalnikAction
from app.schemas.order import StageOut
from app.core.deps import verify_internal_key
from app.services.audit_service import log_action
from app.services.notify_service import send_telegram_message

router = APIRouter(prefix="/stages", tags=["stages"])

STAGE_TO_ORDER_STATUS = {
    StageType.cutting: OrderStatus.cutting,
    StageType.drilling: OrderStatus.drilling,
    StageType.assembling: OrderStatus.assembling,
    StageType.quality_check: OrderStatus.quality_check,
}

WORKER_ROLES = {
    StageType.cutting: UserRole.cutter,
    StageType.drilling: UserRole.driller,
    StageType.assembling: UserRole.operator,
    StageType.quality_check: UserRole.manager,
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
            OrderStage.status.in_([StageStatus.in_progress])
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
        UserRole.cutter: [StageType.cutting],
        UserRole.driller: [StageType.drilling],
        UserRole.operator: [StageType.assembling],
        UserRole.manager: [StageType.quality_check],
        UserRole.nachalnik: [StageType.quality_check],
    }
    allowed_stages = role_to_stage.get(user.role, [])
    role_to_status = {
        UserRole.cutter: [OrderStatus.new, OrderStatus.cutting],
        UserRole.driller: [OrderStatus.cutting, OrderStatus.drilling],
        UserRole.operator: [OrderStatus.drilling, OrderStatus.assembling],
        UserRole.manager: [OrderStatus.assembling, OrderStatus.quality_check],
        UserRole.nachalnik: [OrderStatus.assembling, OrderStatus.quality_check],
    }
    allowed_statuses = role_to_status.get(user.role, [])
    if not allowed_statuses:
        return []
    orders = (
        db.query(Order)
        .options(joinedload(Order.client), joinedload(Order.detail))
        .filter(Order.status.in_(allowed_statuses))
        .all()
    )
    result = []
    for order in orders:
        active_stage = (
            db.query(OrderStage)
            .filter(
                OrderStage.order_id == order.id,
                OrderStage.user_id == user.id,
                OrderStage.status == StageStatus.in_progress,
            )
            .first()
        )
        result.append({
            "order_id": order.id,
            "order_no": order.order_no,
            "status": order.status,
            "deadline": str(order.deadline) if order.deadline else None,
            "client_name": order.client.name if order.client else "",
            "furniture_type": order.detail.furniture_type if order.detail else "",
            "material": order.detail.material if order.detail else "",
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
    existing = db.query(OrderStage).filter(
        OrderStage.order_id == data.order_id,
        OrderStage.user_id == user.id,
        OrderStage.stage == data.stage,
        OrderStage.status == StageStatus.in_progress,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu bosqich allaqachon boshlangan")
    stage = OrderStage(
        order_id=data.order_id,
        user_id=user.id,
        stage=data.stage,
        started_at=datetime.utcnow(),
        status=StageStatus.in_progress,
    )
    db.add(stage)
    if order.status == OrderStatus.new and data.stage == StageType.cutting:
        order.status = OrderStatus.cutting
    elif data.stage == StageType.drilling and order.status == OrderStatus.cutting:
        order.status = OrderStatus.drilling
    elif data.stage == StageType.assembling and order.status == OrderStatus.drilling:
        order.status = OrderStatus.assembling
    elif data.stage == StageType.quality_check and order.status == OrderStatus.assembling:
        order.status = OrderStatus.quality_check
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
    brigadirs = db.query(User).filter(User.role == UserRole.brigadir, User.is_active == True).all()
    for br in brigadirs:
        import asyncio
        asyncio.create_task(send_telegram_message(
            br.telegram_id,
            f"⚠️ Yangi tasdiqlash so'rovi!\n"
            f"Ishchi: {user.full_name}\n"
            f"Bosqich: {stage.stage}\n"
            f"Buyurtma: #{stage.order_id}"
        )) if False else None
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
    stage = db.query(OrderStage).filter(OrderStage.id == stage_id, OrderStage.status == StageStatus.pending_brigadir).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Bosqich topilmadi yoki noto'g'ri holat")
    stage.brigadir_id = user.id
    stage.brigadir_confirmed_at = datetime.utcnow()
    stage.status = StageStatus.pending_nachalnik
    db.commit()
    log_action(db, "brigadir_confirm", user_id=user.id, entity_type="stage", entity_id=stage_id)
    return {"message": "Tasdiqlandi, nachalnikka yuborildi"}


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
    stage = db.query(OrderStage).filter(OrderStage.id == stage_id, OrderStage.status == StageStatus.pending_brigadir).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Bosqich topilmadi")
    stage.brigadir_id = user.id
    stage.brigadir_reject_reason = data.reject_reason
    stage.status = StageStatus.rejected
    db.commit()
    worker = db.query(User).filter(User.id == stage.user_id).first()
    log_action(db, "brigadir_reject", user_id=user.id, entity_type="stage", entity_id=stage_id, details=data.reject_reason)
    return {"message": "Rad etildi", "worker_telegram_id": worker.telegram_id if worker else None, "reason": data.reject_reason}


@router.get("/pending-nachalnik", response_model=List[StageOut])
def pending_nachalnik(
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(telegram_id, db)
    if user.role != UserRole.nachalnik:
        raise HTTPException(status_code=403, detail="Faqat nachalnik uchun")
    stages = (
        db.query(OrderStage)
        .options(joinedload(OrderStage.worker), joinedload(OrderStage.brigadir), joinedload(OrderStage.order))
        .filter(OrderStage.status == StageStatus.pending_nachalnik)
        .all()
    )
    return stages


@router.post("/{stage_id}/nachalnik-confirm")
def nachalnik_confirm(
    stage_id: int,
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    user = _get_user_by_telegram(telegram_id, db)
    if user.role != UserRole.nachalnik:
        raise HTTPException(status_code=403, detail="Faqat nachalnik tasdiqlashi mumkin")
    stage = db.query(OrderStage).filter(OrderStage.id == stage_id, OrderStage.status == StageStatus.pending_nachalnik).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Bosqich topilmadi")
    stage.nachalnik_id = user.id
    stage.nachalnik_confirmed_at = datetime.utcnow()
    stage.status = StageStatus.confirmed
    db.commit()
    log_action(db, "nachalnik_confirm", user_id=user.id, entity_type="stage", entity_id=stage_id)
    order = db.query(Order).filter(Order.id == stage.order_id).first()
    next_status_map = {
        StageType.cutting: OrderStatus.drilling,
        StageType.drilling: OrderStatus.assembling,
        StageType.assembling: OrderStatus.quality_check,
        StageType.quality_check: OrderStatus.ready,
    }
    next_status = next_status_map.get(stage.stage)
    if next_status and order:
        order.status = next_status
        order.updated_at = datetime.utcnow()
        db.commit()
    return {"message": "Tasdiqlandi"}


@router.post("/{stage_id}/nachalnik-reject")
def nachalnik_reject(
    stage_id: int,
    data: NachalnikAction,
    telegram_id: int = Query(...),
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    if not data.reject_reason:
        raise HTTPException(status_code=400, detail="Rad etish sababi kiritilishi shart")
    user = _get_user_by_telegram(telegram_id, db)
    if user.role != UserRole.nachalnik:
        raise HTTPException(status_code=403, detail="Faqat nachalnik rad etishi mumkin")
    stage = db.query(OrderStage).filter(OrderStage.id == stage_id, OrderStage.status == StageStatus.pending_nachalnik).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Bosqich topilmadi")
    stage.nachalnik_id = user.id
    stage.nachalnik_reject_reason = data.reject_reason
    stage.status = StageStatus.rejected
    db.commit()
    brigadir = db.query(User).filter(User.id == stage.brigadir_id).first()
    log_action(db, "nachalnik_reject", user_id=user.id, entity_type="stage", entity_id=stage_id, details=data.reject_reason)
    return {"message": "Rad etildi", "brigadir_telegram_id": brigadir.telegram_id if brigadir else None, "reason": data.reject_reason}
