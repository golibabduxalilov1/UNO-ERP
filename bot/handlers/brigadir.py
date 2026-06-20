from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.main import confirm_reject_kb, cancel_kb
from states import BrigadirRejectStates
import api_client
from api_client import APIError

router = Router()

STAGE_LABELS = {
    "cutting": "Kesish",
    "drilling": "Teshish",
    "assembling": "Yig'ish/Montaj",
}


@router.message(F.text == "⏳ Tasdiq kutilayotganlar")
async def pending_list(message: Message):
    tid = message.from_user.id
    try:
        stages = await api_client.get("/stages/pending-brigadir", params={"telegram_id": tid})
        if not stages:
            await message.answer("📭 Hozirda tasdiq kutayotgan ish yo'q.")
            return
        for s in stages:
            worker_name = s.get("worker", {}).get("full_name", "Noma'lum") if s.get("worker") else "Noma'lum"
            stage_label = STAGE_LABELS.get(s.get("stage", ""), s.get("stage", ""))
            duration = ""
            if s.get("started_at") and s.get("finished_at"):
                try:
                    from datetime import datetime
                    fmt = "%Y-%m-%dT%H:%M:%S.%f"
                    t1 = datetime.fromisoformat(s["started_at"].replace("Z", ""))
                    t2 = datetime.fromisoformat(s["finished_at"].replace("Z", ""))
                    secs = int((t2 - t1).total_seconds())
                    if secs < 60:
                        dur_str = f"{secs} soniya"
                    else:
                        m, sec = divmod(secs, 60)
                        dur_str = f"{m} daqiqa {sec} soniya" if sec else f"{m} daqiqa"
                    started = t1.strftime("%H:%M")
                    duration = f"\nBoshlangan: {started}\nDavomiyligi: {dur_str}"
                except Exception:
                    pass
            await message.answer(
                f"🔔 <b>Tasdiq so'rovi #{s['id']}</b>\n"
                f"Ishchi: {worker_name}\n"
                f"Buyurtma: #{s['order_id']}\n"
                f"Bosqich: {stage_label}"
                f"{duration}",
                reply_markup=confirm_reject_kb(s["id"], "brigadir"),
                parse_mode="HTML",
            )
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.callback_query(F.data.startswith("brigadir_confirm:"))
async def cb_brigadir_confirm(callback: CallbackQuery):
    stage_id = int(callback.data.split(":")[1])
    tid = callback.from_user.id
    try:
        result = await api_client.post(
            f"/stages/{stage_id}/brigadir-confirm",
            params={"telegram_id": tid},
        )
        await callback.message.edit_text(
            f"✅ Bosqich #{stage_id} tasdiqlandi!\n{result.get('message', '')}",
            parse_mode="HTML",
        )
        await callback.answer("Tasdiqlandi!")
    except APIError as e:
        await callback.answer("⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.", show_alert=True)


@router.callback_query(F.data.startswith("brigadir_reject:"))
async def cb_brigadir_reject_start(callback: CallbackQuery, state: FSMContext):
    stage_id = int(callback.data.split(":")[1])
    await state.set_state(BrigadirRejectStates.waiting_reason)
    await state.update_data(stage_id=stage_id)
    await callback.message.answer(
        f"❌ Rad etish sababini yozing (bosqich #{stage_id}):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(BrigadirRejectStates.waiting_reason)
async def cb_brigadir_reject_reason(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=__import__('keyboards.main', fromlist=['brigadir_main_kb']).brigadir_main_kb())
        return
    data = await state.get_data()
    stage_id = data["stage_id"]
    tid = message.from_user.id
    try:
        result = await api_client.post(
            f"/stages/{stage_id}/brigadir-reject",
            json={"reject_reason": message.text},
            params={"telegram_id": tid},
        )
        await state.clear()
        from keyboards.main import brigadir_main_kb
        await message.answer(
            f"❌ Bosqich #{stage_id} rad etildi.\nSabab: {message.text}",
            reply_markup=brigadir_main_kb(),
        )
    except APIError as e:
        await message.answer(f"⚠️ {e}")
