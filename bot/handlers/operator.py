from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import api_client
from api_client import APIError
from keyboards.main import order_action_kb

router = Router()

STAGE_LABELS = {
    "cutting": "Kesish",
    "drilling": "Teshish",
    "assembling": "Yig'ish/Montaj",
    "quality_check": "Sifat nazorati",
}

ROLE_TO_STAGE = {
    "cutter": "cutting",
    "driller": "drilling",
    "operator": "assembling",
    "manager": "quality_check",
    "nachalnik": "quality_check",
}


@router.message(F.text == "✅ Mavjud vazifalar")
async def available_tasks(message: Message):
    tid = message.from_user.id
    try:
        user = await api_client.get(f"/users/by-telegram/{tid}")
        role = user.get("role", "")
        stage = ROLE_TO_STAGE.get(role)
        if not stage:
            await message.answer("❌ Sizning rolingiz uchun vazifalar mavjud emas.")
            return
        orders = await api_client.get("/stages/available", params={"telegram_id": tid})
        if not orders:
            await message.answer("📭 Hozircha sizga mos vazifa yo'q.")
            return
        for o in orders:
            detail = (
                f"📦 <b>{o['order_no']}</b>\n"
                f"Mijoz: {o['client_name']}\n"
                f"Mebel: {o['furniture_type']} ({o['material']})\n"
                f"Status: {o['status']}\n"
                f"Muddat: {o.get('deadline') or 'Belgilanmagan'}"
            )
            kb = order_action_kb(
                o["order_id"], stage,
                o.get("has_active_stage", False),
                o.get("active_stage_id")
            )
            await message.answer(detail, reply_markup=kb, parse_mode="HTML")
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.message(F.text == "📋 Mening buyurtmalarim")
async def my_active_stages(message: Message):
    tid = message.from_user.id
    try:
        stages = await api_client.get("/stages/my", params={"telegram_id": tid})
        if not stages:
            await message.answer("📭 Hozirda faol bosqichlaringiz yo'q.")
            return
        for s in stages:
            stage_label = STAGE_LABELS.get(s.get("stage", ""), s.get("stage", ""))
            started = s.get("started_at")
            if started:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(started.replace("Z", ""))
                    started = dt.strftime("%d.%m.%Y %H:%M")
                except Exception:
                    pass
            builder = InlineKeyboardBuilder()
            builder.button(text="⏹ Yakunladim", callback_data=f"finish_stage:{s['id']}")
            await message.answer(
                f"🔧 <b>Bosqich #{s['id']}</b>\n"
                f"Buyurtma: #{s['order_id']}\n"
                f"Turi: {stage_label}\n"
                f"Boshlangan: {started or 'N/A'}",
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.callback_query(F.data.startswith("start_stage:"))
async def cb_start_stage(callback: CallbackQuery):
    _, order_id, stage = callback.data.split(":")
    tid = callback.from_user.id
    try:
        result = await api_client.post("/stages/start", json={
            "order_id": int(order_id),
            "stage": stage,
            "telegram_id": tid,
        })
        stage_label = STAGE_LABELS.get(stage, stage)
        builder = InlineKeyboardBuilder()
        builder.button(text="⏹ Yakunladim", callback_data=f"finish_stage:{result['id']}")
        await callback.message.edit_text(
            f"▶️ <b>{stage_label}</b> bosqichi boshlandi!\n"
            f"Buyurtma: #{order_id}\n"
            f"Ishni tugatganda tugmani bosing.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
        await callback.answer("Boshlandi!")
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)


@router.callback_query(F.data.startswith("finish_stage:"))
async def cb_finish_stage(callback: CallbackQuery):
    stage_id = int(callback.data.split(":")[1])
    tid = callback.from_user.id
    try:
        await api_client.post("/stages/finish", json={
            "stage_id": stage_id,
            "telegram_id": tid,
        })
        await callback.message.edit_text(
            f"✅ Bosqich #{stage_id} yakunlandi!\n"
            f"Ish brigadirga tasdiq uchun yuborildi.",
            parse_mode="HTML",
        )
        await callback.answer("Yakunlandi!")
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)
