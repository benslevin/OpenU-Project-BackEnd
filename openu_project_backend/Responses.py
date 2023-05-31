import re

def responses(input_text):
    user_message = str(input_text).lower()

    msg = user_message.split()
    return user_message

def get_price(input_text):
    msg = input_text.split()
    for s in msg:
        if s.isnumeric():
            return s

def get_category(input_text):
    msg = input_text.split()
    for s in msg:
        if not s.isnumeric():
            return s

def valid_email(email):
    if len(email) > 7:
        if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email) != None:
            return True
        

start_response = "Welcome to MoneyMate bot!\nThis bot helps you manage and track your expenses in groups.\nFor more information, type /help"

help_response = "Initial setup\nAdd the bot to a group and than you cant start writing expenses.\nFor example, type 50 to add an expense and then select category.\nfor more commands, type / and you will see all the commands\n"