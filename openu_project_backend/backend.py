import uuid
import sqlite3
import psycopg2
import matplotlib.pyplot as plt
from openu_project_backend import config

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host =      config.DB_HOST,
            database =  config.DB_DATABASE_NAME,
            user =      config.DB_USER,
            password =  config.DB_PASSWORD,
            port =  int(config.DB_PORT))
        
        self.cur = self.conn.cursor()


    def insert(self, message_id, group_id, group_name, user_id, user_name, category, price):
        self.cur.execute("INSERT INTO db VALUES (?,?,?,?,?,?,?)",(message_id, group_id, group_name, user_id, user_name, category, price))
        self.conn.commit()

    def view(self):
        self.cur.execute("SELECT * FROM db")
        rows=self.cur.fetchall()
        return rows


    def search(self,user_id):
        self.cur.execute("SELECT * FROM db WHERE user_name=?", (user_id,))
        rows=self.cur.fetchall()
        return rows


    def delete(self,user_id):
        self.cur.execute("DELETE FROM db WHERE user_id=?", (user_id,))
        self.conn.commit()


    def update(self,user_id):
        self.cur.execute("UPDATE user_id SET user_id=? WHERE user_id=?",(user_id))
        self.conn.commit()


    def get_users(self):
        self.cur.execute("SELECT user_name FROM db")
        rows = self.cur.fetchall()
        return rows

    def group_search(self, group_id):
        self.cur.execute("SELECT * FROM db WHERE group_name=?", (group_id,))
        rows = self.cur.fetchall()
        if rows:
            return True
        return False

    def get_group_total_expenses(self):
        # execute the SQL query
        self.cur.execute('SELECT SUM(price) FROM db')
        # fetch the result
        result = self.cur.fetchone()[0]
        return result

    def get_user_total_expenses(self, user_id):
        pass
    
    def create_group(self, group_id, group_name) -> int:
        ''' create group in 'groups' table and return auth number '''
        group_auth = f"{uuid.uuid4()}".split('-')[0][0:5] #generate first 5 numbers for UUID
        
        self.cur.execute(f"INSERT INTO groups (pk_id, group_name, auth) VALUES ({group_id}, {group_name}, {group_auth})")
        self.conn.commit()
        
        return group_auth
    
    def create_user(self, user_id, user_name, email, is_admin) -> None:
        ''' create user in 'users' table '''
        self.cur.execute(f"INSERT INTO users (pk_id, user_name, email, is_admin) VALUES ({user_id}, {user_name}, {email}, {is_admin})")
        self.conn.commit()
    
    def is_user_exists(self, user_id) -> tuple[bool, str]:
        ''' Check if user exists.\n
            Return (True, string of the details about the user) if exists,\n
            Return (False, None) if not exists'''
            
        #check if user_id exists
        self.cur.execute(f"select * from users where pk_id = {user_id}")
        user = self.cur.fetchall() #return list of tuples
        if user:
            return True, f""+user
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
        self.cur.execute(f"INSERT INTO usergroups (fk_user_id, fk_group_id, role) VALUES ({user_id}, {group_id}, {is_group_admin})")
        self.conn.commit()
        
    def is_usergroups_row_exists(self, user_id, group_id) -> bool:
        ''' return True if user-group row is already exists '''
        self.cur.execute(f"SELECT * FROM users WHERE user_id = {user_id} AND group_id = {group_id}")
        row = self.cur.fetchall() #return list of tuples
        if row:
            return True
        else:
            return False
        
        
        
        

def get_group_total_expenses():
    conn = sqlite3.connect('data.db')

    # create a cursor object
    cur = conn.cursor()

    # execute the SQL query
    cur.execute('SELECT SUM(price) FROM db')

    # fetch the result
    result = cur.fetchone()[0]

    # print the result
    #print(result)
    return result

    # close the connection
    conn.close()

def add_row(message_id, group_id, group_name, user_id, user_name, category, price, date):

    #print(f'message id: {message_id}, group id: {group_id}, group name: {group_name}, user id: {user_id}, user name:{user_name}, category: {category}, price:{price}, date:{date}')

    db = Database("data.db")
    db.insert(message_id, group_id, group_name, user_id, user_name, category, price)

    '''
    if group_id in groups:
        pass
    # create new group table
    else:
        pass
    '''

def piechart():
    conn = sqlite3.connect('data.db')

    # retrieve data from database
    cursor = conn.execute("SELECT category, SUM(price) FROM db GROUP BY category")
    data = cursor.fetchall()

    # create lists of categories and total prices
    categories = [row[0][::-1] for row in data]
    prices = [row[1] for row in data]
    # create a pie chart
    plt.pie(prices, labels=categories, autopct='%1.1f%%')

    plt.axis('equal')

    # add a title
    plt.title('result')

    # show the chart
    #plt.show()
    plt.savefig('my_plot.png')
    # close the database connection
    conn.close()
