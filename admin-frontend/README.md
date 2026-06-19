# Mebel Sex — Admin Frontend

Vue.js 3 + Vite + Pinia + TailwindCSS asosidagi admin panel.

## Talab

- Node.js 18+ (https://nodejs.org)

## Ishga tushirish

```bash
cd admin-frontend

# Paketlarni o'rnatish
npm install

# .env sozlash
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000

# Development serverni ishga tushirish
npm run dev
# http://localhost:5173 da ochiladi

# Production build
npm run build
# dist/ papkasiga quriladi, istalgan statik server orqali joylashtiriladi
```

## Kirish ma'lumotlari

Backend ishga tushganda avtomatik admin yaratiladi:
- Login: `admin` (backend `.env` da `FIRST_ADMIN_LOGIN`)
- Parol: `admin123` (backend `.env` da `FIRST_ADMIN_PASSWORD`)

## Sahifalar

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
