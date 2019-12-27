import mysql.connector

USERNAME = 'DbMysql02'
PASSWORD = 'neworder'
HOST = 'mysqlsrv1.cs.tau.ac.il'
DATABASE = 'DbMysql02'


class DatabasePopulator:
    def __init__(self):
        self.cnx = mysql.connector.connect(user=USERNAME,
                                           password=PASSWORD,
                                           host=HOST,
                                           database=DATABASE)
        self.cursor = self.cnx.cursor()

    def sample_population(self, table_name, column, values):
        query = f'INSERT INTO {table_name} {column} VALUES {values}'
        encoded_query = query.encode('utf-8')
        self.cursor.execute(encoded_query)
        self.cursor.commit()

    def close(self):
        self.cnx.close()
