import mysql.connector

USERNAME = 'DbMysql02'
PASSWORD = 'neworder'
# HOST = 'mysqlsrv1.cs.tau.ac.il'
HOST = '127.0.0.1'
PORT = 3305
DATABASE = 'DbMysql02'

class DatabasePopulator:
    def __init__(self):
        self.cnx = mysql.connector.connect(user=USERNAME,
                                           password=PASSWORD,
                                           host=HOST,
                                           database=DATABASE,
                                           port=PORT)
        self.cursor = self.cnx.cursor()

    def insert_row(self, table, values):
        query = f'''INSERT INTO `test_table` (`test1`, `test2`, `test3`)
         VALUES ('{values[0]}', '{values[1]}', '{values[2]}')'''
        encoded_query = query.encode('utf-8')
        self.cursor.execute(encoded_query)
        self.cnx.commit()

    def close(self):
        self.cnx.close()
