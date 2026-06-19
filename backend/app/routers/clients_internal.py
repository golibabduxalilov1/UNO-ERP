"""Bot uchun mijoz yaratish."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.client import Client
from app.schemas.client import ClientOut
from app.core.deps import verify_internal_key
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/clients/internal", tags=["bot-internal"])


class BotClientCreate(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None


@router.post("/create", response_model=ClientOut)
def bot_create_client(
    data: BotClientCreate,
    db: Session = Depends(get_db),
    _key: str = Depends(verify_internal_key),
):
    existing = db.query(Client).filter(Client.phone == data.phone).first()
    if existing:
        return existing
    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client
