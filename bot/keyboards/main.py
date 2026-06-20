from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def worker_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mening buyurtmalarim")],
            [KeyboardButton(text="✅ Mavjud vazifalar")],
            [KeyboardButton(text="ℹ️ Mening ma'lumotlarim")],
        ],
        resize_keyboard=True,
    )


def driver_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚚 Tayyor buyurtmalar")],
            [KeyboardButton(text="ℹ️ Mening ma'lumotlarim")],
        ],
        resize_keyboard=True,
    )


def brigadir_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏳ Tasdiq kutilayotganlar")],
            [KeyboardButton(text="ℹ️ Mening ma'lumotlarim")],
        ],
        resize_keyboard=True,
    )


def nachalnik_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Yakuniy tasdiq")],
            [KeyboardButton(text="📊 Oylik hisobot")],
            [KeyboardButton(text="ℹ️ Mening ma'lumotlarim")],
        ],
        resize_keyboard=True,
    )


def admin_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Yangi buyurtma")],
            [KeyboardButton(text="📋 Barcha buyurtmalar")],
            [KeyboardButton(text="🔍 Buyurtma tarixi")],
            [KeyboardButton(text="ℹ️ Mening ma'lumotlarim")],
        ],
        resize_keyboard=True,
    )


def order_action_kb(order_id: int, stage: str, has_active: bool, active_stage_id: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not has_active:
        builder.button(text="▶️ Boshladim", callback_data=f"start_stage:{order_id}:{stage}")
    else:
        builder.button(text="⏹ Yakunladim", callback_data=f"finish_stage:{active_stage_id}")
    builder.adjust(1)
    return builder.as_markup()


def confirm_reject_kb(stage_id: int, prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"{prefix}_confirm:{stage_id}")
    builder.button(text="❌ Rad etish", callback_data=f"{prefix}_reject:{stage_id}")
    builder.adjust(2)
    return builder.as_markup()


def delivery_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yetkazib berdim", callback_data=f"deliver:{order_id}")
    return builder.as_markup()


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


def material_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for mat in ["DSP", "MDF", "Faner", "Metall", "Shisha", "Boshqa"]:
        builder.button(text=mat, callback_data=f"material:{mat}")
    builder.adjust(3)
    return builder.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ O'tkazib yuborish", callback_data="skip")
    return builder.as_markup()
