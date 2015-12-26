#-*- coding:utf-8 -*-

import smUtils
import gVars
from sqlite3 import connect

def saveLeagueDone(  nation_name, league_name, path, dtime=None ):
    """keeps log of all the leagues downloaded
    """

    if dtime==None:
        from time import time
        dtime = str(time())

    dbase = gVars.main_database
    table = gVars.done_leagues_table

    conn = connect(dbase)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE
        IF NOT EXISTS {}(
        name string(255),
        nation string(255),
        path string(255),
		downDate str(255)
		 )'''.format(
		    table
		    )
		 )

    past_entries = cur.execute('''SELECT * FROM "{}"
                                  WHERE name="{}"
                                  and nation="{}"'''.format( table,
                                                           league_name,
                                                           nation_name
                                                   )
                   ).fetchall()

    num_past_entries = len(past_entries)
    if num_past_entries > 1:
        print smUtils.colored('''Database corrupted !
Still continuing...''', 'red')
    if num_past_entries==0:
        cur.execute('''INSERT INTO "{}"
            (name, nation, path, downDate)
            VALUES ( "{}", "{}", "{}", {} )'''
            .format( table,
                     league_name,
                     nation_name,
                     path,
	                 dtime
            )
	    )
    else:
        cur.execute('''UPDATE "{}"
    	     SET downDate = {}
    	     WHERE name = "{}" and nation="{}"'''
    	     .format( table,
    	     	      dtime,
    	              league_name,
    	              nation_name
    	      )
        )

    conn.commit()
    cur.close()
    conn.close()
	
