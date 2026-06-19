from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.main import manager_main_kb, cancel_kb, material_kb, skip_kb
from states import OrderCreateStates, OrderSearchStates
import api_client
from api_client import APIError

router = Router()

ORDER_STATUSES = {
    "new": "🆕 Yangi",
    "cutting": "✂️ Kesishda",
    "drilling": "🔩 Teshishda",
    "assembling": "🔧 Yig'ishda",
    "quality_check": "🔍 Sifat nazoratida",
    "ready": "✅ Tayyor",
    "delivered": "🚚 Yetkazildi",
    "cancelled": "❌ Bekor qilingan",
}


@router.message(F.text == "📋 Barcha buyurtmalar")
async def all_orders(message: Message):
    try:
        orders = await api_client.get("/orders/internal/list")
        if not orders:
            await message.answer("📭 Buyurtmalar yo'q.")
            return
        lines = ["📋 <b>So'nggi buyurtmalar:</b>\n"]
        for o in orders[:20]:
            status = ORDER_STATUSES.get(o.get("status", ""), o.get("status", ""))
            client = o.get("client", {}) or {}
            lines.append(f"• <b>{o['order_no']}</b> — {client.get('name', '?')} — {status}")
        await message.answer("\n".join(lines), parse_mode="HTML")
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.message(F.text == "🔍 Buyurtma tarixi")
async def order_history_start(message: Message, state: FSMContext):
    await state.set_state(OrderSearchStates.waiting_order_no)
    await message.answer(
        "Buyurtma raqamini kiriting (masalan: MBL-2024-0001):",
        reply_markup=cancel_kb(),
    )


@router.message(OrderSearchStates.waiting_order_no)
async def order_history_search(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=manager_main_kb())
        return
    order_no = message.text.strip().upper()
    try:
        order = await api_client.get(f"/orders/internal/by-no/{order_no}")
        await state.clear()
        detail = order.get("detail") or {}
        client = order.get("client") or {}
        creator = order.get("creator") or {}
        stages = order.get("stages") or []
        status = ORDER_STATUSES.get(order.get("status", ""), order.get("status", ""))
        lines = [
            f"📦 <b>{order['order_no']}</b>",
            f"Mijoz: {client.get('name', '?')} ({client.get('phone', '?')})",
            f"Status: {status}",
            f"Yaratdi: {creator.get('full_name', '?')}",
            f"Mebel: {detail.get('furniture_type', '?')}",
            f"O'lcham: {detail.get('height_mm')}x{detail.get('width_mm')}x{detail.get('depth_mm')} mm",
            f"Material: {detail.get('material', '?')}",
            f"\n<b>Bosqichlar tarixi:</b>",
        ]
        STAGE_LABELS = {"cutting": "Kesish", "drilling": "Teshish", "assembling": "Yig'ish", "quality_check": "Sifat"}
        for s in stages:
            worker = s.get("worker") or {}
            stage_label = STAGE_LABELS.get(s.get("stage", ""), s.get("stage", ""))
            lines.append(
                f"• {stage_label}: {worker.get('full_name', '?')} — {s.get('status', '')} "
                f"({s.get('started_at', '?')[:16] if s.get('started_at') else '?'})"
            )
        await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=manager_main_kb())
    except APIError as e:
        await message.answer(f"⚠️ {e}")
        await state.clear()
        await message.answer("Asosiy menyu:", reply_markup=manager_main_kb())


# ===== Yangi buyurtma kiritish (FSM) =====

