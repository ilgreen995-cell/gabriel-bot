# -*- coding: utf-8 -*-
import os
import random
import requests # <--- ПРОВЕРЕНО
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler)

# --- НАЗВАНИЕ ПРОЕКТА ---
PROJECT_NAME = "--- AI-режиссер «Габриэль глаголит Даля» (v9.0 Бредогенератор) ---"

# Определяем состояния для диалога
SELECTING_THEMES, GENERATING = range(2)

# --- Функция для скачивания словарей из интернета ---
def download_dictionary(url, name):
    print(f"Загружаю словарь '{name}' из интернета...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        words = response.content.decode('utf-8').splitlines()
        print(f"Успешно загружено {len(words)} слов.")
        return [word.strip() for word in words if word.strip()]
    except requests.exceptions.RequestException as e:
        print(f"ОШИБКА: Не удалось загрузить словарь '{name}': {e}")
        return []

# --- ПРОВЕРЕННЫЕ ИНТЕРНЕТ-БАЗЫ СЛОВ ---
URL_NOUNS = "https://raw.githubusercontent.com/danakt/russian-words/master/nouns.txt"
URL_VERBS = "https://raw.githubusercontent.com/danakt/russian-words/master/verbs.txt"
URL_ADJECTIVES = "https://raw.githubusercontent.com/danakt/russian-words/master/adjectives.txt"

NOUNS_RU = download_dictionary(URL_NOUNS, "Существительные")
VERBS_RU = download_dictionary(URL_VERBS, "Глаголы")
ADJECTIVES_RU = download_dictionary(URL_ADJECTIVES, "Прилагательные")

# --- БОЛЬШАЯ БАЗА ТЕМАТИЧЕСКИХ СЛОВ (14 ТЕМ) ---
THEMES = {
    "искусство": {"keywords": ["art", "sculpture", "painting", "gallery"]},
    "рыбалка": {"keywords": ["fishing", "lake", "fish", "boat"]},
    "космос": {"keywords": ["space", "astronaut", "planet", "rocket"]},
    "медицина": {"keywords": ["medical", "doctor", "hospital", "science"]},
    "кулинария": {"keywords": ["cooking", "food", "kitchen", "restaurant"]},
    "военное дело": {"keywords": ["military", "soldier", "tank", "battle"]},
    "мифология": {"keywords": ["mythology", "gods", "legend", "monster"]},
    "наука": {"keywords": ["science", "laboratory", "experiment", "discovery"]},
    "пиратство": {"keywords": ["pirate", "ship", "treasure", "ocean"]},
    "музыка": {"keywords": ["music", "concert", "symphony", "piano"]},
    "религия": {"keywords": ["religion", "temple", "angel", "prayer"]},
    "роскошная жизнь": {"keywords": ["luxury", "yacht", "mansion", "diamonds"]},
    "автомобили": {"keywords": ["car", "racing", "supercar", "engine"]},
    "интернет и тренды": {"keywords": ["internet", "viral", "meme", "hacker"]}
}

# --- ДУША ПРОЕКТА: РАСШИРЕННЫЙ СЛОВАРЬ ДАЛЯ ---
GLAGOLY_DALYA_RU = [
    "встопорщиться", "ерничать", "околпачить", "лукавствовать", "негодовать", "брезжить", 
    "кумекать", "учинить", "насупиться", "ворожить", "скоморошничать", "пенять", "лебезить", 
    "судачить", "юродствовать", "кощунствовать", "ерепениться", "благолепствовать", 
    "фиглярничать", "тунеядствовать", "усердствовать", "лихоимствовать", "благоухать", 
    "велеречить", "возбранять", "гнушаться", "гоношиться", "дерзновенно", "е Vозбранять", 
    "канителиться", "кашеварить", "клянчить", "колобродить", "кочевряжиться", "куражиться", 
    "куролесить", "лоботрясничать", "лукавить", "маяться", "мешкать", "миндальничать", 
    "мудровать", "набедокурить", "навостриться", "назойничать", "напутствовать", 
    "насмешничать", "натореть", "недоумевать", "неистовствовать", "обмишулиться", 
    "обособиться", "образумиться", "окаянствовать", "опростоволоситься", "осерчать", 
    "остолбенеть", "отлынивать", "охальничать", "пакостить", "паясничать", "перечить", 
    "пировать", "пластаться", "плутовать", "подтрунивать", "помыкать", "потворствовать", 
    "почивать", "праздновать", "прекословить", "препираться", "привередничать", "прихвастнуть", 
    "проказничать", "пустословить", "раболепствовать", "разглагольствовать", "разохотиться", 
    "распекать", "своевольничать", "сквернословить", "смиренно", "сокрушаться", "суетиться", 
    "сумасбродствовать", "тешиться", "томиться", "торжествовать", "трепетать", "трусить", 
    "тщеславиться", "ублажать", "угождать", "умиляться", "уповать", "упрямиться", 
    "философствовать", "фордыбачить", "ханжить", "хвастать", "хитрить", "хлопотать", 
    "хохмить", "царствовать", "чародействовать", "чествовать", "чопорничать", "чудить", 
    "шалопайничать", "шествовать", "шиковать", "шкодить", "шутить", "щеголять", "юлить"
]

# --- ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ СЪЕМКИ ---
CAMERA_ANGLES_RU = ["Крупный план", "Сверхширокий общий план", "Съемка с нижнего ракурса", "Вид сверху (птичий полет)", "Голландский угол", "Съемка из-за плеча"]
CAMERA_MOVEMENTS_RU = ["Плавный наезд (dolly in)", "Быстрый, резкий монтаж", "Медленное панорамирование", "Съемка со стедикама", "Вращение камеры", "Эффект 'вертиго'"]
LENS_EFFECTS_RU = ["Эффект 'рыбий глаз'", "Мягкий фокус с боке", "Анаморфотные блики", "Эффект миниатюры 'тильт-шифт'", "Глубокая резкость", "Засветка пленки"]
STYLES_RU = ["в стиле Уэса Андерсона", "гиперреализм", "как запись на VHS кассету 80-х", "кукольная анимация", "в стиле аниме студии Ghibli", "киберпанк", "стимпанк", "съемка на IMAX камеру", "в стиле картины барокко"]
TEMPORAL_ELEMENTS_RU = ["Замедленная съемка (slow motion)", "Ускоренная съемка (timelapse)", "Резкий стоп-кадр", "Обратная перемотка действия", "Эффект 'bullet time'"]
AUDIO_RU = ["Эпическая оркестровая музыка", "Звуки природы: шум дождя и пение птиц", "Тишина, прерываемая редкими шагами", "Электронная музыка в стиле 80-х", "Диалог шепотом", "Звук работающего двигателя", "Смех толпы"]

# --- Английские версии для промпта ---
CAMERA_ANGLES_EN = ["close-up shot", "extreme wide shot", "low-angle shot", "top-down shot", "dutch angle", "over-the-shoulder shot"]
CAMERA_MOVEMENTS_EN = ["dolly in", "fast cut editing", "slow panning", "steadicam shot", "360-degree rotation", "vertigo effect"]
LENS_EFFECTS_EN = ["fisheye lens", "soft focus with bokeh", "anamorphic lens flare", "tilt-shift effect", "deep focus", "light leak"]
STYLES_EN = ["in the style of Wes Anderson", "hyperrealistic, 8K", "80s VHS recording", "stop-motion animation", "Studio Ghibli anime style", "cyberpunk, neon-lit", "steampunk", "shot on IMAX film", "baroque painting"]
TEMPORAL_ELEMENTS_EN = ["slow motion", "timelapse", "freeze frame", "reverse motion", "bullet time effect"]
AUDIO_EN = ["epic orchestral music", "sounds of nature, rain and birds", "silence broken by footsteps", "80s electronic synth music", "whispered dialogue", "engine running sounds", "crowd laughing"]


# --- ИНТЕРАКТИВНЫЕ ФУНКЦИИ БОТА ---

def get_theme_keyboard(selected_themes):
    keyboard = []
    row = []
    for theme_name in THEMES:
        text = f"✅ {theme_name.capitalize()}" if theme_name in selected_themes else theme_name.capitalize()
        row.append(InlineKeyboardButton(text, callback_data=theme_name))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    if len(selected_themes) == 3:
        keyboard.append([InlineKeyboardButton("🚀 Создать Сценарий!", callback_data="generate")])
        
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['selected_themes'] = []
    keyboard = get_theme_keyboard([])
    await update.message.reply_text(
        "Привет! Я — AI-режиссер Габриэль.\n\n"
        "Пожалуйста, выбери три темы для создания уникального сценария.",
        reply_markup=keyboard
    )
    return SELECTING_THEMES

async def select_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    theme_name = query.data
    
    selected_themes = context.user_data.get('selected_themes', [])

    if theme_name == "generate":
        return await generate_script(update, context)

    if theme_name in selected_themes:
        selected_themes.remove(theme_name)
    elif len(selected_themes) < 3:
        selected_themes.append(theme_name)
        
    context.user_data['selected_themes'] = selected_themes
    
    keyboard = get_theme_keyboard(selected_themes)
    
    count = len(selected_themes)
    if count == 0:
        text = "Выбери три темы для создания уникального сценария."
    elif count == 1:
        text = f"Выбрано: {selected_themes[0].capitalize()}. Осталось две."
    elif count == 2:
        text = f"Выбрано: {selected_themes[0].capitalize()}, {selected_themes[1].capitalize()}. Осталась одна."
    else: # count == 3
        text = f"Отлично! Твой микс: {selected_themes[0].capitalize()}, {selected_themes[1].capitalize()}, {selected_themes[2].capitalize()}.\n\nНажми 'Создать Сценарий!'."

    await query.edit_message_text(text=text, reply_markup=keyboard)
    
    return SELECTING_THEMES


async def generate_script(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.edit_message_text(text="Принято! Создаю профессиональный сценарий для VEO, ищу душу в словаре Даля...")

    selected_themes = context.user_data.get('selected_themes', [])

    # Проверка, что словари загрузились
    if not all([NOUNS_RU, VERBS_RU, ADJECTIVES_RU]):
        await context.bot.send_message(chat_id=query.message.chat_id, text="К сожалению, не удалось загрузить словари из интернета. Попробуйте перезапустить бота позже.")
        return ConversationHandler.END

    # Генерация технической части сценария
    subject_ru = random.choice(NOUNS_RU)
    action_ru = random.choice(VERBS_RU)
    scene_ru = f"{random.choice(ADJECTIVES_RU)} пейзаж"
    angle_ru = random.choice(CAMERA_ANGLES_RU)
    movement_ru = random.choice(CAMERA_MOVEMENTS_RU)
    lens_ru = random.choice(LENS_EFFECTS_RU)
    style_ru = random.choice(STYLES_RU)
    temporal_ru = random.choice(TEMPORAL_ELEMENTS_RU)
    audio_ru = random.choice(AUDIO_RU)
    dahl_verb_ru = random.choice(GLAGOLY_DALYA_RU) # Выбираем душу проекта
    
    script_ru = (
        f"🎬 **Режиссерский сценарий (VEO)**\n\n"
        f"▪️ **Subject:** {subject_ru.capitalize()}\n"
        f"▪️ **Action:** {action_ru}\n"
        f"▪️ **Scene:** {scene_ru}\n"
        f"▪️ **Camera angles:** {angle_ru}\n"
        f"▪️ **Camera movements:** {movement_ru}\n"
        f"▪️ **Lens effects:** {lens_ru}\n"
        f"▪️ **Style:** {style_ru}\n"
        f"▪️ **Temporal elements:** {temporal_ru}\n"
        f"▪️ **Audio:** {audio_ru}\n\n"
        f"🎤 **Голос Габриэля:** *И при всем при этом он умудрился **{dahl_verb_ru}**.*"
    )

    # Генерация промпта для AI
    keywords_en = [kw for theme in selected_themes for kw in THEMES[theme]["keywords"]]
    
    # Имитация перевода для английского промпта
    subject_en = "a " + subject_ru 
    action_en = action_ru
    scene_en = "a " + scene_ru
    
    prompt_en = (
        f"Subject: {subject_en}, {' '.join(keywords_en)}\n"
        f"Action: {action_en}\n"
        f"Scene: {scene_en}\n"
        f"Camera angles: {random.choice(CAMERA_ANGLES_EN)}\n"
        f"Camera movements: {random.choice(CAMERA_MOVEMENTS_EN)}\n"
        f"Lens effects: {random.choice(LENS_EFFECTS_EN)}\n"
        f"Style: {random.choice(STYLES_EN)}\n"
        f"Temporal elements: {random.choice(TEMPORAL_ELEMENTS_EN)}\n"
        f"Audio: {random.choice(AUDIO_EN)}"
    )

    await context.bot.send_message(chat_id=query.message.chat_id, text=script_ru, parse_mode='Markdown')
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"🤖 **Промпт для VEO:**\n\n`{prompt_en}`", parse_mode='Markdown')
    
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Действие отменено. Напишите /start, чтобы начать снова.')
    context.user_data.clear()
    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Произошла ошибка: {context.error}")

def main() -> None:
    TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TOKEN:
        print("ОШИБКА: Токен не найден.")
        return

    application = Application.builder().token(TOKEN).build()
    
    application.add_error_handler(error_handler)
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_THEMES: [CallbackQueryHandler(select_theme, per_message=False)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    
    print(f"{PROJECT_NAME} запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()



