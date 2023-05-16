import uuid
from openu_project_backend.Responses import responses, get_price, get_category, valid_email, start_response, help_response
from openu_project_backend.config import TOKEN, BOT_USERNAME, Category, Button, Status, Command, categories_config, categories_config_dict
from openu_project_backend.backend import Database, get_categories, write_category, remove_category

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
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

    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    user_name = update.message.from_user.first_name
    group_name = update.message.chat.title
    user_id = update.message.from_user.id
    group_id = update.message.chat.id

    # checks of user enterd email and checks if it's valid
    if valid_email(update.message.text):
        response = db.add_user(user_id, user_name, email=update.message.text)
        await update.message.reply_text(response)
        return
    
    # check if user and group exists:
    response = db.exists(user_id, group_id, group_name)
    if response: 
        await update.message.reply_text(response) #user doesn't exists
        return
    
    all_categories = categories_config + get_categories(str(group_id))
    reply = responses(update.message.text)
    
    keyboard = [[]]
    j = 0
    for i, item in enumerate(all_categories):
        if i % 3 == 0 and i != 0:
            keyboard.append([])
            j += 1
        if item in categories_config:
            keyboard[j].append(InlineKeyboardButton(categories_config_dict[item], callback_data=item))
        else:
            keyboard[j].append(InlineKeyboardButton(item, callback_data=item))
        
    if update.message.text.isnumeric():  # user report only number -> bot will suggests categories
        if int(update.message.text) < 0:
            update.message.reply_text("Expense must be greater than 0", reply_markup=reply_markup)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(reply, reply_markup=reply_markup)
    else:
        await update.message.reply_text("You must enter a number")



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    msg = query.data
    await query.answer()
    group_id = query.message.chat.id

    responses = ["This Month", "Last Month", "All Time"]
    if msg in responses:
        result = db.total_expenses(group_id,msg)
        if not result:
            await query.message.reply_text(f'No expenses found')
            return
        db.piechart(group_id,msg)
        db.barchart(group_id,msg)
        await query.message.reply_text(f'Total expenses of the group is {result} ')
        await context.bot.send_photo(chat_id=group_id, photo=open('my_plot.png', 'rb'))
        await context.bot.send_photo(chat_id=group_id, photo=open('my_plot2.png', 'rb'))
        await query.message.delete()
        return

    if query.data == f"{Button.APPROVE.value}":
        price = get_price(query.message.text)
        category = get_category(query.message.text)

    else:  # Cancel button
        price = int(query.message.text)
        category = query.data

    user_id = query.message.reply_to_message.from_user.id
    user_name = query.message.reply_to_message.from_user.name
    date = query.message.date

    # add a new row to group table
    if query.message.chat.type == 'group':
        group_id = query.message.chat.id
        #group_name = query.message.chat.title
        db.new_expense(user_id, group_id, category, price)
        res = f"{user_name} spended {query.message.text} on {category}"
        await query.edit_message_text(text=res)

    # add a new row to private user table
    else:
        pass

# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# ---------------------- Commands ----------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do and create group for them in DB"""
    #TODO: XXX: !NICE TO HAVE! - FIRST MESSAGE - check if new group or load existing group
    
    #create new row in 'groups' table
    group_id = update.message.chat.id #get group_id = chat_id
    if update.message.chat.type == 'group':  #get group_name = chat_name / user name (in private chat)
        group_name = update.message.chat.title
    else:
        group_name = update.message.chat.first_name
    
    if not db.is_group_exists(group_id): #if group not exists
        group_auth_key = db.create_group(group_id=group_id, group_name=group_name)
    else: #if group exists - get auth
        group_auth_key = db.get_auth(group_id)
    
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
    await update.message.reply_text(help_response)


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/email ...' sign-in the user email with the group uuid into DB (for permissions to UI) """
    
    #get parameters of sender for new row in 'users' table
    sender_user_id = update.message.from_user.id
    sender_user_name = update.message.from_user.name
    sender_email = (update.message.text).split(Command.SIGN_IN.value)[1].strip() #get text (the email)
    #TODO: XXX: !NICE TO HAVE! verify email is correct 
    group_id = update.message.chat.id #get group_id = chat_id

    #verify user does not exists
    is_user_exists, user_info = db.is_user_exists(user_id=sender_user_id)
    if is_user_exists: #if already exists
        signed_email = user_info[0][2]
        if signed_email == sender_email: #and if he sent different email -> ask for changes
            await update.message.reply_text(f'hey {update.message.from_user.first_name}, your user is already exists in our datebase with the email:\n{signed_email}')
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
    
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return    

    keyboard = [
        [
            InlineKeyboardButton("This Month", callback_data="This Month"),
            InlineKeyboardButton("Last Month", callback_data="Last Month"),
            InlineKeyboardButton("All Time", callback_data="All Time")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a period of time", reply_markup=reply_markup)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    user_id = update.message.from_user.id
    group_id = update.message.chat.id
    deleted = db.delete(group_id, user_id)
    if deleted:
        await update.message.reply_text("Expenses deleted from the last Month!")
    else:
        await update.message.reply_text("Only the admin of the group can delete expenses!")



async def export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    db.toExcel(update.message.chat.id)
    await context.bot.send_document(chat_id=update.message['chat']['id'], document=open('expenses.xlsx', 'rb'))


async def breakeven(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    response = db.breakeven(update.message.chat.id)
    if not response:
        response = "There is no breakeven for this group"
    await update.message.reply_text(response)


async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    try:
        new_category = update.message.text.split()
        group_id = str(update.message.chat.id)
        added = write_category(group_id, new_category[1])
        await update.message.reply_text(added)
    except:
        await update.message.reply_text("an error has occured")


async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    try:
        new_category = update.message.text.split()
        group_id = str(update.message.chat.id)
        deleted = remove_category(group_id, new_category[1])
        await update.message.reply_text(deleted)
    except:
        await update.message.reply_text("an error has occured")


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    group_id = str(update.message.chat.id)
    link ="www.google.com"
    await update.message.reply_text(text = f"<a href='{link}'>dashboard</a>", parse_mode = "html")
    

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot avaible only for groups!')
        return

    group_id = str(update.message.chat.id)
    auth_code = db.get_auth(group_id)
    await update.message.reply_text(f"Your Authentication code is {auth_code}")

# ---------------------- Commands - END ----------------------- #


# Run the program
if __name__ == '__main__':
    db = Database()
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler(f"{Command.START.value}", start))
    app.add_handler(CommandHandler(f"{Command.HELP.value}", help_command))
    app.add_handler(CommandHandler(f"{Command.SIGN_IN.value}", email))
    app.add_handler(CommandHandler(f"{Command.DELETE.value}", delete))
    app.add_handler(CommandHandler(f"{Command.EXPORT.value}", export))
    app.add_handler(CommandHandler(f"{Command.STATS.value}", stats))
    app.add_handler(CommandHandler(f"{Command.BREAKEVEN.value}", breakeven))
    app.add_handler(CommandHandler(f"{Command.ADDCATEGORY.value}", add_category))
    app.add_handler(CommandHandler(f"{Command.DELETECATEGORY.value}", delete_category))
    app.add_handler(CommandHandler(f"{Command.DASHBOARD.value}", dashboard))
    app.add_handler(CommandHandler(f"{Command.AUTH.value}", auth))
    app.add_handler(CallbackQueryHandler(button))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')  # TODO: delete this debug line
    # Run the bot
    app.run_polling(poll_interval=1)
