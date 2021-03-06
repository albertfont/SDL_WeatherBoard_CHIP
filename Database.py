import MySQLdb


class Database:

    host = 'localhost'
    user = 'root'
    password = 'password'
    db = 'test'

    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
	self.password = password
        self.db = db
        self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
        self.cursor = self.connection.cursor()

    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            self.connection.rollback()



    def query(self, query):
        cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
        cursor.execute(query)

        return cursor.fetchall()

    def __del__(self):
        self.connection.close()
