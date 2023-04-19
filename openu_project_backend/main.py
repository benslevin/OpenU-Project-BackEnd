from openu_project_backend.Responses import responses, get_price, get_category
from openu_project_backend.config import TOKEN, BOT_USERNAME, Category, Button, Status, Command
from openu_project_backend.backend import get_group_total_expenses, add_row, piechart
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

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    reply = responses(update.message.text)
    keyboard = [
        [
            InlineKeyboardButton(f"{Button.CANCEL.value}", callback_data=f"{Status.CANCELLED.value}"),
            InlineKeyboardButton(f"{Button.APPROVE.value}", callback_data=f"{Status.APPROVED.value}")
        ]
    ]

    keyboard2 = [
        [
        InlineKeyboardButton(f"{Category.GAS.value}⛽", callback_data=f"{Category.GAS.value}"),
        InlineKeyboardButton(f"{Category.FOOD.value}🍔", callback_data=f"{Category.FOOD.value}"),
        InlineKeyboardButton(f"{Category.SHOPPING.value}🛒", callback_data=f"{Category.SHOPPING.value}")
        ],
        [
        InlineKeyboardButton(f"{Category.CLOTHES.value}👕", callback_data=f"{Category.CLOTHES.value}"),
        InlineKeyboardButton(f"{Category.ENTERTAIMENT.value}🎦", callback_data=f"{Category.ENTERTAIMENT.value}"),
        InlineKeyboardButton(f"{Category.ETC.value}", callback_data=f"{Category.ETC.value}")
        ]
    ]
    if update.message.text.isnumeric(): #user report only number -> bot will suggests categories
        reply_markup = InlineKeyboardMarkup(keyboard2)
    else: #otherwise user report something like "Food 200"
        reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(reply, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    await query.edit_message_text(text=query.data)

    if query.data == f"{Button.APPROVE.value}":
        price = get_price(query.message.text)
        category = get_category(query.message.text)

    else: #Cancel button
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


# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    
    
#---------------------- Commands ----------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    #admins = update.get_bot().get_chat_administrators(update.message.chat.id)
    await update.message.reply_text("hi!")
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")

async def total_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    result = get_group_total_expenses()
    piechart()
    await update.message.reply_text(f'Total expenses of the group is {result} ')
    await context.bot.send_photo(chat_id=update.message['chat']['id'], photo=open('my_plot.png', 'rb'))

#---------------------- Commands - END ----------------------- #
    

# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler(f"{Command.START.value}", start))
    app.add_handler(CommandHandler(f"{Command.HELP.value}", help_command))
    app.add_handler(CommandHandler(f"{Command.TOTAL_EXPENSES.value}", total_expenses))
    app.add_handler(CallbackQueryHandler(button))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...') #TODO: delete this debug line
    # Run the bot
    app.run_polling(poll_interval=1)


