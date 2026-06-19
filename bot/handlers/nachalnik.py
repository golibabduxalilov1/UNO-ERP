from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.main import confirm_reject_kb, cancel_kb, nachalnik_main_kb
from states import NachalnikRejectStates
import api_client
from api_client import APIError

router = Router()

STAGE_LABELS = {
    "cutting": "Kesish",
    "drilling": "Teshish",
    "assembling": "Yig'ish/Montaj",
    "quality_check": "Sifat nazorati",
}


@router.message(F.text == "✅ Brigadir tasdiqlaganlari")
async def pending_nachalnik(message: Message):
    tid = message.from_user.id
    try:
        stages = await api_client.get("/stages/pending-nachalnik", params={"telegram_id": tid})
        if not stages:
            await message.answer("📭 Hozirda tasdiq kutayotgan ish yo'q.")
            return
        for s in stages:
            worker_name = s.get("worker", {}).get("full_name", "Noma'lum") if s.get("worker") else "Noma'lum"
            brigadir_name = s.get("brigadir", {}).get("full_name", "Noma'lum") if s.get("brigadir") else "Noma'lum"
            stage_label = STAGE_LABELS.get(s.get("stage", ""), s.get("stage", ""))
            await message.answer(
                f"🔔 <b>Nachalnik tasdiq #{s['id']}</b>\n"
                f"Ishchi: {worker_name}\n"
                f"Brigadir: {brigadir_name}\n"
                f"Buyurtma: #{s['order_id']}\n"
                f"Bosqich: {stage_label}\n"
                f"Boshlangan: {s.get('started_at', 'N/A')}\n"
                f"Yakunlangan: {s.get('finished_at', 'N/A')}",
                reply_markup=confirm_reject_kb(s["id"], "nachalnik"),
                parse_mode="HTML",
            )
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.callback_query(F.data.startswith("nachalnik_confirm:"))
async def cb_nachalnik_confirm(callback: CallbackQuery):
    stage_id = int(callback.data.split(":")[1])
    tid = callback.from_user.id
    try:
        await api_client.post(
            f"/stages/{stage_id}/nachalnik-confirm",
            params={"telegram_id": tid},
        )
        await callback.message.edit_text(
            f"✅ Bosqich #{stage_id} nachalnik tomonidan tasdiqlandi!",
            parse_mode="HTML",
        )
        await callback.answer("Tasdiqlandi!")
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)


@router.callback_query(F.data.startswith("nachalnik_reject:"))
async def cb_nachalnik_reject_start(callback: CallbackQuery, state: FSMContext):
    stage_id = int(callback.data.split(":")[1])
    await state.set_state(NachalnikRejectStates.waiting_reason)
    await state.update_data(stage_id=stage_id)
    await callback.message.answer(
        f"❌ Rad etish sababini yozing (bosqich #{stage_id}):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(NachalnikRejectStates.waiting_reason)
async def nachalnik_reject_reason(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=nachalnik_main_kb())
        return
    data = await state.get_data()
    stage_id = data["stage_id"]
    tid = message.from_user.id
    try:
        await api_client.post(
            f"/stages/{stage_id}/nachalnik-reject",
            json={"reject_reason": message.text},
            params={"telegram_id": tid},
        )
        await state.clear()
        await message.answer(
            f"❌ Bosqich #{stage_id} rad etildi.\nSabab: {message.text}",
            reply_markup=nachalnik_main_kb(),
        )
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.message(F.text == "📊 Oylik hisobot")
async def monthly_report(message: Message):
    tid = message.from_user.id
    from datetime import datetime
    now = datetime.now()
    try:
        user = await api_client.get(f"/users/by-telegram/{tid}")
        data = await api_client.get("/reports/monthly", params={"year": now.year, "month": now.month})
        if not data:
            await message.answer("📭 Bu oy uchun hisobot ma'lumotlari yo'q.")
            return
        lines = [f"📊 <b>{now.year}-{now.month:02d} oy hisoboti</b>\n"]
        for worker in data:
            lines.append(f"👤 {worker['full_name']} — {worker['total_count']} ta bosqich")
        await message.answer("\n".join(lines), parse_mode="HTML")
    except APIError as e:
        await message.answer(f"⚠️ {e}")
