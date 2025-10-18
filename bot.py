# -*- coding: utf-8 -*-
import os
import random
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- НАЗВАНИЕ ПРОЕКТА ---
PROJECT_NAME = "--- Контент-завод «Габриэль глаголит Даля» (v3.0 Финальная) ---"

# --- БАЗА ДАННЫХ СЛОВ ---
CATEGORIES = {
    "Еда": {
        "adjectives": ["Карамельный", "Подгоревший", "Ледяной", "Острый", "Сливочный"],
        "nouns": ["пончик", "мороженое", "арбуз", "бутерброд", "круассан"]
    },
    "Технологии": {
        "adjectives": ["Виртуальный", "Цифровой", "Лазерный", "Неоновый", "Роботизированный"],
        "nouns": ["дрон", "проектор", "сервер", "нейросеть", "микрочип"]
    },
    "Спорт": {
        "adjectives": ["Олимпийский", "Рекордный", "Атлетичный", "Прыгучий", "Гибкий"],
        "nouns": ["батут", "скакалка", "гантеля", "боксерская груша", "скейтборд"]
    },
    "Искусство": {
        "adjectives": ["Абстрактный", "Классический", "Бронзовый", "Мраморный", "Авангардный"],
        "nouns": ["мольберт", "граффити", "статуя", "гобелен", "палитра"]
    },
    "Медицина": {
        "adjectives": ["Стерильный", "Хирургический", "Клинический", "Анатомический", "Инъекционный"],
        "nouns": ["шприц", "стетоскоп", "скальпель", "микроскоп", "таблетка"]
    }
}

# --- ДУША ПРОЕКТА: ГЛАГОЛЫ ДАЛЯ ---
DAHL_VERBS = ["юлит", "шарахает", "голдит", "еры́згает", "кумекает", "ерепенится", "фиглярничает", "скоморошничает", "лукавствует", "пеняет"]

# --- ИНТЕГРАЦИЯ С GEMINI ---

async def modernize_with_gemini(prompts: list) -> str:
    """Отправляет промпты в Gemini и получает один обогащенный сценарий."""
    try:
        # ИСПОЛЬЗУЕМ НОВУЮ, СТАБИЛЬНУЮ МОДЕЛЬ
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        meta_prompt = (
            "Ты — гениальный креативный директор для вирусных видео. "
            "Тебе даны 3 абсурдные идеи. "
            "Твоя задача: объединить их в один детализированный, визуально насыщенный и кинематографичный сценарий для видео-нейросети. "
            "Опиши сцену, действия, стиль и атмосферу. Сделай это странным, но понятным для визуализации.\n\n"
            "Идеи:\n"
            f"- {prompts[0]}\n"
            f"- {prompts[1]}\n"
            f"- {prompts[2]}\n\n"
            "Твой сценарий:"
        )
        
        response = await model.generate_content_async(meta_prompt)
        return response.text
    except Exception as e:
        print(f"!!! КРИТИЧЕСКАЯ ОШИБКА при работе с Gemini: {e}")
        return "Не удалось связаться с креативным директором Gemini. Проверьте API-ключ и логи на сервере."

# --- ОСНОВНЫЕ ФУНКЦИИ БОТА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["Габриэль, глаголь!"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "Мы родились, чтоб разум сделать пылью. (v3.0)\n\n"
        "Нажми на кнопку.",
        reply_markup=reply_markup,
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Принято! Генерирую абсурд, отправляю на креативный совет к Gemini...")

    category_names = list(CATEGORIES.keys())
    selected_categories = random.sample(category_names, 3)
    adjective_pool = [adj for cat in selected_categories for adj in CATEGORIES[cat]["adjectives"]]
    noun_pool = [noun for cat in selected_categories for noun in CATEGORIES[cat]["nouns"]]
    
    base_prompts = []
    for _ in range(3):
        adj = random.choice(adjective_pool)
        noun = random.choice(noun_pool)
        verb = random.choice(DAHL_VERBS)
        base_prompts.append(f"{adj} {noun} {verb}")

    gemini_script = await modernize_with_gemini(base_prompts)

    theme_text = ", ".join(selected_categories)
    final_message = (
        f"🔥 **Креативный совет завершен!**\n\n"
        f"Темы этого часа: **{theme_text}**.\n\n"
        f"Базовые идеи:\n"
        f"▪️ {base_prompts[0]}\n"
        f"▪️ {base_prompts[1]}\n"
        f"▪️ {base_prompts[2]}\n\n"
        f"🎬 **Сценарий от Gemini:**\n{gemini_script}"
    )
    await update.message.reply_text(final_message, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Произошла ошибка: {context.error}")

def main() -> None:
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    if not TOKEN or not GEMINI_API_KEY:
        print("ОШИБКА: Один из API-ключей не найден.")
        return
        
    genai.configure(api_key=GEMINI_API_KEY)

    application = Application.builder().token(TOKEN).build()
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Габриэль, глаголь!$"), generate))
    
    print(f"{PROJECT_NAME} запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()

