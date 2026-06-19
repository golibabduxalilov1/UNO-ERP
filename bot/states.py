from aiogram.fsm.state import State, StatesGroup


class OrderCreateStates(StatesGroup):
    waiting_client_phone = State()
    waiting_client_name = State()
    waiting_client_address = State()
    waiting_furniture_type = State()
    waiting_height = State()
    waiting_width = State()
    waiting_depth = State()
    waiting_material = State()
    waiting_color = State()
    waiting_holes = State()
    waiting_cuts = State()
    waiting_notes = State()
    waiting_deadline = State()
    confirm = State()


class BrigadirRejectStates(StatesGroup):
    waiting_reason = State()


class NachalnikRejectStates(StatesGroup):
    waiting_reason = State()


class OrderSearchStates(StatesGroup):
    waiting_order_no = State()
