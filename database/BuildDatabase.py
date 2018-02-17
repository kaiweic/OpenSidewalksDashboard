import pymysql

db = pymysql.connect('localhost', 'kevin', 'kevin', 'sidewalk_data')
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS test")
cursor.execute('CREATE TABLE test (ID INT NOT NULL, NAME CHAR(20) NOT NULL)')
