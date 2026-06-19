from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, clients, orders, stages, deliveries, reports, bot_internal, clients_internal
from app.database import engine, SessionLocal, Base
from app import models  # noqa: F401 — registers all ORM models with Base

app = FastAPI(
    title="Mebel Sex Boshqaruv Tizimi",
    description="Mebel ishlab chiqarish sexini raqamli boshqarish API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clients.router)
app.include_router(orders.router)
app.include_router(stages.router)
app.include_router(deliveries.router)
app.include_router(reports.router)
app.include_router(bot_internal.router)
app.include_router(clients_internal.router)


@app.on_event("startup")
def startup_event():
    # Jadvallar mavjud bo'lmasa avtomatik yaratish (alembic o'rniga)
    Base.metadata.create_all(bind=engine)
    _create_default_admin()


def _create_default_admin():
    from app.config import settings
    from app.models.user import User, UserRole
    from app.core.security import hash_password, verify_password
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.login == settings.FIRST_ADMIN_LOGIN).first()
        if not existing:
            admin = User(
                telegram_id=0,
                full_name="Administrator",
                login=settings.FIRST_ADMIN_LOGIN,
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                role=UserRole.admin,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"[startup] Admin yaratildi: login={settings.FIRST_ADMIN_LOGIN}")
        else:
            # Parol .env bilan mos kelmasa — yangilash
            needs_update = False
            if not existing.hashed_password:
                needs_update = True
            else:
                try:
                    if not verify_password(settings.FIRST_ADMIN_PASSWORD, existing.hashed_password):
                        needs_update = True
                except Exception:
                    needs_update = True

            if needs_update or not existing.is_active:
                existing.hashed_password = hash_password(settings.FIRST_ADMIN_PASSWORD)
                existing.is_active = True
                db.commit()
                print(f"[startup] Admin paroli yangilandi: login={settings.FIRST_ADMIN_LOGIN}")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "mebel-backend"}
