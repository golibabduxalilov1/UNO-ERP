# Mebel Sex — Backend API

FastAPI asosidagi backend. Python 3.10+ talab qilinadi.

## PostgreSQL sozlash

```bash
# PostgreSQL o'rnatilgan bo'lishi kerak (https://www.postgresql.org/download/)
# Windows: PostgreSQL installer orqali o'rnating

# psql orqali baza yaratish:
psql -U postgres
CREATE DATABASE mebel_db;
CREATE USER mebel_user WITH PASSWORD 'mebel_pass';
GRANT ALL PRIVILEGES ON DATABASE mebel_db TO mebel_user;
\q
```

## Ishga tushirish

```bash
cd backend

# Virtual muhit yaratish
python -m venv venv

# Aktivlashtirish
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Paketlarni o'rnatish
pip install -r requirements.txt

# .env fayl sozlash
cp .env.example .env
# .env faylni oching va DATABASE_URL, SECRET_KEY, INTERNAL_API_KEY ni to'ldiring

# Migratsiyalarni qo'llash
alembic upgrade head

# Serverni ishga tushirish
uvicorn app.main:app --reload --port 8000
```

## Birinchi admin

Server ishga tushganda `.env` da ko'rsatilgan `FIRST_ADMIN_LOGIN` va `FIRST_ADMIN_PASSWORD` bilan
avtomatik admin yaratiladi (`telegram_id=0` bilan). Keyin admin paneldan to'liq ishchi qo'shing.

## API hujjatlar

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Muhim .env parametrlar

| Parametr | Tavsif |
|---|---|
| `DATABASE_URL` | PostgreSQL ulanish URL |
| `SECRET_KEY` | JWT uchun maxfiy kalit (32+ belgi) |
| `INTERNAL_API_KEY` | Bot bilan o'zaro aloqa kaliti |
| `BOT_TOKEN` | Telegram bot token (xabarnoma uchun) |
| `FIRST_ADMIN_LOGIN` | Birinchi admin logini |
| `FIRST_ADMIN_PASSWORD` | Birinchi admin paroli |
