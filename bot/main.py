import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = 'YOUR_BOT_TOKEN'  # <-- o'zgartiring
ADMIN_GROUP_ID = -1001234567890  # <-- o'zgartiring
DJANGO_URL = 'http://localhost:8000'  # Django backend URL


storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Xotirada yangi reportlar uchun oddiy navbat (prod uchun Redis yoki DB ishlating)
# Xotirada yangi reportlar uchun oddiy navbat (prod uchun Redis yoki DB ishlating)
REPORT_QUEUE = []

# --- Onboarding States ---
class RegisterStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_location = State()
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    # Backendda user bor-yo'qligini tekshirish
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{DJANGO_URL}/api/users/nearby/?lat=0&lon=0') as resp:
            # Bu joyda real tekshiruv uchun alohida endpoint qilish mumkin
            pass
    await message.answer("Ismingizni kiriting:")
    await RegisterStates.waiting_for_name.set()

@dp.message_handler(state=RegisterStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👨 Erkak", callback_data="gender_male"),
        InlineKeyboardButton("👩 Ayol", callback_data="gender_female")
    )
    await message.answer("Jinsingizni tanlang:", reply_markup=keyboard)
    await RegisterStates.waiting_for_gender.set()

@dp.callback_query_handler(lambda c: c.data.startswith('gender_'), state=RegisterStates.waiting_for_gender)
async def process_gender(call: types.CallbackQuery, state: FSMContext):
    gender = call.data.split('_')[1]
    await state.update_data(gender=gender)
    await call.message.answer("Yoshingizni kiriting:")
    await RegisterStates.waiting_for_age.set()
    await call.answer()

@dp.message_handler(lambda m: not m.text.isdigit(), state=RegisterStates.waiting_for_age)
async def process_age_invalid(message: types.Message, state: FSMContext):
    await message.reply("Yosh faqat raqamda bo'lishi kerak. Qayta kiriting:")

@dp.message_handler(lambda m: m.text.isdigit(), state=RegisterStates.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("Lokatsiyani yuborish", request_location=True))
    await message.answer("Lokatsiyangizni yuboring:", reply_markup=keyboard)
    await RegisterStates.waiting_for_location.set()

@dp.message_handler(content_types=types.ContentType.LOCATION, state=RegisterStates.waiting_for_location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    data = await state.get_data()
    # Ro'yxatdan o'tkazish uchun backendga so'rov
    payload = {
        'telegram_id': message.from_user.id,
        'name': data['name'],
        'gender': data['gender'],
        'age': data['age'],
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'password': str(message.from_user.id)  # demo uchun
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{DJANGO_URL}/api/register/', json=payload) as resp:
            if resp.status == 201:
                await message.answer("Ro'yxatdan o'tdingiz!", reply_markup=types.ReplyKeyboardRemove())
            else:
                await message.answer("Xatolik yuz berdi yoki siz allaqachon ro'yxatdan o'tgansiz.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
    await show_main_menu(message)

async def show_main_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👩‍❤️‍👨 Do‘st izlash", callback_data="find_friends"),
        InlineKeyboardButton("💬 Mening suhbatlarim", callback_data="my_chats")
    )
    keyboard.add(
        InlineKeyboardButton("📂 Do‘stlarim", callback_data="my_friends"),
        InlineKeyboardButton("🚨 Shikoyat qilish", callback_data="report")
    )
    await message.answer("Asosiy menyu:", reply_markup=keyboard)

async def fetch_reports():
    """Django backenddan yangi reportlarni polling orqali olish (demo uchun)"""
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'{DJANGO_URL}/api/report/notify/') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for report in data.get('reports', []):
                            if report['report_id'] not in REPORT_QUEUE:
                                await send_report_to_admin(report)
                                REPORT_QUEUE.append(report['report_id'])
            except Exception as e:
                print('Polling error:', e)
        await asyncio.sleep(5)

async def send_report_to_admin(report):
    text = (
        f"🛑 Yangi shikoyat!\n"
        f"Shikoyatchi: {report['reporter']}\n"
        f"Shikoyat qilinuvchi: {report['reported']}\n"
        f"Sabab: {report['reason']}\n"
        f"Vaqt: {report['timestamp']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Ban qilish", callback_data=f"ban_{report['reported']}"),
         InlineKeyboardButton(text="❌ Ochish", callback_data=f"ignore_{report['report_id']}")]
    ])
    await bot.send_message(ADMIN_GROUP_ID, text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('ban_'))
async def ban_user_callback(call: types.CallbackQuery):
    telegram_id = call.data.split('_')[1]
    async with aiohttp.ClientSession() as session:
        await session.post(f'{DJANGO_URL}/api/users/ban/', json={'telegram_id': telegram_id})
    await call.answer("Foydalanuvchi ban qilindi!")
    await call.message.edit_reply_markup()

@dp.callback_query_handler(lambda c: c.data.startswith('ignore_'))
async def ignore_report_callback(call: types.CallbackQuery):
    await call.answer("Shikoyat yopildi.")
    await call.message.edit_reply_markup()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(fetch_reports())
    executor.start_polling(dp, skip_updates=True)
