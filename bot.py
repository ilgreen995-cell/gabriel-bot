# -*- coding: utf-8 -*-
import os
import random
import asyncio
import requests # "Интернет-антенна" для скачивания словарей
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- НАЗВАНИЕ ПРОЕКТА ---
PROJECT_NAME = "--- AI-режиссер «Габриэль глаголит Даля» (v7.2 - Стабильная) ---"

# Определяем состояния для диалога
TREND_INPUT = 0

# --- Функция для скачивания словарей из интернета ---
def download_dictionary(url, name):
    print(f"Загружаю словарь '{name}' из интернета...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        words = response.content.decode('utf-8').splitlines()
        print(f"Успешно загружено {len(words)} слов.")
        return [word.strip() for word in words if word.strip()]
    except requests.exceptions.RequestException as e:
        print(f"ОШИБКА: Не удалось загрузить словарь '{name}': {e}")
        return []

# --- ОБНОВЛЕННЫЕ ССЫЛКИ НА БОЛЬШИЕ ИНТЕРНЕТ-СЛОВАРИ ---
URL_SUBJECTS = "https://raw.githubusercontent.com/danakt/russian-words/master/nouns.txt"
URL_ACTIONS = "https://raw.githubusercontent.com/danakt/russian-words/master/verbs.txt" # Будем использовать как действия
URL_SCENES = "https://raw.githubusercontent.com/danakt/russian-words/master/adjectives.txt" # Будем использовать как описания сцен

# --- ЗАГРУЖАЕМ СЛОВАРИ ПРИ СТАРТЕ БОТА ---
SUBJECTS_RU = download_dictionary(URL_SUBJECTS, "Герои (существительные)")
ACTIONS_RU = download_dictionary(URL_ACTIONS, "Действия (глаголы)")
SCENES_RU_ADJECTIVES = download_dictionary(URL_SCENES, "Сцены (прилагательные)")

# Добавим немного конкретных мест для разнообразия
SCENES_RU_NOUNS = ["в пустой галерее", "на тихом озере", "на поверхности Марса", "в операционной будущего", "на кухне ресторана", "в ночном Токио", "в пентхаусе с видом на город", "на пиратском корабле", "в концертном зале", "в заброшенном храме", "на гоночной трассе"]

# --- ДУША ПРОЕКТА: ГЛАГОЛЫ ДАЛЯ ---
GLAGOLY_DALYA_RU = ["встопорщиться", "ерничать", "околпачить", "лукавствовать", "негодовать", "брезжить", "кумекать", "учинить", "насупиться", "ворожить", "скоморошничать", "пенять", "лебезить", "судачить", "юродствовать", "кощунствовать", "ерепениться", "благолепствовать", "фиглярничать", "тунеядствовать", "усердствовать", "лихоимствовать"]

# --- ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ СЪЕМКИ (остаются неизменными) ---
CAMERA_ANGLES_RU = ["Крупный план", "Сверхширокий общий план", "Съемка с нижнего ракурса", "Вид сверху (птичий полет)", "Голландский угол", "Съемка из-за плеча"]
CAMERA_MOVEMENTS_RU = ["Плавный наезд (dolly in)", "Быстрый, резкий монтаж", "Медленное панорамирование", "Съемка со стедикама", "Вращение камеры", "Эффект 'вертиго'"]
LENS_EFFECTS_RU = ["Эффект 'рыбий глаз'", "Мягкий фокус с боке", "Анаморфотные блики", "Эффект миниатюры 'тильт-шифт'", "Глубокая резкость", "Засветка пленки"]
STYLES_RU = ["в стиле Уэса Андерсона", "гиперреализм", "как запись на VHS кассету 80-х", "кукольная анимация", "в стиле аниме студии Ghibli", "киберпанк", "стимпанк", "съемка на IMAX камеру", "в стиле картины барокко"]
TEMPORAL_ELEMENTS_RU = ["Замедленная съемка (slow motion)", "Ускоренная съемка (timelapse)", "Резкий стоп-кадр", "Обратная перемотка действия", "Эффект 'bullet time'"]

# --- АНГЛИЙСКИЕ ВЕРСИИ ДЛЯ ПРОМПТА (остаются для структуры) ---
SUBJECTS_EN = ["a living statue", "a talking fish", "a lonely astronaut"]
ACTIONS_EN = ["writing a self-portrait", "smoking a cigar", "playing golf on the Moon"]
SCENES_EN = ["in an empty art gallery", "on a quiet lake", "on the surface of Mars"]
CAMERA_ANGLES_EN = ["close-up shot", "extreme wide shot", "low-angle shot"]
CAMERA_MOVEMENTS_EN = ["dolly in", "fast cut editing", "slow panning"]
LENS_EFFECTS_EN = ["fisheye lens", "soft focus with bokeh", "anamorphic lens flare"]
STYLES_EN = ["in the style of Wes Anderson", "hyperrealistic", "80s VHS recording"]
TEMPORAL_ELEMENTS_EN = ["slow motion", "timelapse", "freeze frame"]


# --- ИНТЕРАКТИВНЫЕ ФУНКЦИИ БОТА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["Создать Сценарий 🎬"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я — AI-режиссер Габриэль.\n\n"
        "Я создаю вирусные сценарии на основе твоих трендов и безграничных баз слов.\n\n"
        "Нажми на кнопку, чтобы начать.",
        reply_markup=reply_markup,
    )
    return ConversationHandler.END

