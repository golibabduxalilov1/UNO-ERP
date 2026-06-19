from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.main import delivery_kb
import api_client
from api_client import APIError

router = Router()


@router.message(F.text == "🚚 Tayyor buyurtmalar")
async def ready_orders(message: Message):
    tid = message.from_user.id
    try:
        orders = await api_client.get("/deliveries/ready", params={"telegram_id": tid})
        if not orders:
            await message.answer("📭 Hozirda yetkazilishi kerak bo'lgan buyurtma yo'q.")
            return
        for o in orders:
            await message.answer(
                f"📦 <b>{o['order_no']}</b>\n"
                f"Mijoz: {o['client_name']}\n"
                f"📱 Telefon: {o['client_phone']}\n"
                f"📍 Manzil: {o.get('client_address') or 'Kiritilmagan'}\n"
                f"Mebel: {o['furniture_type']}\n"
                f"Muddat: {o.get('deadline') or 'Belgilanmagan'}",
                reply_markup=delivery_kb(o["order_id"]),
                parse_mode="HTML",
            )
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.callback_query(F.data.startswith("deliver:"))
async def cb_deliver(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    tid = callback.from_user.id
    try:
        result = await api_client.post("/deliveries/deliver", json={
            "order_id": order_id,
            "telegram_id": tid,
        })
        await callback.message.edit_text(
            f"✅ <b>{result['order_no']}</b> buyurtmasi yetkazib berildi!\n"
            f"Vaqt qayd etildi.",
            parse_mode="HTML",
        )
        await callback.answer("Yetkazildi!")
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)
