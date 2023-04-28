import os
from sys import exit
from enum import Enum
from dotenv import load_dotenv
from typing import Final #A special typing construct to indicate to type checkers that a name cannot be re-assigned or overridden in a subclass

#load .env file
load_dotenv()

# BOT Token
#TOKEN: Final = '5673704938:AAH7bcLtTitCVkmYyoDNSnMTRyvUaI5VsKk' -Money_Friendly_Bot
TOKEN: Final = '6235208308:AAEpoDVVKMXFvsrOiG2_CZibVkEuc5Xx6Xg'

# BOT name ro identify in group chats
BOT_USERNAME: Final = '@MoneyMateIL_bot'

#DB info
DB_PORT = os.environ.get("DB_PORT")

#Commands
class Command(Enum):
    START = "start" #start conversation
    HELP = "help" #get information to how to use the bot
    TOTAL_EXPENSES = "total_expenses" #show total expenses
    NEW = "new" #add a new expense
    DELETE = "delete" #delete a new expenses
    SUM = "sum" #get the total expenses in a specific month or year in a pie chart histogram
    LIST = "list" #get a list of all your expenses in a specific month or year
    EXPORT = "export" #export the expenses of a given month as excel file
    STOP = "stop" #stops a recurring expense
    LINK = "link" #send fast UI link (NICE TO HAVE)

    


#buttons:
class Button(Enum):
    APPROVE = "Approve ✅"
    CANCEL = "Cancel ❌"

class Status(Enum):
    APPROVED = "Approved ✅"
    CANCELLED = "Cancelled ❌"
    

#categories:
class Category(Enum):
    FOOD = "food"
    GAS = "gas"
    GROCERIES = "groceries"
    SHOPPING = "shopping"
    CLOTHES = "clothes"
    ENTERTAIMENT = "entertaiment"
    ETC = "etc"
    #TODO: verify categories
