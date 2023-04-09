import sqlite3
import matplotlib.pyplot as plt

class Database:
    def __init__(self, db):
        self.conn=sqlite3.connect(db)
        self.cur=self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS db (message_id integer PRIMARY KEY, group_id integer , group_name text, user_id text, user_name text, category text, price text)")
        self.conn.commit()


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
    plt.title('תואצוה')

    # show the chart
    #plt.show()
    plt.savefig('my_plot.png')
    # close the database connection
    conn.close()
