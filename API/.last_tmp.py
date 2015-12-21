#-*- coding:utf-8 -*-

from swUtils import testFolder
import sqlite3 as sql
from time import time

testBase = testFolder + 'logtest.db'

def saveLeagueDone(  name, url, dbase=testBase, table='test', dtime=None ):
    if dtime==None:
        dtime = getTime()
    
    conn = sql.connect( dbase )
    cur = conn.cursor()
    cur.execute('''CREATE TABLE 
        IF NOT EXISTS ?(
        name string(255)
        CONSTRAINT u_name UNIQUE,
        url string 
        CONSTRAINT u_league UNIQUE,
		 downDate str(255)
		 );'''
		 ,( table )
		 )
    try:
        cur.execute('''INSERT INTO ?
            (name, url, downDate)
            VALUES ( ?,?,? )'''
            ,(table
            	,name
	          ,url
	          ,dtime)
	    )
    except sql.IntegrityError as e:
        cur.execute('''UPDATE ?
    	     SET downDate = ?
    	     WHERE name = ?'''
    	     ,( table
    	     	,dtime
    	       ,name
    	       )
        )

    conn.commit()

    r = cur.execute('''SELECT * FROM test''')
    print r.fetchall()

    cur.close()
    conn.close()
	
def getTime():
    return str(time())