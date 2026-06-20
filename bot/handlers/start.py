from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import api_client
from api_client import APIError
from keyboards.main import (
    worker_main_kb, driver_main_kb, brigadir_main_kb,
    nachalnik_main_kb, admin_main_kb
)

router = Router()

ROLE_LABELS = {
    "admin": "Administrator",
    "brigadir": "Brigadir",
    "nachalnik": "Nachalnik",
    "operator": "Stanok operatori",
    "cutter": "Kesuvchi",
    "driller": "Teshuvchi",
    "driver": "Haydovchi",
    "director": "Direktor",
}

WORKER_ROLES = {"operator", "cutter", "driller"}


def get_keyboard_for_role(role: str):
    if role in WORKER_ROLES:
        return worker_main_kb()
    if role == "driver":
        return driver_main_kb()
    if role == "brigadir":
        return brigadir_main_kb()
    if role == "nachalnik":
        return nachalnik_main_kb()
    if role in ("admin", "director"):
        return admin_main_kb()
    return worker_main_kb()


@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    try:
        user = await api_client.get(f"/users/by-telegram/{telegram_id}")
        role = user.get("role", "")
        role_label = ROLE_LABELS.get(role, role)
        kb = get_keyboard_for_role(role)
        await message.answer(
            f"👋 Xush kelibsiz, <b>{user['full_name']}</b>!\n"
            f"Sizning rolingiz: <b>{role_label}</b>\n\n"
            f"Quyidagi menyu orqali ishlashingiz mumkin:",
            reply_markup=kb,
            parse_mode="HTML",
        )
    except APIError:
        await message.answer(
            "❌ Siz tizimda ro'yxatdan o'tmagansiz.\n"
            "Administratorga murojaat qiling va Telegram ID'ingizni yuboring:\n"
            f"<code>{telegram_id}</code>",
            parse_mode="HTML",
        )


@router.message(F.text == "ℹ️ Mening ma'lumotlarim")
async def my_info(message: Message):
    telegram_id = message.from_user.id
    try:
        user = await api_client.get(f"/users/by-telegram/{telegram_id}")
        role_label = ROLE_LABELS.get(user.get("role", ""), user.get("role", ""))
        await message.answer(
            f"👤 <b>Mening ma'lumotlarim</b>\n\n"
            f"Ism: {user['full_name']}\n"
            f"Rol: {role_label}\n"
            f"Telefon: {user.get('phone') or 'Kiritilmagan'}\n"
            f"Telegram ID: <code>{telegram_id}</code>",
            parse_mode="HTML",
        )
    except APIError as e:
        await message.answer(f"⚠️ Xatolik: {e}")
