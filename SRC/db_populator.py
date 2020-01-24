import mysql.connector
from constants import *

class DatabasePopulator:
    def __init__(self):
        self.cnx = mysql.connector.connect(user=DB_USERNAME,
                                           password=DB_PASSWORD,
                                           host=DB_HOST,
                                           database=DB_NAME,
                                           port=DB_PORT)
        self.cursor = self.cnx.cursor()

    def insert_row(self, table_name, values):
        input_values = ', '.join(map(lambda x: "%s", values))
        sql_query = f'INSERT INTO `%s` VALUES (%s)' % (table_name, input_values)
        try:
            self.cursor.execute(sql_query, tuple(values))
            self.cnx.commit()
        except Exception as ex:
            print(ex)
            self.cnx.rollback()

    def close(self):
        self.cnx.close()
