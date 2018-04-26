import sqlite3
import os

def writeListToSQLite(proxyList,db):
    if not os.path.exists(db):
        print('data base not found')
        return
    try:
        conn=sqlite3.connect(db)
        cursor=conn.cursor()
        for proxy in proxyList:
            print(proxy)
            cursor.execute('insert into proxyList (proxy) values(?)',(proxy,))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:print(e)


if __name__=='__main__':
    proxyList=[
        'http://192.168.6.6:666',
        'http://192.168.6.66:667'
    ]
    db=os.path.dirname(os.path.dirname(__file__))+r'\proxyList.db'
    writeListToSQLite(proxyList,db)