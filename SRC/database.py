import mysql.connector

USERNAME = 'DbMysql02'
PASSWORD = 'neworder'
HOST = 'mysqlsrv1.cs.tau.ac.il'
DATABASE = 'DbMysql02'


class Database:
    def __init__(self):
        self.cnx = mysql.connector.connect(user=USERNAME,
                                           password=PASSWORD,
                                           host=HOST,
                                           database=DATABASE)
        self.cursor = self.cnx.cursor()

    def sample_query(self, min_rank, max_rank):
        query = 'SELECT * FROM SongTable WHERE num BETWEEN %s AND %s'
        self.cursor.execute(query, min_rank, max_rank)
        return self.cursor.fetchall()

    def close(self):
        self.cnx.close()
