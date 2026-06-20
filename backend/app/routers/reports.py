from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, extract
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.stage import OrderStage, StageStatus
from app.models.delivery import Delivery
from app.core.deps import require_roles

router = APIRouter(prefix="/reports", tags=["reports"])

REPORT_ROLES = [UserRole.admin, UserRole.nachalnik, UserRole.director]


@router.get("/monthly")
def monthly_report(
    year: int = Query(...),
    month: int = Query(...),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(REPORT_ROLES)),
):
    q = (
        db.query(OrderStage, User)
        .join(User, OrderStage.user_id == User.id)
        .filter(
            OrderStage.status == StageStatus.confirmed,
            OrderStage.brigadir_confirmed_at != None,
            extract("year", OrderStage.brigadir_confirmed_at) == year,
            extract("month", OrderStage.brigadir_confirmed_at) == month,
        )
    )
    if user_id:
        q = q.filter(OrderStage.user_id == user_id)
    rows = q.all()
    result = {}
    for stage, user in rows:
        key = user.id
        if key not in result:
            result[key] = {
                "user_id": user.id,
                "full_name": user.full_name,
                "role": user.role,
                "stages": [],
                "total_count": 0,
            }
        duration = None
        if stage.started_at and stage.finished_at:
            duration = int((stage.finished_at - stage.started_at).total_seconds() / 60)
        result[key]["stages"].append({
            "stage_id": stage.id,
            "order_id": stage.order_id,
            "stage": stage.stage,
            "started_at": stage.started_at,
            "finished_at": stage.finished_at,
            "duration_minutes": duration,
        })
        result[key]["total_count"] += 1
    return list(result.values())


@router.get("/orders-status")
def orders_status_report(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(REPORT_ROLES)),
):
    q = db.query(Order)
    if from_date:
        q = q.filter(Order.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        q = q.filter(Order.created_at <= datetime.combine(to_date, datetime.max.time()))
    orders = q.all()
    by_status = {}
    for o in orders:
        s = o.status.value
        by_status[s] = by_status.get(s, 0) + 1
    return {
        "total": len(orders),
        "by_status": by_status,
        "period": {"from": str(from_date), "to": str(to_date)},
    }


@router.get("/delayed")
def delayed_orders(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(REPORT_ROLES)),
):
    today = date.today()
    orders = (
        db.query(Order)
        .options(joinedload(Order.client))
        .filter(
            Order.deadline < today,
            Order.status.notin_([OrderStatus.delivered, OrderStatus.cancelled]),
        )
        .order_by(Order.deadline)
        .all()
    )
    result = []
    for o in orders:
        result.append({
            "order_id": o.id,
            "order_no": o.order_no,
            "status": o.status,
            "deadline": str(o.deadline),
            "days_delayed": (today - o.deadline).days,
            "client_name": o.client.name if o.client else "",
            "client_phone": o.client.phone if o.client else "",
        })
    return result


@router.get("/order-history/{order_no}")
def order_history(
    order_no: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(REPORT_ROLES)),
):
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    stages = (
        db.query(OrderStage)
        .options(joinedload(OrderStage.worker), joinedload(OrderStage.brigadir))
        .filter(OrderStage.order_id == order.id)
        .order_by(OrderStage.started_at)
        .all()
    )
    delivery = db.query(Delivery).options(joinedload(Delivery.driver)).filter(Delivery.order_id == order.id).first()
    creator = db.query(User).filter(User.id == order.created_by).first()
    stage_list = []
    for s in stages:
        stage_list.append({
            "stage": s.stage,
            "worker_name": s.worker.full_name if s.worker else None,
            "started_at": s.started_at,
            "finished_at": s.finished_at,
            "status": s.status,
            "brigadir_name": s.brigadir.full_name if s.brigadir else None,
            "brigadir_confirmed_at": s.brigadir_confirmed_at,
            "brigadir_reject_reason": s.brigadir_reject_reason,
        })
    nachalnik_user = db.query(User).filter(User.id == order.nachalnik_id).first() if order.nachalnik_id else None
    return {
        "order_no": order.order_no,
        "status": order.status,
        "created_at": order.created_at,
        "created_by": creator.full_name if creator else None,
        "deadline": str(order.deadline) if order.deadline else None,
        "nachalnik_name": nachalnik_user.full_name if nachalnik_user else None,
        "nachalnik_confirmed_at": order.nachalnik_confirmed_at,
        "stages": stage_list,
        "delivery": {
            "driver_name": delivery.driver.full_name if delivery and delivery.driver else None,
            "delivered_at": delivery.delivered_at if delivery else None,
            "notes": delivery.notes if delivery else None,
        } if delivery else None,
    }


@router.get("/dashboard")
def dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(REPORT_ROLES)),
):
    from datetime import timedelta
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    # Current month bounds
    month_start = datetime.combine(today.replace(day=1), datetime.min.time())
    prev_month_end = month_start
    prev_month_start = datetime.combine(
        (today.replace(day=1) - timedelta(days=1)).replace(day=1),
        datetime.min.time()
    )

    # Yesterday for delayed comparison
    yesterday = today - timedelta(days=1)

    total_orders = db.query(func.count(Order.id)).scalar()
    today_new = db.query(func.count(Order.id)).filter(Order.created_at >= today_start).scalar()
    in_progress = db.query(func.count(Order.id)).filter(
        Order.status.notin_([OrderStatus.delivered, OrderStatus.cancelled, OrderStatus.new])
    ).scalar()
    delayed = db.query(func.count(Order.id)).filter(
        Order.deadline < today,
        Order.status.notin_([OrderStatus.delivered, OrderStatus.cancelled])
    ).scalar()
    delivered_today = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.delivered,
        Order.updated_at >= today_start
    ).scalar()

    # Trend: this month new orders vs prev month new orders
    this_month_new = db.query(func.count(Order.id)).filter(
        Order.created_at >= month_start
    ).scalar()
    prev_month_new = db.query(func.count(Order.id)).filter(
        Order.created_at >= prev_month_start,
        Order.created_at < prev_month_end,
    ).scalar()
    if prev_month_new and prev_month_new > 0:
        total_orders_trend = round((this_month_new - prev_month_new) / prev_month_new * 100, 1)
    else:
        total_orders_trend = None

    # Trend: delayed today vs delayed yesterday
    delayed_yesterday = db.query(func.count(Order.id)).filter(
        Order.deadline < yesterday,
        Order.status.notin_([OrderStatus.delivered, OrderStatus.cancelled])
    ).scalar()
    if delayed_yesterday and delayed_yesterday > 0:
        delayed_trend = round((delayed - delayed_yesterday) / delayed_yesterday * 100, 1)
    else:
        delayed_trend = None

    by_status_rows = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    by_status = {row[0].value: row[1] for row in by_status_rows}
    return {
        "total_orders": total_orders,
        "today_new": today_new,
        "in_progress": in_progress,
        "delayed": delayed,
        "delivered_today": delivered_today,
        "by_status": by_status,
        "total_orders_trend": total_orders_trend,
        "delayed_trend": delayed_trend,
    }
