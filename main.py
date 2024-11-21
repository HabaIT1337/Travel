from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

# Состояния для этапов диалога
MAIN_MENU, SELECT_TRIP_TYPE, BOOKING_TRIP, BOOKING_PACKAGE, NAME, PHONE, DATE, DESTINATION, CONTACT_PHONE, CONFIRMATION = range(
    10)

# Переменные
admin_chat_id = '1387587155'  # ID администратора
dispatcher_contact = '@eduardhabib'  # Контакт диспетчера
seats_available = 20  # Начальное количество мест для каждого маршрута

# Информация о маршрутах с остановками, временем и стоимостью
routes_info = {
    "Краснодар - Домбай": """
🚐 Краснодар - Домбай  
⏰ Отправление: 6:00 или 16:00  
💰 Стоимость:
- 🏙 Армавир — *1000 ₽* 
- 🏙 Кочубеевское — *1500 ₽* 
- 🏙 Ивановская — *1500 ₽* 
- 🏙 Черкесск — *1500 ₽* 
- 🏙 Карачаевск — *2000 ₽* 
- 🏞 Теберда — *2500 ₽* 
- 🏔 Домбай — *2500 ₽* 
    """,
    "Домбай - Краснодар": """
🚐 Домбай - Краснодар  
⏰ Отправление: 14:30  
💰 Стоимость: такие же, как и в направлении "Краснодар - Домбай".
    """,
    "Краснодар - Архыз": """
🚐 Краснодар - Архыз  
⏰ Отправление: 6:00 или 16:00  
💰 Стоимость:
- 🏙 Майкоп — *800 ₽*  
- 🏙 Лабинск — *1000 ₽*  
- 🏙 Мостовской — *1200 ₽*  
- 🏙 Псебай — *1500 ₽*  
- 🏙 Курджиново — *1500 ₽*  
- 🏙 Преградная — *1800 ₽*  
- 🏙 Сторожевая — *2000 ₽*  
- 🏞 Зеленчукская — *2000 ₽*  
- 🏞 Архыз — *2500 ₽*  
    """,
    "Архыз - Краснодар": """
🚐 Архыз - Краснодар  
⏰ Отправление: 14:00  
💰 Стоимость: такие же, как и в направлении "Краснодар - Архыз".
    """
}


# Начальная функция, показывающая кнопку "Поехали! 🚀"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [[KeyboardButton("Поехали! 🚀")]]

    await update.message.reply_text(
        "Нажмите кнопку ниже, чтобы начать бронирование! 🚀",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return SELECT_TRIP_TYPE


# Функция для отображения описания и выбора типа услуги
async def select_trip_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["🚗 Поездка", "📦 Посылка", "🛠 Поддержка"]]
    await update.message.reply_text(
        "🚗 *Бронирование поездок и отправка посылок с лёгкостью!* 🚗\n\n"
        "Наш бот создан, чтобы сделать ваши поездки максимально удобными и комфортными. Всё, что вам нужно — выбрать маршрут и дату, а остальное мы берём на себя! 😎\n\n"
        "📍 *Доступные маршруты:*\n\n"
        "- Краснодар - Домбай 🏔\n"
        "- Краснодар - Архыз 🏞\n"
        "Промежуточные остановки в самых популярных местах 🛣\n\n"
        "📦 Также с нами можно отправить посылку: быстро и надёжно! 🎁\n\n"
        "Начните с кнопки «Поехали! 🚀», выберите свою поездку и наслаждайтесь лёгким процессом бронирования! 🚌✨",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return MAIN_MENU


# Основное меню, обрабатывающее выбор пользователя
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == "🚗 Поездка":
        route_options = [[f"🚍 {route}"] for route in routes_info.keys()] + [["🔙 Назад"]]
        await update.message.reply_text(
            "Пожалуйста, выберите маршрут:",
            reply_markup=ReplyKeyboardMarkup(route_options, resize_keyboard=True)
        )
        return BOOKING_TRIP
    elif user_choice == "📦 Посылка":
        context.user_data["route_type"] = "Посылка"
        await update.message.reply_text("Вы выбрали отправку посылки. Пожалуйста, введите своё имя для начала.",
                                        reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
        return BOOKING_PACKAGE
    elif user_choice == "🛠 Поддержка":
        await update.message.reply_text(
            f"Связаться с диспетчером можно по этому аккаунту: {dispatcher_contact}",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
        )
        return MAIN_MENU
    elif user_choice == "🔙 Назад":
        await select_trip_type(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите одну из доступных опций: Поездка, Посылка, или Поддержка.",
            reply_markup=ReplyKeyboardMarkup([["🚗 Поездка", "📦 Посылка", "🛠 Поддержка"]], resize_keyboard=True)
        )
        return MAIN_MENU


# Функция для бронирования поездки
async def booking_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_route = update.message.text.replace("🚍 ", "")
    context.user_data['route'] = selected_route
    await update.message.reply_text(
        f"Вы выбрали маршрут:\n\n{routes_info[selected_route]}\n\nВведите дату поездки (например, 15.10.2024).",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
    )
    return DATE


# Запрос даты и времени поездки
async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['date'] = update.message.text
    times_options = [["6:00", "16:00"], ["🔙 Назад"]]

    await update.message.reply_text(
        "Выберите время отправления:",
        reply_markup=ReplyKeyboardMarkup(times_options, resize_keyboard=True)
    )
    return DESTINATION


# Функция для выбора конечной остановки или назначения
async def destination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['time'] = update.message.text
    if context.user_data.get("route_type") == "Посылка":
        await update.message.reply_text("Введите номер телефона получателя для посылки.",
                                        reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
        return CONTACT_PHONE
    else:
        await update.message.reply_text("Введите своё имя.",
                                        reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
        return NAME


# Запрос имени
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите номер телефона для подтверждения бронирования.",
                                    reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
    return PHONE


# Запрос номера телефона для бронирования
async def contact_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['contact_phone'] = update.message.text
    await update.message.reply_text("Введите ваш номер телефона для подтверждения.",
                                    reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
    return PHONE


# Завершение бронирования и отправка данных администратору
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    selected_route = context.user_data['route']
    global seats_available

    if seats_available > 0:
        seats_available -= 1
        booking_info = (
            f"Новое бронирование!\n"
            f"Маршрут: {selected_route}\n"
            f"Дата: {context.user_data['date']} в {context.user_data['time']}\n"
            f"Имя: {context.user_data['name']}\n"
            f"Телефон: {context.user_data['phone']}\n"
            f"Контакт для встречи посылки: {context.user_data.get('contact_phone', 'не указано')}\n"
            f"Осталось мест: {seats_available}"
        )

        await context.bot.send_message(chat_id=admin_chat_id, text=booking_info)
        await update.message.reply_text("Ваше бронирование подтверждено. Мы свяжемся с вами для подтверждения.")
    else:
        await update.message.reply_text("Извините, но на данный момент все места заняты.")

    return MAIN_MENU


# Функция отмены бронирования
async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Бронирование отменено. Если хотите начать заново, нажмите 'Поехали!' 🚀.")
    return MAIN_MENU


# Основная функция
def main() -> None:
    application = ApplicationBuilder().token("7984620054:AAH2NIHnC-c1IDW0_g2KY5iz-lQoBgUpNos").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            SELECT_TRIP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_trip_type)],
            BOOKING_TRIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_trip)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            CONTACT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_phone)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel_booking)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()












