# UNO — Mebel Ishlab Chiqarish Boshqaruv Tizimi

Mebel sexlari uchun to'liq boshqaruv tizimi: buyurtmalarni kuzatish, ishchilar rollarini boshqarish, Telegram bot integratsiyasi va admin panel.

---

## Arxitektura

```
UNO/
├── backend/          # FastAPI + PostgreSQL (REST API)
├── bot/              # Telegram bot (aiogram 3.x)
└── admin-frontend/   # Admin panel (Vue.js 3 + Vite)
```

| Qism | Texnologiya | Port |
|---|---|---|
| Backend API | FastAPI + PostgreSQL + Alembic | 8000 |
| Telegram Bot | aiogram 3.x | — |
| Admin Panel | Vue.js 3 + Vite + Pinia + TailwindCSS | 5173 |

---

## Ishchilar rollari

| Rol | Tavsif |
|---|---|
| `admin` | To'liq huquq, tizim sozlamalari |
| `director` | Umumiy nazorat, hisobotlar |
| `nachalnik` | Sex boshlig'i, bosqichlarni tasdiqlash |
| `brigadir` | Guruh rahbari |
| `operator` | Buyurtma holati yangilash |
| `cutter` | Kesish bosqichi |
| `driller` | Teshish bosqichi |
| `driver` | Yetkazib berish |

---

## Buyurtma bosqichlari

```
new → cutting → drilling → assembling → pending_nachalnik → ready → delivered
                                                                    ↘ cancelled
```

---

## Ishga tushirish

### 1. Backend

```bash
cd backend

# Virtual muhit
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Muhit o'zgaruvchilari
cp .env.example .env
# .env faylni oching: DATABASE_URL, SECRET_KEY, INTERNAL_API_KEY ni to'ldiring

# Ma'lumotlar bazasi migratsiyasi
alembic upgrade head

# Serverni ishga tushirish
uvicorn app.main:app --reload --port 8000
```

PostgreSQL bazasini oldindan yarating:

```sql
CREATE DATABASE mebel_db;
CREATE USER mebel_user WITH PASSWORD 'mebel_pass';
GRANT ALL PRIVILEGES ON DATABASE mebel_db TO mebel_user;
```

### 2. Telegram Bot

```bash
cd bot

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# BOT_TOKEN va INTERNAL_API_KEY ni to'ldiring
# INTERNAL_API_KEY backend/.env dagi bilan bir xil bo'lishi kerak!

python bot.py
```

### 3. Admin Panel

```bash
cd admin-frontend

npm install

cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000

npm run dev
# http://localhost:5173
```

---

## Birinchi kirish

Backend ishga tushganda `.env` dagi `FIRST_ADMIN_LOGIN` / `FIRST_ADMIN_PASSWORD` bilan avtomatik admin yaratiladi.

Sukut bo'yicha: `admin` / `admin123` (ishga tushirishdan oldin `.env` da o'zgartiring).

---

## Admin panel sahifalari

| URL | Tavsif |
|---|---|
| `/` | Dashboard — statistika va grafik |
| `/orders` | Buyurtmalar ro'yxati (filtr, qidiruv) |
| `/orders/new` | Yangi buyurtma kiritish |
| `/orders/:id` | Buyurtma tafsiloti + timeline |
| `/users` | Ishchilarni boshqarish |
| `/clients` | Mijozlar ro'yxati |
| `/reports` | Oylik hisobot, kechikkan buyurtmalar |
| `/complaint` | Shikoyat tekshiruvi (order_no bo'yicha) |

---

## API hujjatlar

Backend ishga tushgandan so'ng:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Muhit o'zgaruvchilari

### backend/.env

| Parametr | Tavsif |
|---|---|
| `DATABASE_URL` | `postgresql://user:pass@localhost/mebel_db` |
| `SECRET_KEY` | JWT uchun maxfiy kalit (32+ belgi) |
| `INTERNAL_API_KEY` | Bot ↔ Backend aloqa kaliti |
| `BOT_TOKEN` | Telegram bot tokeni (xabarnoma uchun) |
| `FIRST_ADMIN_LOGIN` | Birinchi admin logini |
| `FIRST_ADMIN_PASSWORD` | Birinchi admin paroli |

### bot/.env

| Parametr | Tavsif |
|---|---|
| `BOT_TOKEN` | @BotFather dan olingan token |
| `BACKEND_URL` | `http://localhost:8000` |
| `INTERNAL_API_KEY` | Backend bilan bir xil kalit |

### admin-frontend/.env

| Parametr | Tavsif |
|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` |

---

## Talablar

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
