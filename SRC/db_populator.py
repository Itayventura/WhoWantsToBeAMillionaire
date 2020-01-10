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

    def insert_row(self, table_name, values, columns=""):
        input_values = ', '.join(map(lambda x: "'%s'", values))
        input_values = input_values % tuple(values)
        sql_query = "INSERT INTO %s %s " \
                    "VALUES (%s)"
        sql_query = sql_query % (table_name, columns, input_values)
        sql_query = sql_query.encode('utf-8')
        try:
            self.cursor.execute(sql_query)
            self.cnx.commit()
        except Exception as ex:
            print(ex)
            self.cnx.rollback()

    def close(self):
        self.cnx.close()
