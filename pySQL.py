from urllib.parse import urlparse
import mysql.connector

url = urlparse('mysql://user:pass@localhost:3306/test')

conn = mysql.connector.connect(
    host = url.hostname or 'localhost',
    port = 3306,
    user = 'root',
    password = 'password',
    database = url.path[1:],
)
conn.ping(reconnect=True)
cur = conn.cursor()

try:
    cur.execute('INSERT INTO score(uri,DNN,SVM,Total,Rank) VALUES(%s,%s,%s,%s,%s) on duplicate key update uri="/test",DNN=0', ('/test',1,1,1,1))
#    cur.execute('INSERT INTO score(uri,DNN,SVM,Total,Rank) VALUES(%s,%s,%s,%s,%s)', ('/test',1,1,1,1))
    conn.commit()
except:
    conn.rollback()
    raise
cur.execute('SELECT * FROM score ')

print(cur.fetchall())
