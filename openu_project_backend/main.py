import uuid
from openu_project_backend.Responses import responses, get_price, get_category
from openu_project_backend.config import TOKEN, BOT_USERNAME, Category, Button, Status, Command
from openu_project_backend.backend import get_group_total_expenses, add_row, piechart, Database
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

#globals:
db = Database()

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
    """Inform user about what this bot can do and create group for them in DB"""
    
    global db #declare global
    
    #TODO: XXX: !NICE TO HAVE! - FIRST MESSAGE - check if new group or load existing group
    
    #create new row in 'groups' table
    group_id = update.message.chat.id #get group_id = chat_id
    if update.message.chat.type == 'group':  #get group_name = chat_name / username (in private chat)
        group_name = update.message.chat.title
    else:
        group_name = update.message.chat.username
        
    group_auth_key = db.create_group(group_id=group_id, group_name=group_name)
    
    # ~~ FIRST MESSAGE ~~ (welcome)
    await update.message.reply_text("Hey there!, \nThank you for added me, I will help you to track your expenses.")
    
    # ~~ SECOND MESSAGE ~~ (share auth with group)
    await update.message.reply_text(f"your login auth is: {group_auth_key},\nfor future login to our UI")
    
    # ~~ THIRD MESSAGE ~~ (instruct to use '/email' command)
    #if it is a group
    if update.message.chat.type == 'group': 
        await update.message.reply_text(f"Please each of you provide me your emails for login premissions to our UI, e.g:\n'/{Command.SIGN_IN.value} sagivabu@gmail.com'")
    else: 
        await update.message.reply_text(f"Please provide me your email for login premissions to our UI, e.g:\n'/{Command.SIGN_IN.value} sagivabu@gmail.com'")
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")

async def total_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    result = get_group_total_expenses()
    piechart()
    await update.message.reply_text(f'Total expenses of the group is {result} ')
    await context.bot.send_photo(chat_id=update.message['chat']['id'], photo=open('my_plot.png', 'rb'))

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/email ...' sign-in the user email with the group uuid into DB (for permissions to UI) """
    
    global db #declare global
    
    #get parameters of sender for new row in 'users' table
    sender_user_id = update.message.from_user.id
    sender_user_name = update.message.from_user.username
    sender_email = (update.message.text).strip() #get text (the email)
    #TODO: XXX: !NICE TO HAVE! verify email is correct 
    group_id = update.message.chat.id #get group_id = chat_id

    #verify user does not exists
    is_user_exists, user_info = db.is_user_exists(user_id=sender_user_id)
    if is_user_exists: #if already exists
        if user_info[2] == sender_email: #and if he sent different email -> ask for changes
            await update.message.reply_text(f'hey {update.message.from_user.first_name}, your user is already exists in our datebase with the email:\n{user_info}')
            #TODO: !NICE TO HAVE! would you like to change the email? (button of (Accept / Decline))
            #TODO: !NICE TO HAVE! NOAM - how to add button to accept changes
            
            
    else: #if user does not exists in 'users' table  
        db.create_user(user_id=sender_user_id, user_name=sender_user_name, email=sender_email, is_admin=0)
    
    
    #CREATE connection between user and group in 'usergroups' table
    connection = db.is_usergroups_row_exists(user_id=sender_user_id, group_id=group_id) #check if connection already exists
    if not connection: #if connection NOT exists
        #create connetcion (row) in 'usergroups' table
        chat_admins = await update.effective_chat.get_administrators() #get administrators list
        if update.effective_user in (admin.user for admin in chat_admins): #if sender is admin
            db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=1)
        else: #user is not admin
            db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=0)
            
    return

#TODO: @@@ STOPPED HERE @@@ - need to test start and email and merge branches
    
#---------------------- Commands - END ----------------------- #
    

# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler(f"{Command.START.value}", (start,db)))
    app.add_handler(CommandHandler(f"{Command.HELP.value}", help_command))
    app.add_handler(CommandHandler(f"{Command.TOTAL_EXPENSES.value}", total_expenses))
    app.add_handler(CommandHandler(f"{Command.SIGN_IN.value}", email))
    app.add_handler(CallbackQueryHandler(button))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...') #TODO: delete this debug line
    # Run the bot
    app.run_polling(poll_interval=1)