async def request_trends(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Отлично! Теперь введите до 3-х актуальных трендов, каждый с новой строки.\n\n"
        "Я выберу один случайным образом и построю вокруг него сценарий."
    )
    return TREND_INPUT

async def generate_script_from_trends(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Принято! Подключаюсь к интернет-базам, анализирую ваши тренды, пишу сценарий...")
    
    user_trends = [trend.strip() for trend in update.message.text.splitlines() if trend.strip()]
    
    if not user_trends:
        await update.message.reply_text("Вы не ввели ни одного тренда. Пожалуйста, попробуйте снова, нажав на кнопку.")
        return ConversationHandler.END

    if not all([SUBJECTS_RU, ACTIONS_RU, SCENES_RU_ADJECTIVES]):
         await update.message.reply_text("Извините, не удалось загрузить словари из интернета. Попробуйте позже.")
         return ConversationHandler.END

    trend_ru = random.choice(user_trends)
    trend_en = "something trending now"

    subject_ru = random.choice(SUBJECTS_RU)
    action_ru = random.choice(ACTIONS_RU)
    scene_ru = f"{random.choice(SCENES_RU_ADJECTIVES)} {random.choice(SCENES_RU_NOUNS)}"
    angle_ru = random.choice(CAMERA_ANGLES_RU)
    movement_ru = random.choice(CAMERA_MOVEMENTS_RU)
    lens_ru = random.choice(LENS_EFFECTS_RU)
    style_ru = random.choice(STYLES_RU)
    temporal_ru = random.choice(TEMPORAL_ELEMENTS_RU)
    dahl_verb_ru = random.choice(GLAGOLY_DALYA_RU)
    
    script_ru = (
        f"🎬 **Режиссерский сценарий**\n\n"
        f"▪️ **🔥 Ваш Тренд:** {trend_ru.capitalize()}\n\n"
        f"▪️ **Subject:** {subject_ru.capitalize()}\n"
        f"▪️ **Action:** {action_ru}\n"
        f"▪️ **Scene:** {scene_ru}\n"
        f"▪️ **Camera Angle:** {angle_ru}\n"
        f"▪️ **Camera Movement:** {movement_ru}\n"
        f"▪️ **Lens Effect:** {lens_ru}\n"
        f"▪️ **Style:** {style_ru}\n"
        f"▪️ **Temporal:** {temporal_ru}\n\n"
        f"🎤 **Голос Габриэля:** *И на фоне всего этого он умудрился **{dahl_verb_ru}**.*"
    )
    
    prompt_en = (
        f"Trending now: {trend_en}. "
        f"{random.choice(SUBJECTS_EN)}, {random.choice(ACTIONS_EN)}, {random.choice(SCENES_EN)}, "
        f"{random.choice(CAMERA_ANGLES_EN)}, {random.choice(CAMERA_MOVEMENTS_EN)}, {random.choice(LENS_EFFECTS_EN)}, "
        f"{random.choice(STYLES_EN)}, {random.choice(TEMPORAL_ELEMENTS_EN)}, "
        f"cinematic, masterpiece, high detail"
    )

    await update.message.reply_text(script_ru, parse_mode='Markdown')
    await update.message.reply_text(f"🤖 **Промпт для AI-генератора:**\n\n`{prompt_en}`", parse_mode='Markdown')
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Действие отменено. Нажмите кнопку, чтобы начать снова.')
    return ConversationHandler.END

# НОВЫЙ БЛОК: "Помощник режиссера" для отлова ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Записывает ошибки в лог, чтобы бот не падал."""
    print(f"Произошла ошибка: {context.error}")

def main() -> None:
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        print("ОШИБКА: Токен не найден.")
        return

    application = Application.builder().token(TOKEN).build()
    
    # Подключаем "помощника режиссера"
    application.add_error_handler(error_handler)
    
    # Создаем обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Создать Сценарий 🎬$"), request_trends)],
        states={
            TREND_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_script_from_trends)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    
    print(f"{PROJECT_NAME} запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()

