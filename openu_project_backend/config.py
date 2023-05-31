import os
from sys import exit
from enum import Enum
from dotenv import load_dotenv
#from typing import \
#Final  # A special typing construct to indicate to type checkers that a name cannot be re-assigned or overridden in a subclass

# load .env file
load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"
# BOT Token
# TOKEN: Final = '5673704938:AAH7bcLtTitCVkmYyoDNSnMTRyvUaI5VsKk' #-Money_Friendly_Bot
#TOKEN: Final = '6235208308:AAEpoDVVKMXFvsrOiG2_CZibVkEuc5Xx6Xg' #-MoneyMateIL_bot
#TOKEN: Final = '6186969245:AAGNbZJG8cH2etqCiKkhi6zmqZ5X16VrF3A'
#OKEN = '6186969245:AAGNbZJG8cH2etqCiKkhi6zmqZ5X16VrF3A'
TOKEN = '6274493416:AAHka4PzyLkVBmdoW-KFXAeCZUf9EuXIHe8'
# BOT name ro identify in group chats
#BOT_USERNAME = '@sadna1_bot'
BOT_USERNAME = '@MoneyMate_ExpenseBot'

#DB info
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_DATABASE_NAME = os.environ.get("DB_DATABASE_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "sadna_admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Password1")
DB_PORT = os.environ.get("DB_PORT", "5432")

# telegram info
# TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Commands
class Command(Enum):
    START = "start"  # start conversation
    HELP = "help"  # get information to how to use the bot
    STATS = "stats"  # show stats of the group
    NEW = "new"  # add a new expense
    DELETE = "delete"  # delete a new expenses
    SUM = "sum"  # get the total expenses in a specific month or year in a pie chart histogram
    LIST = "list"  # get a list of all your expenses in a specific month or year
    EXPORT = "export"  # export the expenses of a given month as excel file
    STOP = "stop"  # stops a recurring expense
    LINK = "link"  # send fast UI link (NICE TO HAVE)
    BREAKEVEN = "breakeven"
    ADDCATEGORY = "addCategory"
    DELETECATEGORY = "deleteCategory"
    DASHBOARD = "dashboard"
    GET_PASSOWRD = "getPassword" # send the user his password in private chat
    SET_PASSWORD = "newPassword" # give the user the option to change his password
    GET_LOGIN = "getLogin"
    SET_LOGIN = "setLogin"
    SIGN_IN = "email" # create user in 'users' table


# buttons:
class Button(Enum):
    APPROVE = "Approve ✅"
    CANCEL = "Cancel ❌"


class Status(Enum):
    APPROVED = "Approved ✅"
    CANCELLED = "Cancelled ❌"


# categories:
class Category(Enum):
    FOOD = "food"
    GAS = "gas"
    GROCERIES = "groceries"
    SHOPPING = "shopping"
    CLOTHES = "clothes"
    ENTERTAIMENT = "entertaiment"
    OTHER = "other"
    # TODO: verify categories

categories_config = ["food", "gas", "groceries", "shopping", "clothes", "pleasure", "other"]
categories_config_dict = {"food": "Food 🍔", "gas": "Gas ⛽", "groceries": "Groceries🍎", "shopping": "Shopping🛒", "clothes": "Clothes👕", "pleasure": "Pleasure🎦", "other": "Other"}
