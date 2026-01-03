import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import date, datetime
from aiogram.types import ReplyKeyboardRemove

# ================== SOZLAMALAR ==================
from config import BOT_TOKEN, PRIVATE_GROUP_ID
from state import IshFSM

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== DATABASE ==================
conn = sqlite3.connect("bot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")
conn.commit()

# button
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

date_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Bugun")],
        [KeyboardButton(text="✏️ Boshqa sana")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def get_user(telegram_id: int):
    cur.execute("SELECT name FROM users WHERE telegram_id=?", (telegram_id,))
    return cur.fetchone()


def save_user(telegram_id: int, name: str):
    cur.execute(
        "INSERT OR REPLACE INTO users (telegram_id, name) VALUES (?, ?)",
        (telegram_id, name)
    )
    conn.commit()


# ================== STATES ==================
class WorkState(StatesGroup):
    waiting_for_name = State()
    waiting_for_job = State()
    waiting_for_count = State()
    waiting_for_date = State()


# ================== BOT ==================
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ================== START ==================
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)

    if not user:
        await message.answer("👋 Assalomu alaykum!\nIsmingizni kiriting:")
        await state.set_state(WorkState.waiting_for_name)
    else:
        await message.answer(
            f"👋 Xush kelibsiz, {user[0]}!\n\n"
            f"✍️ Ish nomini yozing:"
        )
        await state.set_state(WorkState.waiting_for_job)


# ================== SAVE NAME ==================
@dp.message(WorkState.waiting_for_name)
async def save_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Ism juda qisqa. Qayta kiriting:")
        return

    save_user(message.from_user.id, name)

    await message.answer(
        f"✅ Rahmat, {name}!\n\n"
        f"✍️ Endi ish nomini yozing:"
    )
    await state.set_state(WorkState.waiting_for_job)


# ================== JOB NAME ==================
@dp.message(WorkState.waiting_for_job)
async def job_name(message: types.Message, state: FSMContext):
    await state.update_data(job_name=message.text.strip())
    await message.answer("🔢 Ish sonini kiriting:")
    await state.set_state(WorkState.waiting_for_count)


# ================== JOB COUNT + SEND TO GROUP ==================
@dp.message(WorkState.waiting_for_count)
async def job_count(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    await state.update_data(count=message.text)

    await message.answer(
        "📅 Ish sanasini tanlang:",
        reply_markup=date_keyboard
    )
    await state.set_state(WorkState.waiting_for_date)


@dp.message(WorkState.waiting_for_date)
async def job_date(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if text == "📅 Bugun":
        selected_date = date.today().strftime("%Y-%m-%d")

    elif text == "✏️ Boshqa sana":
        await message.answer(
            "✏️ Sanani quyidagi formatda kiriting:\n"
            "YYYY-MM-DD (masalan: 2026-01-05)",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    else:
        # qo‘lda kiritilgan sana
        try:
            datetime.strptime(text, "%Y-%m-%d")
            selected_date = text
        except ValueError:
            selected_date = text

    await state.update_data(date=selected_date)

    data = await state.get_data()
    user_db = get_user(message.from_user.id)

    tg_user = message.from_user
    username = f"@{tg_user.username}" if tg_user.username else "yo‘q"

    group_text = (
        "📝 YANGI ISH\n\n"
        f"🧑 Ishchi: {user_db[0]}\n"
        f"📦 Ish nomi: {data['job_name']}\n"
        f"🔢 Soni: {data['count']}\n"
        f"📅 Sana: {data['date']}\n\n"
        "👤 Telegram ma'lumotlari:\n"
        f"• Username: {username}\n"
        f"• ID: {tg_user.id}"
    )

    await bot.send_message(PRIVATE_GROUP_ID, group_text)

    await message.answer(
        "✅ Ish guruhga yuborildi!\n\n"
        "🔁 Yangi ish yozish uchun /start ni bosing",
        reply_markup=ReplyKeyboardRemove()
    )

    # 🔥 ENG MUHIMI
    await state.clear()
    


# ================== RUN ==================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
