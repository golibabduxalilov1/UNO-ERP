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
}

ROLE_TO_STAGE = {
    "cutter": "cutting",
    "driller": "drilling",
    "operator": "assembling",
}


def order_detail_text(o: dict, stage_label: str = "", started: str = "") -> str:
    order_no = o.get('order_no') or f"#{o.get('order_id', '?')}"
    lines = [
        f"📦 <b>{order_no} — {stage_label or ''}</b>",
        f"👤 Mijoz: {o.get('client_name', '?')}",
        f"🪑 Mebel: <b>{o.get('furniture_type', '?')}</b>",
        f"📐 O'lcham: <b>{o.get('height_mm')}×{o.get('width_mm')}×{o.get('depth_mm')} mm</b>",
        f"🧱 Material: {o.get('material', '?')}",
    ]
    if o.get('color'):
        lines.append(f"🎨 Rang: {o['color']}")
    if o.get('holes'):
        lines.append(f"🔩 Teshish joylari: {o['holes']}")
    if o.get('cuts'):
        lines.append(f"✂️ Kesish: {o['cuts']}")
    if o.get('notes'):
        lines.append(f"📝 Izoh: {o['notes']}")
    lines.append(f"📅 Muddat: {o.get('deadline') or 'Belgilanmagan'}")
    if started:
        lines.append(f"⏱ Boshlangan: {started}")
    return "\n".join(lines)


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
        stage_label = STAGE_LABELS.get(stage, stage)
        for o in orders:
            text = order_detail_text(o, stage_label)
            kb = order_action_kb(
                o["order_id"], stage,
                o.get("has_active_stage", False),
                o.get("active_stage_id")
            )
            await message.answer(text, reply_markup=kb, parse_mode="HTML")
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
        # available dan to'liq ma'lumotni olish
        try:
            all_orders = await api_client.get("/stages/available", params={"telegram_id": tid})
            orders_map = {o["order_id"]: o for o in all_orders}
        except Exception:
            orders_map = {}

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
            order_info = orders_map.get(s["order_id"])
            if order_info:
                text = (
                    f"🔧 <b>Davom etayotgan ish — {stage_label}</b>\n\n"
                    + order_detail_text(order_info, stage_label, started or "N/A")
                    + "\n\n⬇️ Ishni tugatganda tugmani bosing."
                )
            else:
                text = (
                    f"🔧 <b>Bosqich #{s['id']}</b>\n"
                    f"Buyurtma: #{s['order_id']}\n"
                    f"Turi: {stage_label}\n"
                    f"Boshlangan: {started or 'N/A'}"
                )
            await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
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

        # To'liq buyurtma ma'lumotini olish
        try:
            orders = await api_client.get("/stages/available", params={"telegram_id": tid})
            order_info = next((o for o in orders if o["order_id"] == int(order_id)), None)
        except Exception:
            order_info = None

        order_no = order_info.get('order_no', f'#{order_id}') if order_info else f'#{order_id}'

        builder = InlineKeyboardBuilder()
        builder.button(text="⏹ Yakunladim", callback_data=f"finish_stage:{result['id']}:{order_no}")

        if order_info:
            text = (
                f"▶️ <b>{stage_label} bosqichi boshlandi!</b>\n\n"
                + order_detail_text(order_info, stage_label)
                + "\n\n⬇️ Ishni tugatganda tugmani bosing."
            )
        else:
            text = (
                f"▶️ <b>{stage_label}</b> bosqichi boshlandi!\n"
                f"Buyurtma: {order_no}\n"
                f"Ishni tugatganda tugmani bosing."
            )

        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        await callback.answer("Boshlandi!")
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)


@router.callback_query(F.data.startswith("finish_stage:"))
async def cb_finish_stage(callback: CallbackQuery):
    parts    = callback.data.split(":", 2)
    stage_id = int(parts[1])
    order_no = parts[2] if len(parts) > 2 else "?"
    tid = callback.from_user.id
    try:
        await api_client.post("/stages/finish", json={
            "stage_id": stage_id,
            "telegram_id": tid,
        })
        await callback.message.edit_text(
            f"✅ <b>{order_no}</b> yakunlandi!\n"
            f"Ish brigadirga tasdiq uchun yuborildi.",
            parse_mode="HTML",
        )
        await callback.answer("Yakunlandi!")
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)
