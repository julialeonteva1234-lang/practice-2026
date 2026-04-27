import asyncio
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен не найден! Проверь файл .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class MenuText:
    """Все тексты для меню в одном месте"""
    
    BTN_ABOUT = "📖 Коротко о проекте"
    BTN_GOALS = "🎯 Какие у нас задачи и цели"
    BTN_PARTNER = "🤝 О нашем партнере"
    BTN_SOCIAL = "📱 Мы в соц сетях"
    BTN_QUIZ = "🍄 Узнать какой ты гриб"
    BTN_TOP = "🏆 Топ грибов"
    
    MSG_START = """🍄 Привет! Здесь ты сможешь лучше познакомиться с проектом Fungi.

Выбери, что тебя интересует:"""
    
    MSG_ABOUT = """📌 Коротко о проекте:

Fungi — это проект по созданию платформы с энциклопедией грибов и интересными статьями о них. Поможет пользователям улучшить навыки идентификации и сбора грибов, расширить свои знания о грибах и повысить интерес к природе."""
    
    MSG_GOALS = """🎯 Какие у нас задачи и цели:

Цель проекта:
Создание доступной, функциональной и информативной платформы для грибников

Задачи проекта:
• Разработка структуры энциклопедии грибов, в том числе создание информационных карточек для грибов и их категоризация по различным признакам
• Создание дополнительного научно-популярного контента о грибах
• Исследование и анализ сферы деятельности проекта, его целевой аудитории и работа с ней.
• Разработка удобного и интуитивно понятного интерфейса для приложений и его интеграция в них.
• Разработка веб-приложения при помощи средств ASP .NET Core 7 и React + TS
• Разработка мобильного приложения при помощи средств React Native
• Тестирование итоговых продуктов и их дальнейшая поддержка"""
    
    MSG_PARTNER = """🤝 О нашем партнере:

Наш партнёр — Автономная некоммерческая организация Центр содействия социальным инновациям «Технологии изменения и развития»
Организация позиционирует себя как центр, способствующий внедрению социальных инноваций и развитию личности.
Ключевое направление — развитие и внедрение культуры проектной деятельности в образовательных организациях. В рамках этого направления команда занимается:
•	Проектированием развивающей среды.
•	Формированием экосистемы проектной деятельности.
•	Проектированием «организаций будущего».
"""
    
    MSG_SOCIAL = """📱 Переходи в наш тг-канал!

• Telegram: https://t.me/fungiofficial
"""
    
    @classmethod
    def get_all_buttons(cls):
        return [
            [KeyboardButton(text=cls.BTN_ABOUT)],
            [KeyboardButton(text=cls.BTN_GOALS)],
            [KeyboardButton(text=cls.BTN_PARTNER)],
            [KeyboardButton(text=cls.BTN_SOCIAL)],
            [KeyboardButton(text=cls.BTN_QUIZ)],
            [KeyboardButton(text=cls.BTN_TOP)]
        ]
    
  
    @classmethod
    def get_router(cls):
        return {
            cls.BTN_ABOUT: "about",
            cls.BTN_GOALS: "goals",
            cls.BTN_PARTNER: "partner",
            cls.BTN_SOCIAL: "social",
        }
    
  
    @classmethod
    def get_response(cls, key):
        responses = {
            "about": cls.MSG_ABOUT,
            "goals": cls.MSG_GOALS,
            "partner": cls.MSG_PARTNER,
            "social": cls.MSG_SOCIAL,
        }
        return responses.get(key, "Информация временно недоступна")


