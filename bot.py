# -*- coding: utf-8 -*-
import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- НАЗВАНИЕ ПРОЕКТА ---
PROJECT_NAME = "--- Контент-завод «Габриэль глаголит Даля» (v1.1) ---"

# --- БАЗА ДАННЫХ СЛОВ (v1.0 - Встроена в код) ---
# Наполняем 5 из 30 категорий для теста

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

# --- ДУША ПРОЕКТА: ГЛАГОЛЫ ДАЛЯ (В ПРАВИЛЬНОЙ ФОРМЕ) ---
DAHL_VERBS = ["юлит", "шарахает", "голдит", "еры́згает", "кумекает", "ерепенится", "фиглярничает", "скоморошничает", "лукавствует", "пеняет"]

# --- ОСНОВНЫЕ ФУНКЦИИ БОТА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение и показывает кнопку."""
    keyboard = [["Габриэль, глаголь!"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        "Мы родились, чтоб разум сделать пылью.\n\n"
        "Нажми на кнопку.",
        reply_markup=reply_markup,
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главная функция: генерирует и отправляет 3 промпта."""
    await update.message.reply_text("Принято! Выбираю темы, смешиваю слова, ищу душу в словаре Даля...")

    # 1. Выбор 3 случайных тем
    category_names = list(CATEGORIES.keys())
    selected_categories = random.sample(category_names, 3)
    
    # 2. Формирование пула слов
    adjective_pool = []
    noun_pool = []
    for cat_name in selected_categories:
        adjective_pool.extend(CATEGORIES[cat_name]["adjectives"])
        noun_pool.extend(CATEGORIES[cat_name]["nouns"])

    # 3. Генерация 3 промтов
    prompts = []
    for i in range(3):
        adj = random.choice(adjective_pool)
        noun = random.choice(noun_pool)
        verb = random.choice(DAHL_VERBS)
        prompts.append(f"{i+1}. {adj} {noun} {verb}")

    # Формирование и отправка финального сообщения
    theme_text = ", ".join(selected_categories)
    final_message = (
        f"🔥 **Готово!**\n\n"
        f"Темы этого часа: **{theme_text}**.\n\n"
        "Ваши абсурдные промпты:\n"
        f"▪️ {prompts[0]}\n"
        f"▪️ {prompts[1]}\n"
        f"▪️ {prompts[2]}"
    )
    await update.message.reply_text(final_message, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логирует ошибки."""
    print(f"Произошла ошибка: {context.error}")

def main() -> None:
    """Запускает бота."""
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        print("ОШИБКА: Токен не найден. Убедись, что он добавлен в переменные окружения.")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_error_handler(error_handler)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Габриэль, глаголь!$"), generate))

    print(f"{PROJECT_NAME} запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()

