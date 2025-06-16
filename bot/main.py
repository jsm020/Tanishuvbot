import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from config import settings

# Redis FSM
storage = RedisStorage.from_url("redis://localhost:6379/0")

# Bot va Dispatcher
bot = Bot(token=settings.BOT_TOKEN, default=ParseMode.HTML)
dp = Dispatcher(storage=storage)

DJANGO_URL = "http://127.0.0.1:8000"  # Django API manzilingiz

# --- FSM holatlar ---
class RegisterStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_location = State()

# --- Start komandasi ---
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{DJANGO_URL}/api/chat/check-user/', json={"telegram_id": message.from_user.id}) as resp:
            data = await resp.json()
            if data.get("exists"):
                await show_main_menu(message)
                return

    # Agar mavjud bo‘lmasa
    await message.answer("Ismingizni kiriting:")
    await state.set_state(RegisterStates.waiting_for_name)

# --- Ism ---
@dp.message(RegisterStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]
    ], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Jinsingizni tanlang:", reply_markup=keyboard)
    await state.set_state(RegisterStates.waiting_for_gender)

# --- Jins ---
@dp.message(RegisterStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    gender = message.text
    if gender not in ["Erkak", "Ayol"]:
        return await message.answer("Faqat 'Erkak' yoki 'Ayol' deb yozing.")
    await state.update_data(gender=gender)
    await message.answer("Yoshingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterStates.waiting_for_age)

# --- Yosh ---
@dp.message(lambda m: not m.text.isdigit(), RegisterStates.waiting_for_age)
async def process_age_invalid(message: Message, state: FSMContext):
    await message.reply("Yosh raqamda bo‘lishi kerak. Qayta urinib ko‘ring:")

@dp.message(lambda m: m.text.isdigit(), RegisterStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Lokatsiyani yuborish", request_location=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Lokatsiyangizni yuboring:", reply_markup=keyboard)
    await state.set_state(RegisterStates.waiting_for_location)

# --- Lokatsiya ---
@dp.message(F.location, RegisterStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    data = await state.get_data()
    payload = {
        "telegram_id": message.from_user.id,
        "name": data["name"],
        "gender": data["gender"],
        "age": data["age"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "password": str(message.from_user.id)  # Demo maqsadida
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{DJANGO_URL}/api/register/", json=payload) as resp:
                if resp.status == 201:
                    await message.answer("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=ReplyKeyboardRemove())
                else:
                    await message.answer("⚠️ Xatolik yuz berdi yoki allaqachon ro'yxatdan o'tgansiz.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"❗ Server bilan aloqa muvaffaqiyatsiz: {e}", reply_markup=ReplyKeyboardRemove())

    await state.clear()
    await show_main_menu(message)

# --- Asosiy menyu ---
async def show_main_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👩‍❤️‍👨 Do‘st izlash", callback_data="find_friends"),
            InlineKeyboardButton(text="💬 Mening suhbatlarim", callback_data="my_chats")
        ],
        [
            InlineKeyboardButton(text="📂 Do‘stlarim", callback_data="my_friends"),
            InlineKeyboardButton(text="🚨 Shikoyat qilish", callback_data="report")
        ]
    ])
    await message.answer("Asosiy menyu:", reply_markup=keyboard)

# --- Botni ishga tushurish ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
