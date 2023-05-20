import uuid
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import random
import json
from collections import defaultdict
from openu_project_backend import config
from openu_project_backend.config import categories_config

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host =      config.DB_HOST,
            database =  config.DB_DATABASE_NAME,
            user =      config.DB_USER,
            password =  config.DB_PASSWORD,
            port =  int(config.DB_PORT))
        
        self.cur = self.conn.cursor()
        
    def new_expense(self, user_id,group_id, category, price):
        self.cur.execute("INSERT INTO userproducts (fk_user_id,fk_group_id,category_name,amount) VALUES (%s, %s, %s ,%s)",(user_id, group_id,category, price))
        self.conn.commit()


    def insert(self, message_id, group_id, group_name, user_id, user_name, category, price):
        self.cur.execute("INSERT INTO db VALUES (?,?,?,?,?,?,?)",(message_id, group_id, group_name, user_id, user_name, category, price))
        self.conn.commit()

    def delete(self,group_id, user_id):
        self.cur.execute(f"select role from usergroups where fk_group_id = {group_id} and fk_user_id = {user_id} ")
        user_role = self.cur.fetchone()[0]
        if user_role == 1:
            self.cur.execute(f"DELETE FROM userproducts WHERE fk_group_id = {group_id} and EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE)")
            self.conn.commit()

        return user_role

    def toExcel(self, group_id):
        query = f"select u.user_name as user, category_name as category, amount as price from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id}"
        df = pd.read_sql(query, self.conn)
        df.to_excel("expenses.xlsx", index=False)  

    def piechart(self, group_id, date):
        if date == "This Month":
            query = f"SELECT category_name, SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY category_name"
        elif date == "Last Month":
            query = f"SELECT category_name, SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE) -1 AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY category_name"
        else:
            query = f"SELECT category_name, SUM(amount) FROM userproducts where fk_group_id = {group_id} GROUP BY category_name"
        
        self.cur.execute(query)
        data = self.cur.fetchall()
        # create lists of categories and total prices
        categories = [row[0][::1] for row in data]
        prices = [row[1] for row in data]

        plt.pie(prices, labels=categories, autopct='%1.1f%%')
        plt.axis('equal')
        plt.title('Expenses')
        plt.savefig('my_plot.png')
        plt.clf()

    def barchart(self,group_id, date):
        if date == "This Month":
            query = f"select u.user_name, sum(amount) from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} AND EXTRACT(MONTH FROM up.date_created) = EXTRACT(MONTH FROM CURRENT_DATE) group by u.user_name"
        elif date == "Last Month":
            query = f"select u.user_name, sum(amount) from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} AND EXTRACT(MONTH FROM up.date_created) = EXTRACT(MONTH FROM CURRENT_DATE) -1 group by u.user_name"
        else:
            query = f"select u.user_name, sum(amount) from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} group by u.user_name"
        
        self.cur.execute(query)
        data = self.cur.fetchall()
        # create lists of categories and total prices
        users = [row[0][::1] for row in data]
        prices = [row[1] for row in data]

        plt.bar(users, prices)
        plt.xlabel('user')
        plt.ylabel('amount spend')
        plt.title('Expenses by users')
        plt.savefig('my_plot2.png')
        plt.clf()

    def total_expenses(self, group_id, date):
        if date == "This Month":
            self.cur.execute(f'SELECT SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE)')

        elif date == "Last Month":
            self.cur.execute(f'SELECT SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE)-1 AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE)')
        else:
           self.cur.execute(f'SELECT SUM(amount) FROM userproducts where fk_group_id = {group_id}') 
        return self.cur.fetchone()[0]

    def exists(self,user_id, group_id, group_name):

        #check if user exists
        self.cur.execute(f"select * from users where pk_id = {user_id}")
        user = self.cur.fetchall()
        if not user:
            return "Please enter Email first!"
            #self.cur.execute("INSERT INTO users (pk_id,user_name,email,is_admin) VALUES (%s, %s, %s, %s)",(user_id, user_name, email, 0))
            #self.conn.commit()
        
        # check if group exists
        self.cur.execute(f"select * from groups where pk_id = {group_id}")
        group= self.cur.fetchall()
        if not group:
            auth = random.randint(10000,99999)
            self.cur.execute("INSERT INTO groups (pk_id,group_name,auth) VALUES (%s,%s,%s)",(group_id,group_name,auth))
            self.conn.commit()

        # check if user is in group:
        self.cur.execute(f"select * from usergroups where fk_user_id = {user_id} and fk_group_id = {group_id}")
        usergroups= self.cur.fetchall()
        if not usergroups:
            if group:
                role = 0
            else:
                role = 1
            self.cur.execute("INSERT INTO usergroups (fk_user_id,fk_group_id, role) VALUES (%s, %s, %s)",(user_id, group_id, role))
            self.conn.commit()

    def add_user(self,user_id,user_name, email):
        #check if user exists

        email = email.lower()
        #check if email already in the db:
        self.cur.execute(f"select * from users where email = '{email}'")
        email_in_db = self.cur.fetchall()
        if email_in_db:
            return "Email already in the db"
        

        self.cur.execute(f"select * from users where pk_id = {user_id}")
        user = self.cur.fetchall()
        if not user:
            self.cur.execute("INSERT INTO users (pk_id,user_name,email,is_admin) VALUES (%s, %s, %s, %s)",(user_id, user_name, email, 0))
            self.conn.commit()
            return "User added"
        #update 
        else:
            return "User already has email"

    def breakeven(self, group_id):
        
        self.cur.execute(f"select u.user_name, sum(amount)from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} group by u.user_name")
        data = self.cur.fetchall()
        if not data:
            return "No expenses to split"
        balances = []
        sum = 0
        average = 0
        result = ""
        # חישוב המוצע שכל אדם צריך לשלם
        for person in data:
            sum += person[1]
        average = sum / len(data)
        # חישוב המאזן של כל אדם
        for person in data:
            balances.append([person[0], average - person[1]])
        for b1 in balances:
            if b1[1] > 0:
                for b2 in balances:
                    if b2[1] < 0:
                        if b1[1] <= -b2[1]: # b1 pay all his debt to b2
                            result += b1[0] + " owe " + b2[0] + " " + str(round(b1[1])) + " ₪\n"
                            b2[1] = b2[1] + b1[1]
                            b1[1] = 0
                            break
                        else: # b1 pay part of his debt to b2
                            result += b1[0] + " owe " + b2[0] + " " + str(round(-b2[1])) + " ₪\n"
                            b1[1] = b1[1] + b2[1]
                            b2[1] = 0
        return result

    def get_auth(self, group_id):
        self.cur.execute(f"select auth from groups where pk_id = {group_id}")
        row = self.cur.fetchone()[0]
        return row
    
    def create_group(self, group_id, group_name) -> None:
        ''' create group in 'groups' table '''
        self.cur.execute(f"INSERT INTO groups (pk_id, group_name) VALUES ('{group_id}', '{group_name}')")
        self.conn.commit()
    
    def is_group_exists(self, group_id) -> None:
        ''' Check if group exists, return True / False'''
        #check if group_id exists
        self.cur.execute(f"select * from groups where pk_id = {group_id}")
        group = self.cur.fetchall() #return list of tuples
        if group:
            return True
        else:
            return False
    
    def get_password(self, user_id) -> str:
        ''' Get password from user_id '''
        #get password following given user_id
        self.cur.execute(f"select password from users where pk_id = {user_id}")
        password = self.cur.fetchall()[0][0] #return list of tuples thats why
        if password:
            return password
        else:
            return None
        
    def new_password(self, user_id, password) -> str:
        ''' set new password for user_id, return None if failed, return password if valid '''
        #validate password #NOTE: XXX: !NICE TO HAVE! more validation cases
        if len(password) < 6: return None
        if len(password) > 40: return None
        
        #set new password in db
        self.cur.execute(f"UPDATE users SET password = '{password}' WHERE pk_id = {user_id}")
        self.conn.commit()
        
        return password
    
    
    def create_user(self, user_id, user_name, email, is_admin) -> str:
        ''' create user in 'users' table '''
        random_password = f"{uuid.uuid4()}" #generate new password
        
        self.cur.execute(f"INSERT INTO users (pk_id, user_name, email, is_admin, password) VALUES ('{user_id}', '{user_name}', '{(email).lower()}', '{is_admin}', '{random_password}')")
        self.conn.commit()
        
        return random_password
    
    def is_user_exists(self, user_id) -> tuple[bool, str]:
        ''' Check if user exists.\n
            Return (True, string of the details about the user) if exists,\n
            Return (False, None) if not exists'''
            
        #check if user_id exists
        self.cur.execute(f"select * from users where pk_id = {user_id}")
        user = self.cur.fetchall() #return list of tuples
        if user:
            return True, user
        else:
            return False, None
        
    def is_email_exists(self, email) -> bool:
        ''' Check if email exists '''
        #check if email exists #NOTE: stupid verification instead of googleAPI to prevent from UI to collapse because of 2 rows with identifiy emails
        self.cur.execute(f"select * from users where email = {email}")
        email = self.cur.fetchall() #return list of tuples
        if email:
            return True
        else:
            return False
        
    def create_usergroups(self, user_id, group_id, is_group_admin) -> None:
        ''' create connection (row) in 'usergroups' table '''
        self.cur.execute(f"INSERT INTO usergroups (fk_user_id, fk_group_id, role) VALUES ('{user_id}', '{group_id}', '{is_group_admin}')")
        self.conn.commit()
        
    def is_usergroups_row_exists(self, user_id, group_id) -> bool:
        ''' return True if user-group row is already exists '''
        self.cur.execute(f"SELECT * FROM usergroups WHERE fk_user_id = {user_id} AND fk_group_id = {group_id}")
        row = self.cur.fetchall() #return list of tuples
        if row:
            return True
        else:
            return False
    # end of class


