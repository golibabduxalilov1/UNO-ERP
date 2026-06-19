# Mebel Sex — Telegram Bot

aiogram 3.x asosidagi Telegram bot. Barcha 8 rol uchun interfeys.

## Oldindan talab

- Telegram Bot Token — @BotFather dan oling: `/newbot`
- Backend ishlaydigan bo'lishi kerak (`http://localhost:8000`)

## Ishga tushirish

```bash
cd bot

# Virtual muhit
python -m venv venv

# Aktivlashtirish
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Paketlar
pip install -r requirements.txt

# .env sozlash
cp .env.example .env
# BOT_TOKEN va INTERNAL_API_KEY ni to'ldiring
# INTERNAL_API_KEY backend/.env dagi bilan bir xil bo'lishi kerak!

# Botni ishga tushirish
python bot.py
```

## Bot oqimi

1. Ishchi `/start` bosadi
2. Tizim Telegram ID bo'yicha foydalanuvchini topadi
3. Roliga mos menyu ko'rsatiladi
4. Barcha so'rovlar backend API orqali bajariladi

## Ishchilarni qo'shish

Admin panelda (Vue.js) "Ishchilar" bo'limida yangi ishchi qo'shing:
- To'liq ismi
- Telegram ID (ishchi @userinfobot dan bilib olishi mumkin)
- Rol

## .env parametrlar

```
BOT_TOKEN=123456789:ABCdef...
BACKEND_URL=http://localhost:8000
INTERNAL_API_KEY=same-as-backend
```
