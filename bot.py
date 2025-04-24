import os, asyncio, logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters
)

ASK_PHONE, ASK_NAME, ASK_CITY = range(3)
ADMIN_CHAT_ID = 245084180

async def start(update: Update, _):
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton('📞 Оставить заявку', request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        'Здравствуйте! Нажмите кнопку и поделитесь номером для бесплатной консультации.',
        reply_markup=kb)
    return ASK_PHONE

async def phone(update: Update, context):
    phone = (update.message.contact.phone_number
             if update.message.contact else update.message.text)
    context.user_data['phone'] = phone
    await update.message.reply_text('Спасибо! Как к вам обращаться?')
    return ASK_NAME

async def name(update: Update, context):
    context.user_data['name'] = update.message.text
    await update.message.reply_text('Из какого вы города?')
    return ASK_CITY

async def city(update: Update, context):
    context.user_data['city'] = update.message.text
    data = context.user_data
    await context.bot.send_message(
        ADMIN_CHAT_ID,
        f"Новая заявка:\nИмя: {data['name']}\nТелефон: {data['phone']}\nГород: {data['city']}")
    await update.message.reply_text('Спасибо! Юрист свяжется с вами сегодня.')
    return ConversationHandler.END

async def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(os.getenv('TOKEN')).build()
    conv = ConversationHandler(
        [CommandHandler('start', start)],
        {ASK_PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, phone)],
         ASK_NAME: [MessageHandler(filters.TEXT, name)],
         ASK_CITY: [MessageHandler(filters.TEXT, city)]},
        fallbacks=[CommandHandler('start', start)])
    app.add_handler(conv)
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())