#other functions:

def write_category(group_id, new_category):
    if not open("categories.json").read(1):
        # file is empty
        data = {}
    else:
        # file is not empty, read JSON file into a dictionary
        with open("categories.json", "r") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                # file is not in valid JSON format
                data = {}
    # add a new key-value pair with a string value to the dictionary
    
    if group_id in data:
        if new_category in data[group_id] or new_category in categories_config:
            return "Category already exists!"
        else: 
            data[group_id].append(new_category) # add new category to the group

    # group not exist. add new group    
    else:
        data[group_id] = [new_category]
    # write the updated dictionary to the same JSON file
    with open("categories.json", "w") as f:
        json.dump(data, f)
    return "Category added successfuly!"


def get_categories(group_id):
    
    if not open("categories.json").read(1):
        # file not exists
        data = {}
        json_string = json.dumps(data)
        with open("categories.json", "w") as f:
            f.write(json_string)
        return []

    else:
        # file is not empty, read JSON file into a dictionary
        with open("categories.json", "r") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                # file is not in valid JSON format
                data = {}
    if group_id in data:
        return data[group_id]
    else:
        return []

def remove_category(group_id, category):
    if not open("categories.json").read(1):
        # file is empty
        return "category not exist"
    else:
        # file is not empty, read JSON file into a dictionary
        with open("categories.json", "r") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                # file is not in valid JSON format
                return "category not exist"
    if group_id in data:
        if category in data[group_id]:
            data[group_id].remove(str(category))
            with open("categories.json", "w") as f:
                json.dump(data, f)
            return "category removed successfuly!"
    else:
        return "category not exist"

