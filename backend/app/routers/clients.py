from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut
from app.core.deps import require_roles, verify_internal_key

router = APIRouter(prefix="/clients", tags=["clients"])

STAFF_ROLES = [UserRole.admin, UserRole.manager, UserRole.nachalnik, UserRole.director]


@router.get("", response_model=List[ClientOut])
def list_clients(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(STAFF_ROLES)),
):
    q = db.query(Client)
    if search:
        q = q.filter(
            Client.name.ilike(f"%{search}%") | Client.phone.ilike(f"%{search}%")
        )
    return q.order_by(Client.name).all()


@router.post("", response_model=ClientOut)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles([UserRole.admin, UserRole.manager])),
):
    existing = db.query(Client).filter(Client.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan")
    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(STAFF_ROLES)),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    return client


@router.patch("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles([UserRole.admin, UserRole.manager])),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles([UserRole.admin, UserRole.manager])),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    from app.models.order import Order
    has_orders = db.query(Order).filter(Order.client_id == client_id).first()
    if has_orders:
        raise HTTPException(status_code=400, detail="Bu mijozning buyurtmalari mavjud, o'chirib bo'lmaydi")
    db.delete(client)
    db.commit()
    return {"message": "Mijoz o'chirildi"}


@router.get("/internal/list", response_model=List[ClientOut])
def list_clients_internal(
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    return db.query(Client).order_by(Client.name).all()
