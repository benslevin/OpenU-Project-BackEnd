import os
from sys import exit
from enum import Enum
from dotenv import load_dotenv

# load .env file
load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

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
    BREAKEVEN = "breakeven"
    ADDCATEGORY = "addCategory"
    DELETECATEGORY = "deleteCategory"
    DASHBOARD = "dashboard"
    SET_PASSWORD = "setPassword" # give the user the option to change his password
    GET_LOGIN = "getLogin"
    SET_LOGIN = "setLogin"


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

categories_config = ["food", "groceries", "transport", "rent", "insurance","health", "education", "entertaiment", "travel", "pet", "childcare", "gas",  "shopping", "clothing", "other"]
categories_config_dict = {"food": "Food🍔", "groceries": "Groceries🛒", "transport": "Transport 🚗", "rent":"Rent 🏠", "insurance":" Insurance🏥","health":"Health⚕️", "education":"Education📚", "entertaiment": "Entertaiment🎬", "travel":"Travel✈️", "pet":"Pet🐾", "childcare": "Childcare👶", "gas": "Gas⛽",  "shopping": "Shopping🛒", "clothing": "Clothing👕", "other": "Other"}

#GLOBAL VALUES:
PASSWORD_MAX_LENGTH = 40
PASSWORD_MIN_LENGTH = 6
LOGIN_NAME_MAX_LENGTH = 12
LOGIN_NAME_MIN_LENGTH = 6
