
import os
import sys
import uuid

from openu_project_backend.Responses import responses, get_price, get_category, valid_email, help_response
from openu_project_backend.config import TOKEN, BOT_USERNAME, Category, Button, Status, Command, categories_config, categories_config_dict, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, LOGIN_NAME_MIN_LENGTH, LOGIN_NAME_MAX_LENGTH
from openu_project_backend.backend import Database, get_categories, write_category, remove_category, valid_input
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

    group_admin_flag = False #flag if the user is group admin
    group_type = update.message.chat.type
    if group_type == 'private':
        group_id = update.message.from_user.id
        group_name = update.message.from_user.first_name
        group_admin_flag = True
    else:
        group_id = update.message.chat.id
        group_name = update.message.chat.title
        chat_admins = await update.effective_chat.get_administrators() #get administrators list
        if update.effective_user in (admin.user for admin in chat_admins): #if sender is admin
            group_admin_flag = True

    user_name = update.message.from_user.first_name
    user_id = update.message.from_user.id
    
    # check if user and group exists:
    
    response = db.exists(user_id, user_name, group_id, group_name, group_admin_flag, update)
    if response: 
        await update.message.reply_text(response) #user doesn't exists
        return

    all_categories = categories_config + get_categories(str(group_id))

    is_invalid_input = valid_input(update.message.text)
    if is_invalid_input:
        pass #if invalid input - do nothing for now
        #await update.message.reply_text(is_invalid_input)

    else:
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

        keyboard[j].append(InlineKeyboardButton("Cancel ❌", callback_data="cancel"))
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(update.message.text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    
    query = update.callback_query
    msg = query.data
    await query.answer()
    group_id = query.message.chat.id
    
    # cancel button:
    if msg == "cancel":
        await query.edit_message_text(text="Cancelled")
        return
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
        if query.message.chat.type == 'group':
            await context.bot.send_photo(chat_id=group_id, photo=open('my_plot2.png', 'rb'))
        await query.message.delete()
        return
    
    price = int(query.message.text)
    category = query.data
    
    if query.message.chat.type == 'group':
        user_id = query.message.reply_to_message.from_user.id
        user_name = query.message.reply_to_message.from_user.name
        db.new_expense(user_id, group_id, category, price)
        res = f"{user_name} spended {query.message.text} on {category}"
        await query.edit_message_text(text=res)

    else:
        db.new_expense(group_id, group_id, category, price)
        res = f"You spended {query.message.text} on {category}"
        await query.edit_message_text(text=res)
        
# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# ---------------------- Commands ----------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do and create group for them in DB"""
    #TODO: XXX: !NICE TO HAVE! - FIRST MESSAGE - check if new group or load existing group
    
    #get group_id and group_name (if group/private)
    group_id = update.message.chat.id #get group_id = chat_id
    group_type = update.message.chat.type
    if group_type == 'group':  #get group_name = chat_name / user name (in private chat)
        group_name = update.message.chat.title
    else:
        group_name = update.message.chat.first_name
    
    #create group if not already exists
    if not db.is_group_exists(group_id):
        db.create_group(group_id=group_id, group_name=group_name)
    
    # ~~ FIRST MESSAGE ~~ (welcome)
    await update.message.reply_text("Thank you for adding me, I will help you to track your expenses.")
    
    # ~~ SECOND MESSAGE ~~ (instruct to use '/email' command)
    #if it is a group
    if group_type == 'group': 
        await update.message.reply_text(f"Please each of you provide me your username for login permissions to our website, e.g:\n'/{Command.SIGN_IN.value} sagivabu'")
        #NOTE: need to guide them to use SIGN_IN if this is a new group
    else: 
        await update.message.reply_text(f"Please provide me your username for login permissions to our website, e.g:\n'/{Command.SIGN_IN.value} sagivabu'")
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(help_response)

async def sign_in(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/signin LOGIN_NAME' sign-in the user with given login_name into DB (for permissions to website) """
    #get parameters of sender for new row in 'users' table
    sender_user_id = update.message.from_user.id
    sender_user_name = update.message.from_user.name
    sender_loginname = (update.message.text).split(Command.SIGN_IN.value)[1].strip() #get text (the loginname)
    group_id = update.message.chat.id #get group_id = chat_id
    last_message_flag = False #to cut messages early

    #check if user exists and get his user's info from DB
    is_user_exists, user_info = db.is_user_exists(user_id=sender_user_id)
    
    #if user is exists
    if is_user_exists: 
        signed_loginname = user_info[0][2] #get loginname from user_info
        if signed_loginname != sender_loginname: #and if he sent different loginname -> ask for changes
            await update.message.reply_text(f'hey {update.message.from_user.first_name}, your user is already signed-in with the login name:\n{signed_loginname}')
            await update.message.reply_text(f"To change the login name please use the next command: '/{Command.SET_LOGIN.value} YOUR_NEW_LOGIN_NAME'")
            last_message_flag = True
            #TODO: !NICE TO HAVE! would you like to change the loginname? (button of (Accept / Decline))
            #TODO: !NICE TO HAVE! NOAM - how to add button to accept changes
            
        if db.get_password(sender_user_id) == None: #if password not exists
            db.set_password(user_id=sender_user_id, password=f"{uuid.uuid4()}")
            await update.message.reply_text(f"hey {update.message.from_user.first_name}, I have generated you a new password.\nPlease use '/{Command.GET_PASSOWRD.value}' command in a private chat with me.")
            
    #if user is NOT exists
    else:
        temp_password = f"{uuid.uuid4()}" #generate new password  
        succeed = db.create_user(user_id=sender_user_id, user_name=sender_user_name, login_name=sender_loginname, password=temp_password, is_admin=0)
        if not succeed:
            await update.message.reply_text(f"hey {update.message.from_user.first_name}, your login_name should be between [{LOGIN_NAME_MIN_LENGTH}-{LOGIN_NAME_MAX_LENGTH}] charatcers")
        else:
            await update.message.reply_text(f"hey {update.message.from_user.first_name}, I have generated you a new password for our website.\nPlease use '/{Command.GET_PASSOWRD.value}' command in a private chat with me.")
            await update.message.reply_text(f"To change the password please use the next command in a private chat with me: '/{Command.SET_PASSWORD.value} YOUR_NEW_PASSWORD'")

    #CREATE connection between user and group in 'usergroups' table
    connection = db.is_usergroups_row_exists(user_id=sender_user_id, group_id=group_id) #check if connection already exists
    if not connection: #if connection NOT exists
        
        #on group chat
        group_type = update.message.chat.type
        if group_type == 'group':
            chat_admins = await update.effective_chat.get_administrators() #get administrators list
            if update.effective_user in (admin.user for admin in chat_admins): #if sender is admin
                db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=1)
                await update.message.reply_text(f"hey {update.message.from_user.first_name}, I have added your account admin permissions for this group")
            else: #user is not admin
                db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=0)
                await update.message.reply_text(f"hey {update.message.from_user.first_name}, I have added your account viewer permissions for this group")
                
        #on private chat
        else:
            db.create_usergroups(user_id=sender_user_id, group_id=group_id, is_group_admin=1)
            await update.message.reply_text(f"hey {update.message.from_user.first_name}, I have added your account admin permissions for this chat")
    
    else:
        if last_message_flag == False:
            await update.message.reply_text(f"hey {update.message.from_user.first_name}, you already signed-in and have permissions to our website")
        
    return

