from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiohttp import ClientSession

from config import settings
from states import RegisterStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:")
    await state.set_state(RegisterStates.waiting_for_name)

@router.message(RegisterStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="👦 O‘g‘il"), KeyboardButton(text="👧 Qiz")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Jinsingizni tanlang:", reply_markup=keyboard)
    await state.set_state(RegisterStates.waiting_for_gender)

@router.message(RegisterStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    if message.text not in ["👦 O‘g‘il", "👧 Qiz"]:
        await message.answer("Iltimos, tugmalardan birini tanlang.")
        return
    await state.update_data(gender=message.text)
    await message.answer("Yoshingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterStates.waiting_for_age)

@router.message(RegisterStates.waiting_for_age, lambda m: not m.text.isdigit())
async def process_age_invalid(message: Message, state: FSMContext):
    await message.reply("Yosh faqat raqamda bo'lishi kerak. Qayta kiriting:")

@router.message(RegisterStates.waiting_for_age, lambda m: m.text.isdigit())
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Lokatsiyangizni yuboring:", reply_markup=keyboard)
    await state.set_state(RegisterStates.waiting_for_location)

@router.message(RegisterStates.waiting_for_location, lambda m: m.location is not None)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(
        latitude=message.location.latitude,
        longitude=message.location.longitude
    )
    data = await state.get_data()
    payload = {
        "telegram_id": message.from_user.id,
        "name": data["name"],
        "gender": data["gender"],
        "age": data["age"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "password": str(message.from_user.id)
    }

    try:
        async with ClientSession() as session:
            async with session.post(f"{settings.DJANGO_URL}/api/register/", json=payload) as resp:
                if resp.status == 201:
                    await message.answer("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=ReplyKeyboardRemove())
                else:
                    await message.answer("⚠️ Xatolik yuz berdi yoki siz allaqachon ro'yxatdan o'tgansiz.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"❗ Server bilan aloqa muvaffaqiyatsiz tugadi: {e}", reply_markup=ReplyKeyboardRemove())

    await state.clear()
    await show_main_menu(message)

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
