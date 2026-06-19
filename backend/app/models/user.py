import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Enum
from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    brigadir = "brigadir"
    nachalnik = "nachalnik"
    operator = "operator"
    cutter = "cutter"
    driller = "driller"
    driver = "driver"
    director = "director"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    login = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