async def set_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/setLogin ....' - set a new login_name for the user """
        
    #set the new login_name for this user
    sender_user_id = update.message.from_user.id
    try:
        sender_loginname = (update.message.text).split(Command.SET_LOGIN.value)[1].strip() #get the text after the command (the loginname)
    except:
        await update.message.reply_text(f"hey {update.message.from_user.first_name}, please send this command in the format of '/{Command.SET_LOGIN.value} YOUR_LOGIN_NAME'")
    succeed = db.set_login_name(sender_user_id, login_name=sender_loginname) #get None if failed
    if succeed == None:
        await update.message.reply_text(f'hey {update.message.from_user.first_name}, your new login_name should be between [{LOGIN_NAME_MIN_LENGTH}-{LOGIN_NAME_MAX_LENGTH}] charatcers')
    else:
        await update.message.reply_text(f"hey {update.message.from_user.first_name}, your new login_name has been updated to: '{succeed}'")

async def get_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/getLogin' - send the user his login_name """
    
    #get the login_name from db
    sender_user_id = update.message.from_user.id
    login = db.get_login(sender_user_id)
    
    #send login_name
    if login:
        await update.message.reply_text(f"Hello, your login name for our website is: {login}")
    else:
        await update.message.reply_text(f"hey {update.message.from_user.first_name}, please sign-in first using the next command: '/{Command.SIGN_IN.value} YOUR_LOGIN_NAME''")