@router.message(F.text == "➕ Yangi buyurtma")
async def new_order_start(message: Message, state: FSMContext):
    await state.set_state(OrderCreateStates.waiting_client_phone)
    await state.update_data(order_data={})
    await message.answer(
        "📋 <b>Yangi buyurtma kiritish</b>\n\nMijozning telefon raqamini kiriting (+998XXXXXXXXX):",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(OrderCreateStates.waiting_client_phone)
async def order_client_phone(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    phone = message.text.strip()
    try:
        clients = await api_client.get("/clients/internal/list")
        existing = next((c for c in clients if c.get("phone") == phone), None)
        data = await state.get_data()
        order_data = data.get("order_data", {})
        if existing:
            order_data["client_id"] = existing["id"]
            order_data["client_name"] = existing["name"]
            await state.update_data(order_data=order_data)
            await state.set_state(OrderCreateStates.waiting_furniture_type)
            await message.answer(
                f"✅ Mijoz topildi: <b>{existing['name']}</b>\n\nMebel turini kiriting (shkaf, stol, stul, divan...):",
                reply_markup=cancel_kb(),
                parse_mode="HTML",
            )
        else:
            order_data["client_phone"] = phone
            await state.update_data(order_data=order_data)
            await state.set_state(OrderCreateStates.waiting_client_name)
            await message.answer(
                "Yangi mijoz. Ismini kiriting:",
                reply_markup=cancel_kb(),
            )
    except APIError as e:
        await message.answer(f"⚠️ {e}")


@router.message(OrderCreateStates.waiting_client_name)
async def order_client_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["client_name_new"] = message.text.strip()
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_client_address)
    await message.answer("Mijoz manzilit kiriting (ixtiyoriy):", reply_markup=skip_kb())


@router.message(OrderCreateStates.waiting_client_address)
async def order_client_address(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["client_address"] = message.text.strip() if message.text != "⏭ O'tkazib yuborish" else None
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_furniture_type)
    await message.answer("Mebel turini kiriting (shkaf, stol, stul, divan...):", reply_markup=cancel_kb())


@router.callback_query(F.data == "skip")
async def skip_field(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    data = await state.get_data()
    order_data = data.get("order_data", {})
    if current == OrderCreateStates.waiting_client_address:
        order_data["client_address"] = None
        await state.update_data(order_data=order_data)
        await state.set_state(OrderCreateStates.waiting_furniture_type)
        await callback.message.answer("Mebel turini kiriting:", reply_markup=cancel_kb())
    elif current == OrderCreateStates.waiting_color:
        order_data["color"] = None
        await state.update_data(order_data=order_data)
        await state.set_state(OrderCreateStates.waiting_holes)
        await callback.message.answer("Teshish joylari (ixtiyoriy):", reply_markup=skip_kb())
    elif current == OrderCreateStates.waiting_holes:
        order_data["holes"] = None
        await state.update_data(order_data=order_data)
        await state.set_state(OrderCreateStates.waiting_cuts)
        await callback.message.answer("Qo'shimcha kesish tafsilotlari (ixtiyoriy):", reply_markup=skip_kb())
    elif current == OrderCreateStates.waiting_cuts:
        order_data["cuts"] = None
        await state.update_data(order_data=order_data)
        await state.set_state(OrderCreateStates.waiting_notes)
        await callback.message.answer("Qo'shimcha izoh (ixtiyoriy):", reply_markup=skip_kb())
    elif current == OrderCreateStates.waiting_notes:
        order_data["notes"] = None
        await state.update_data(order_data=order_data)
        await state.set_state(OrderCreateStates.waiting_deadline)
        await callback.message.answer("Muddat (YYYY-MM-DD formatida, ixtiyoriy):", reply_markup=skip_kb())
    elif current == OrderCreateStates.waiting_deadline:
        order_data["deadline"] = None
        await state.update_data(order_data=order_data)
        await _show_confirm(callback.message, state)
    await callback.answer()


@router.message(OrderCreateStates.waiting_furniture_type)
async def order_furniture_type(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["furniture_type"] = message.text.strip()
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_height)
    await message.answer("Bo'yi (mm):", reply_markup=cancel_kb())


@router.message(OrderCreateStates.waiting_height)
async def order_height(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting (mm da):")
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["height_mm"] = int(message.text)
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_width)
    await message.answer("Eni (mm):")


@router.message(OrderCreateStates.waiting_width)
async def order_width(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting (mm da):")
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["width_mm"] = int(message.text)
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_depth)
    await message.answer("Chuqurligi (mm):")


@router.message(OrderCreateStates.waiting_depth)
async def order_depth(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting (mm da):")
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["depth_mm"] = int(message.text)
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_material)
    await message.answer("Materialini tanlang:", reply_markup=material_kb())


@router.callback_query(F.data.startswith("material:"))
async def select_material(callback: CallbackQuery, state: FSMContext):
    mat = callback.data.split(":")[1]
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["material"] = mat
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_color)
    await callback.message.answer(f"Material: {mat}\n\nRangini kiriting (ixtiyoriy):", reply_markup=skip_kb())
    await callback.answer()


@router.message(OrderCreateStates.waiting_color)
async def order_color(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["color"] = message.text.strip()
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_holes)
    await message.answer("Teshish joylari tavsifi (ixtiyoriy):", reply_markup=skip_kb())


@router.message(OrderCreateStates.waiting_holes)
async def order_holes(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["holes"] = message.text.strip()
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_cuts)
    await message.answer("Qo'shimcha kesish tafsilotlari (ixtiyoriy):", reply_markup=skip_kb())


@router.message(OrderCreateStates.waiting_cuts)
async def order_cuts(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["cuts"] = message.text.strip()
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_notes)
    await message.answer("Qo'shimcha izoh (ixtiyoriy):", reply_markup=skip_kb())


@router.message(OrderCreateStates.waiting_notes)
async def order_notes(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    order_data["notes"] = message.text.strip()
    await state.update_data(order_data=order_data)
    await state.set_state(OrderCreateStates.waiting_deadline)
    await message.answer("Muddat (YYYY-MM-DD formatida, ixtiyoriy):", reply_markup=skip_kb())


@router.message(OrderCreateStates.waiting_deadline)
async def order_deadline(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await _cancel(message, state)
        return
    data = await state.get_data()
    order_data = data.get("order_data", {})
    if message.text and message.text != "⏭ O'tkazib yuborish":
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", message.text.strip()):
            await message.answer("⚠️ Format: YYYY-MM-DD (masalan: 2024-12-31)")
            return
        order_data["deadline"] = message.text.strip()
    else:
        order_data["deadline"] = None
    await state.update_data(order_data=order_data)
    await _show_confirm(message, state)


async def _show_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get("order_data", {})
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data="confirm_order")
    builder.button(text="❌ Bekor qilish", callback_data="cancel_order")
    builder.adjust(2)
    await state.set_state(OrderCreateStates.confirm)
    await message.answer(
        f"📋 <b>Buyurtma ma'lumotlari:</b>\n\n"
        f"Mebel: {order_data.get('furniture_type', '?')}\n"
        f"O'lcham: {order_data.get('height_mm')}x{order_data.get('width_mm')}x{order_data.get('depth_mm')} mm\n"
        f"Material: {order_data.get('material', '?')}\n"
        f"Rang: {order_data.get('color') or 'Belgilanmagan'}\n"
        f"Muddat: {order_data.get('deadline') or 'Belgilanmagan'}\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get("order_data", {})
    tid = callback.from_user.id
    try:
        # Yangi mijoz yaratish kerak bo'lsa
        client_id = order_data.get("client_id")
        if not client_id:
            client_phone = order_data.get("client_phone", "")
            try:
                new_client = await api_client.post("/clients/internal/list", json={
                    "name": order_data.get("client_name_new", "Noma'lum"),
                    "phone": client_phone,
                    "address": order_data.get("client_address"),
                })
                client_id = new_client["id"]
            except Exception:
                await callback.message.answer("⚠️ Mijoz yaratishda xatolik. Adminpaneldan qo'shing.")
                await state.clear()
                return

        # Buyurtma yaratish
        order = await api_client.post("/orders/internal/create", json={
            "client_id": client_id,
            "deadline": order_data.get("deadline"),
            "detail": {
                "furniture_type": order_data.get("furniture_type"),
                "height_mm": order_data.get("height_mm"),
                "width_mm": order_data.get("width_mm"),
                "depth_mm": order_data.get("depth_mm"),
                "material": order_data.get("material"),
                "color": order_data.get("color"),
                "holes": order_data.get("holes"),
                "cuts": order_data.get("cuts"),
                "notes": order_data.get("notes"),
            },
            "telegram_id": tid,
        })
        await state.clear()
        await callback.message.edit_text(
            f"✅ <b>Buyurtma yaratildi!</b>\n\nRaqam: <b>{order['order_no']}</b>",
            parse_mode="HTML",
        )
        await callback.message.answer("Asosiy menyu:", reply_markup=manager_main_kb())
    except APIError as e:
        await callback.answer(f"⚠️ {e}", show_alert=True)
    await callback.answer()


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma kiritish bekor qilindi.")
    await callback.message.answer("Asosiy menyu:", reply_markup=manager_main_kb())
    await callback.answer()


async def _cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=manager_main_kb())
