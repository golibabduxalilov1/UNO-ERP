from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.main import nachalnik_main_kb
import api_client
from api_client import APIError

router = Router()

STAGE_LABELS = {
    "cutting": "Kesish",
    "drilling": "Teshish",
    "assembling": "Yig'ish/Montaj",
}


def _fmt_dt(val: str | None) -> str:
    if not val:
        return "N/A"
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(val.replace("Z", ""))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return val


def order_summary_text(o: dict) -> str:
    lines = [
        f"📦 <b>{o.get('order_no', '?')} — Yakuniy tasdiq</b>",
        f"👤 Mijoz: {o.get('client_name', '?')}",
        f"🪑 Mebel: <b>{o.get('furniture_type', '?')}</b>",
        f"📐 O'lcham: <b>{o.get('height_mm')}×{o.get('width_mm')}×{o.get('depth_mm')} mm</b>",
        f"🧱 Material: {o.get('material', '?')}",
    ]
    if o.get('color'):
        lines.append(f"🎨 Rang: {o['color']}")
    if o.get('notes'):
        lines.append(f"📝 Izoh: {o['notes']}")
    lines.append(f"📅 Muddat: {o.get('deadline') or 'Belgilanmagan'}")
    lines.append("")
    for s in (o.get("stages") or []):
        label = STAGE_LABELS.get(s.get("stage", ""), s.get("stage", ""))
        if s.get("status") != "confirmed":
            continue
        lines.append(
            f"✅ <b>{label}</b>\n"
            f"   Ishchi: {s.get('worker_name') or 'N/A'}\n"
            f"   Boshlangan: {_fmt_dt(s.get('started_at'))}\n"
            f"   Yakunlangan: {_fmt_dt(s.get('finished_at'))}\n"
            f"   Brigadir: {s.get('brigadir_name') or 'N/A'} ({_fmt_dt(s.get('brigadir_confirmed_at'))})"
        )
    return "\n".join(lines)


def nachalnik_confirm_kb(order_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"nachalnik_order_confirm:{order_id}")
    return builder.as_markup()


@router.message(F.text == "✅ Yakuniy tasdiq")
async def pending_nachalnik(message: Message):
    tid = message.from_user.id
    try:
        orders = await api_client.get("/orders/internal/pending-nachalnik", params={"telegram_id": tid})
        if not orders:
            await message.answer("📭 Hozirda tasdiq kutayotgan buyurtma yo'q.")
            return
        for o in orders:
            text = order_summary_text(o)
            kb = nachalnik_confirm_kb(o["order_id"])
            await message.answer(text, reply_markup=kb, parse_mode="HTML")
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.callback_query(F.data.startswith("nachalnik_order_confirm:"))
async def cb_nachalnik_order_confirm(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    tid = callback.from_user.id
    try:
        result = await api_client.post(
            f"/orders/internal/{order_id}/nachalnik-confirm",
            params={"telegram_id": tid},
        )
        await callback.message.edit_text(
            f"✅ Buyurtma #{order_id} tasdiqlandi!\n"
            f"Haydovchiga yuborildi.",
            parse_mode="HTML",
        )
        await callback.answer("Tasdiqlandi!")
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)


@router.message(F.text == "📊 Oylik hisobot")
async def monthly_report(message: Message):
    tid = message.from_user.id
    from datetime import datetime
    now = datetime.now()
    try:
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
