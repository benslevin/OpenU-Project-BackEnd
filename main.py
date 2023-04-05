from Responses import responses, get_price, get_category,  Token
from backend import get_group_total_expenses, add_row, piechart
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text("hi!")

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    reply = responses(update.message.text)
    keyboard = [
        [
            InlineKeyboardButton("ביטול ❌ ", callback_data="מבוטל❌"),
            InlineKeyboardButton("אישור ✅ ", callback_data="מאושר ✅")
        ]
    ]

    keyboard2 = [
        [
        InlineKeyboardButton("דלק⛽", callback_data="דלק"),
        InlineKeyboardButton("אוכל🍔", callback_data="אוכל"),
        InlineKeyboardButton("קניות🛒", callback_data="קניות")
        ],
        [
        InlineKeyboardButton("בגדים👕", callback_data="בגדים"),
        InlineKeyboardButton("בידור🎦", callback_data="בידור"),
        InlineKeyboardButton("אחר", callback_data="אחר"),
        ]
    ]
    if update.message.text.isnumeric():
        reply_markup = InlineKeyboardMarkup(keyboard2)
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(reply, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    await query.edit_message_text(text=query.data)

    if query.data == 'מאושר ✅':
        price = get_price(query.message.text)
        category = get_category(query.message.text)

    else:
        price = int(query.message.text)
        category = query.data

    message_id = query.message.message_id
    user_id = query.message.reply_to_message.from_user.id
    user_name = query.message.reply_to_message.from_user.name
    date = query.message.date


    # add a new row to group table
    if query.message.chat.type == 'group':
        group_id = query.message.chat.id
        group_name = query.message.chat.title
        add_row(message_id, group_id, group_name, user_id, user_name, category, price, date)

    # add a new row to private user table
    else:
        pass


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")

async def total_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    result = get_group_total_expenses()
    piechart()
    await update.message.reply_text(f'Total expenses of the group is {result} ')
    await context.bot.send_photo(chat_id=update.message['chat']['id'], photo=open('my_plot.png', 'rb'))

application = Application.builder().token(Token).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("total_expenses", total_expenses))
application.add_handler(CallbackQueryHandler(button))
application.run_polling()
