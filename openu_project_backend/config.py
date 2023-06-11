import os
from sys import exit
from enum import Enum
from dotenv import load_dotenv
from typing import \
    Final  # A special typing construct to indicate to type checkers that a name cannot be re-assigned or overridden in a subclass

# load .env file
load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

#DB info
DB_HOST = os.environ.get("DB_HOST")
DB_DATABASE_NAME = os.environ.get("DB_DATABASE_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")


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
    SET_PASSWORD = "setPassword" # give the user the option to change his password
    GET_LOGIN = "getLogin"
    SET_LOGIN = "setLogin"
    SIGN_IN = "signin" # create user in 'users' table


# buttons:
class Button(Enum):
    APPROVE = "Approve ✅"
    CANCEL = "Cancel ❌"

# status:
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


#GLOBAL VALUES:
PASSWORD_MAX_LENGTH = 40
PASSWORD_MIN_LENGTH = 6
LOGIN_NAME_MAX_LENGTH = 12
LOGIN_NAME_MIN_LENGTH = 6