def init_db():
    """Создаём таблицу для статистики квиза"""
    conn = sqlite3.connect("quiz_stats.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            mushroom_type TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_quiz_result(user_id, username, mushroom_type):
    """Сохраняем результат квиза"""
    conn = sqlite3.connect("quiz_stats.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quiz_results (user_id, username, mushroom_type, date) VALUES (?, ?, ?, ?)",
        (user_id, username, mushroom_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_top_mushrooms(limit=5):
    """Получаем топ-5 самых популярных грибов"""
    conn = sqlite3.connect("quiz_stats.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mushroom_type, COUNT(*) as count 
        FROM quiz_results 
        GROUP BY mushroom_type 
        ORDER BY count DESC 
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


QUIZ = [
    {
        "question": "🌲 Где ты предпочитаешь проводить время?",
        "options": ["В густом лесу", "На опушке", "У ручья", "На солнечной поляне"],
        "results": {
            "В густом лесу": "Боровик",
            "На опушке": "Подберёзовик",
            "У ручья": "Сыроежка",
            "На солнечной поляне": "Лисичка"
        }
    },
    {
        "question": "🎭 Какой твой характер?",
        "options": ["Спокойный и мудрый", "Энергичный и яркий", "Загадочный и тихий", "Дружелюбный и общительный"],
        "results": {
            "Спокойный и мудрый": "Белый гриб",
            "Энергичный и яркий": "Мухомор",
            "Загадочный и тихий": "Сморчок",
            "Дружелюбный и общительный": "Опята"
        }
    },
    {
        "question": "🍽️ Что ты выберешь на ужин?",
        "options": ["Стейк", "Салат", "Суп", "Десерт"],
        "results": {
            "Стейк": "Груздь",
            "Салат": "Шампиньон",
            "Суп": "Вешенка",
            "Десерт": "Трюфель"
        }
    }
]

user_answers = {}

def get_main_keyboard():
    """Главная клавиатура с кнопками"""
    return ReplyKeyboardMarkup(
        keyboard=MenuText.get_all_buttons(), 
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(MenuText.MSG_START, reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text in MenuText.get_router().keys())
async def handle_info(message: types.Message):
    router = MenuText.get_router()
    key = router.get(message.text)
    await message.answer(MenuText.get_response(key), reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text == MenuText.BTN_TOP)
async def show_top_mushrooms(message: types.Message):
    top = get_top_mushrooms(5)
    if not top:
        await message.answer(f"📊 Пока никто не проходил квиз! Будь первым — нажми '{MenuText.BTN_QUIZ}'", reply_markup=get_main_keyboard())
        return
    
    text = "🏆 Топ-5 самых популярных грибов среди пользователей:\n\n"
    for i, (mushroom, count) in enumerate(top, 1):
        if count % 10 == 1 and count % 100 != 11:
            word = "раз"
        elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
            word = "раза"
        else:
            word = "раз"
        
        text += f"{i}. {mushroom} — {count} {word} 🍄\n"
    
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text == MenuText.BTN_QUIZ)
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    user_answers[user_id] = {"step": 0, "answers": []}
    await send_quiz_question(message, user_id)

async def send_quiz_question(message: types.Message, user_id: int):
    """Отправляет текущий вопрос квиза"""
    step = user_answers[user_id]["step"]
    if step >= len(QUIZ):
        await finish_quiz(message, user_id)
        return
    
    q = QUIZ[step]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"quiz_{step}_{opt}")] for opt in q["options"]
    ])
    await message.answer(f"❓ Вопрос {step+1}/{len(QUIZ)}: {q['question']}", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data and c.data.startswith("quiz_"))
async def handle_quiz_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_answers:
        await callback.message.answer(f"Начни квиз заново кнопкой '{MenuText.BTN_QUIZ}'", reply_markup=get_main_keyboard())
        await callback.answer()
        return

    parts = callback.data.split("_")
    step = int(parts[1])
    answer = "_".join(parts[2:])
    answer = answer.replace("_", " ")

    q = QUIZ[step]
    mushroom = q["results"].get(answer, "Загадочный гриб")
    
    user_answers[user_id]["answers"].append(mushroom)
    user_answers[user_id]["step"] += 1
    
    await callback.message.delete()
    
    if user_answers[user_id]["step"] >= len(QUIZ):
        await finish_quiz(callback.message, user_id)
    else:
        await send_quiz_question(callback.message, user_id)
    
    await callback.answer()

async def finish_quiz(message: types.Message, user_id: int):
    """Завершает квиз и показывает результат"""
    answers = user_answers[user_id]["answers"]
    final_mushroom = answers[-1] if answers else "Лисичка"
    
    username = message.from_user.username or message.from_user.first_name
    save_quiz_result(user_id, username, final_mushroom)
    
    result_text = f"🍄 Ты — **{final_mushroom}**!\n\n"
    result_text += "✨ Этот гриб отражает твою уникальную натуру.\n"
    result_text += "Поделись результатом с друзьями!"
    
    await message.answer(result_text, reply_markup=get_main_keyboard())
    
    del user_answers[user_id]

async def main():
    init_db()
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())