async def set_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/setPassword ....' - set a new password for the user """
    
    #verify it is private chat
    group_type = update.message.chat.type
    if group_type == 'group':  #get group_name = chat_name / user name (in private chat)
        await update.message.reply_text(f'hey {update.message.from_user.first_name}, this command can only be used in a private chat with me')
        return
        
    #set the new password for this user
    sender_user_id = update.message.from_user.id
    try:
        sender_password = (update.message.text).split(Command.SET_PASSWORD.value)[1].strip() #get the text after the command (the password)
    except:
        await update.message.reply_text(f"hey {update.message.from_user.first_name}, please send this command in the format of '/{Command.SET_PASSWORD.value} YOUR_PASSWORD'")
    succeed = db.set_password(sender_user_id, password=sender_password) #get None if failed
    if succeed == None:
        await update.message.reply_text(f'hey {update.message.from_user.first_name}, your new password should be between [{PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH}] charatcers')
    else:
        await update.message.reply_text(f"hey {update.message.from_user.first_name}, your new password has been updated to: '{succeed}'")

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ '/getPassword' - send the user his password in private chat """
    
    #verify it is private chat
    group_type = update.message.chat.type
    if group_type == 'group':  #get group_name = chat_name / user name (in private chat)
        await update.message.reply_text(f'hey {update.message.from_user.first_name}, this command can only be used in a private chat with me')
        return
        
    #get the password from db
    sender_user_id = update.message.from_user.id
    password = db.get_password(sender_user_id)
    
    #send password in private chat
    if password:
        await update.message.reply_text(f"Hello, your password for our website is: {password}")
    else:
        await update.message.reply_text(f"hey {update.message.from_user.first_name}, please sign-in first using the next command: '/{Command.SIGN_IN.value} YOUR_LOGIN_NAME''")
        
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

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
        group_id = update.message.from_user.id
    else:
        group_id = update.message.chat.id

    user_id = update.message.from_user.id
    msg = update.message.text.split()
    if len(msg) == 2:
        delete_time = msg[1]
    elif len(msg) == 1:
        delete_time = 'latest'
    else:
        await update.message.reply_text("could not procces this command")
        return
    
    deleted = db.delete(group_id, user_id, delete_time)
    await update.message.reply_text(deleted)

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.chat.type == 'private':
        print(update.message.chat.id)
    else:
        db.toExcel(update.message.chat.id)
        await context.bot.send_document(chat_id=update.message['chat']['id'], document=open('expenses.xlsx', 'rb'))

async def breakeven(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.message.chat.type == 'private':
        await update.message.reply_text(f'This bot is available only for groups')
        return

    response = db.breakeven(update.message.chat.id)
    if not response:
        response = "There is no breakeven for this group"
    await update.message.reply_text(response)

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message.chat.type == 'private':
        group_id = update.message.from_user.id
    else:
        group_id = update.message.chat.id

    try:
        new_category = update.message.text.split()
        added = write_category(group_id, new_category[1])
        await update.message.reply_text(added)
    except:
        await update.message.reply_text("an error has occured")

async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message.chat.type == 'private':
        group_id = update.message.from_user.id
    else:
        group_id = update.message.chat.id

    try:
        new_category = update.message.text.split()
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
    

# ---------------------- Commands - END ----------------------- #


# Run the program
if __name__ == '__main__':
    #sys.stdout.reconfigure(encoding='utf-8')
    db = Database()
    
    #os.environ["PYTHONIOENCODING"] = "utf-8"
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler(f"{Command.START.value}", start))
    app.add_handler(CommandHandler(f"{Command.HELP.value}", help_command))
    app.add_handler(CommandHandler(f"{Command.SIGN_IN.value}", sign_in))
    app.add_handler(CommandHandler(f"{Command.SET_LOGIN.value}", set_login))
    app.add_handler(CommandHandler(f"{Command.GET_LOGIN.value}", get_login))
    app.add_handler(CommandHandler(f"{Command.SET_PASSWORD.value}", set_password))
    app.add_handler(CommandHandler(f"{Command.GET_PASSOWRD.value}", get_password))
    app.add_handler(CommandHandler(f"{Command.STATS.value}", stats))
    app.add_handler(CommandHandler(f"{Command.DELETE.value}", delete))
    app.add_handler(CommandHandler(f"{Command.EXPORT.value}", export))
    app.add_handler(CommandHandler(f"{Command.BREAKEVEN.value}", breakeven))
    app.add_handler(CommandHandler(f"{Command.ADDCATEGORY.value}", add_category))
    app.add_handler(CommandHandler(f"{Command.DELETECATEGORY.value}", delete_category))
    app.add_handler(CommandHandler(f"{Command.DASHBOARD.value}", dashboard))
    app.add_handler(CallbackQueryHandler(button))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')  # TODO: delete this debug line
    # Run the bot
    app.run_polling(poll_interval=1)
