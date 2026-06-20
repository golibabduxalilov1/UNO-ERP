from datetime import datetime
from sqlalchemy.orm import Session
from app.models.order import Order, OrderStatus


STATUS_FLOW = {
    OrderStatus.new: [OrderStatus.cutting, OrderStatus.cancelled],
    OrderStatus.cutting: [OrderStatus.drilling, OrderStatus.cancelled],
    OrderStatus.drilling: [OrderStatus.assembling, OrderStatus.cancelled],
    OrderStatus.assembling: [OrderStatus.pending_nachalnik, OrderStatus.cancelled],
    OrderStatus.pending_nachalnik: [OrderStatus.ready, OrderStatus.cancelled],
    OrderStatus.ready: [OrderStatus.delivered, OrderStatus.cancelled],
    OrderStatus.delivered: [],
    OrderStatus.cancelled: [],
}


def generate_order_no(db: Session) -> str:
    year = datetime.utcnow().year
    last_order = (
        db.query(Order)
        .filter(Order.order_no.like(f"MBL-{year}-%"))
        .order_by(Order.id.desc())
        .first()
    )
    if last_order:
        last_num = int(last_order.order_no.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"MBL-{year}-{new_num:04d}"


def can_transition(current: OrderStatus, target: OrderStatus) -> bool:
    return target in STATUS_FLOW.get(current, [])
