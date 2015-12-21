#-*- coding: utf-8 -*-

import re
try:
    import BeautifulSoup as bs
except:
    import bs4 as bs
import os
import time
import gVars
import sqlite3 as sql

#=========================================================================
#
#                       GLOBAL VARIABLES
#
#=========================================================================    
transL = {'e':{'è','é','ê','ë','ē'},
        'y':{'ÿ','ý'},
        'u':{'ù','ú','û','ü','ū'}, 
        'i':{'ì','í','î','ï','ī'},
        'o':{'ò','ó','ô','õ','ö','ō','œ','ø'},
        'a':{'à','á','â','ã','ä','å','ā','æ'},
	     's':{'§','ß'},
	     'c':{'ç'}, 'n':{'ñ'} 
	     }

transU = {'E':{'È','É','Ê','Ë','Ē'},
        'Y':{'Ý','Ÿ'},
        'U':{'Ù','Ú','Û','Ü','Ū'}, 
        'I':{'Ì','Í','Î','Ï','Ī'},
        'O':{'Ò','Ó','Ô','Õ','Ö','Ō','Œ','Ø'},
        'A':{'À','Á','Â','Ã','Ä','Å','Ā','Æ'},
	     'S':{'§','SS' },
	     'c':{'Ç'}, 'n':{'Ñ'} 
	     } 
	     
transC = { '':{'¡', '¿'}, '"':{'“','”','˝'},
        }
 
homepage = gVars.homepage
deepest_dir = gVars.database_folder
test_folder= gVars.test_folder
colors ={ 'red':"\033[31m", 
          'white':"\033[37m", 
          'green':"\033[32m",
          'blue':"\033[34m",
          'cyan':"\033[36m",
          'yellow':"\033[33m",
          'magenta' : "\033[35m",
          'reset':"\033[0m" }

#=========================================================================
#
#                       FUNCTION DEFINITIONS
#
#=========================================================================

def toAscii( inp ):
    """replaces foreign words their english counterparts
    
    inp: string to convert
    
    returns: string
    """
    if isinstance( inp, unicode ):
        st = inp.encode('utf-8')
    else:
        st = str(inp)
    for dictionary in [transL, transU, transC]:
        for asc, lat in dictionary.items():
            for let in lat:
                if repr(st).count('\\')==0:
                    return st
                if let in st:
                    st = st.replace( let, asc )
    return st
               
def getStringTag( tag ):
   """get text in <tag> ( text ) </tag>
   
   tag:     BeautifulSoup.Tag
   
   returns: string
   """
   name = tag.string.encode('utf-8').strip()
   if '(' in name:
       regex_str = r'[^(]+'
       without_brackets = re.search( regex_str, name )
       name = without_brackets.group(0).strip()
   return name

def getString( st ):
    """gets string from tag or string
    """
    if isinstance(st, bs.Tag):
        st = getStringTag( st )
    return toAscii( st )
 
def getLink( tag, field='href' ):
    """get hyperlink form given tag
    
    tag:    BeautifulSoup tag
    field:  href, title, etc
    
    returns:    URL as string
    """
    href = tag.get( field )
    return homepage+href
    
def extractAnchor( tag, field='href' ):
    """gets both name and link for HTML <a> tag
    
    tag:    BeautifulSoup tag
    field:  href, title, etc
    
    returns:    (text, link) tuple"""
    text = getString( tag )
    link = getLink( tag, field )
    return text, link
    
def pickOne( the_dict ):
    """prompts user to choose one of the items in list
    
    the_dict:   python dict with {name: url} pairs
    
    returns:    (int, string)
    """    
    choice_dict = {}
    for num, name in enumerate( sorted(the_dict.keys()) ):
        choice_dict.update({ num : the_dict[name] })
        print num, name
    print 'Pick one to fetch data'
    while True:
        res = raw_input('Enter no > ')
       
        if res.isdigit() and int(res)<len( choice_dict ):
            break
    choice = choice_dict[ int(res) ] 
    return (res, choice)
    
def bracketed( li, sep=', ' ):
    """get the string enclosed in brackets
    """
    if hasattr( li, '__iter__' ):
        st = sep.join( li )
    elif isinstance( li, str ):
        st = li
    else:
        print 'Invalid argument of ', type(li)
        return li
    return '('+ st +')'
    
def makeFolder( flist ):
    """Makes the folder hierarchy as given in string
    
    flist:      list of folders in order
    
    returns:    string - final path
    """
    now_on = os.path.abspath( os.curdir )
    os.chdir('/')
    if isinstance(flist, str):
        flist = flist.split('/')
        for c in range( flist.count('') ):
            flist.remove('')
    fullPath = os.path.join( *flist )
    
    if not os.path.exists( fullPath ):
        os.makedirs( fullPath )
        
    os.chdir(now_on)
    
    return fullPath
    
def quoted( st ):
    """quotes the given text
    quoted("Hello") -> '"Hello"'
    """
    st = str(st)
    if st[-1]=='"':
        return "'" + st + "'"
    return '"'+ st +'"'
 
def toDict( st ):
    """make dictionary from given string
    """
    if isinstance( st, str ):
        return eval( st )
    elif isinstance( st, dict ):
        return st
    else:
        return None
        
def makeTable( name, column_and_type, cursor):
    """Makes the table in database with given column
    data
    
    name:               name of table
    column_and_type:    {name, type} dictionary
    cursor:             cursor to database
    
    raises:             sql.OperationalError
    """
    base_strings = [ "{} {}".format( x, y ) for x, y in column_and_type.items() ]
    init_string = ',\n'.join( base_strings ) 
    try:
        cursor.execute("""CREATE TABLE {}
            {};""".format( quoted(name), bracketed(init_string) )
        )
    except sql.OperationalError as e:
        if e.message.endswith('exists'):
            cursor.execute("""DROP TABLE {}""".format( quoted(name) ) )
            makeTable( name, column_and_type, cursor )
        else:
            raise e
    
def getInsertQuery( dict_str, cols, cols_str, table ):
    """makes sql insert query string from given data
    
    dict_str:       player stats dictionary in string format
    cols:           columns to save data in
    cols_str:       contents of cols in single string
    table:          name of table
    
    returns:        string
    """
    basic_str = """INSERT INTO {}
    ({})
    VALUES ({});"""
    data = toDict( dict_str )  
    
    values = [ quoted(data[ x ]) for x in cols ]
    val_str = ', '.join( values )
    
    insert_str = basic_str.format( quoted(table), cols_str, val_str )
    return insert_str
    
def colored( st, clr ):
    """gives string with color code appended to it
    """
    return colors[clr] + getString(st) + colors['white']   
    
def getDoneLeagues():
    """gives the names of nations for which data 
    has been downloaded, along with league and 
    path where data is stored
    
    returns:    [(league, nation, path)]
    """
    
    leagues_table = gVars.done_leagues_table
    conn = sql.connect( gVars.main_database )
    cur = conn.cursor()
    
    try:
        rows = cur.execute("SELECT name, nation, path FROM {} "
                        .format( leagues_table )
               ).fetchall()
    except:
        rows = []
           
    data = []
    for row in rows:
        name, nation, path = row
        data.append([ str(x) for x in [name, nation, path] ])

    cur.close()
    conn.close()
    return data   
    
get_at_n = lambda x,n: [ t[n] for t in x ]
getLeagues = lambda x: get_at_n(x, 0)
getNations = lambda x: get_at_n(x, 1)
getPaths = lambda x: get_at_n(x, 2) 
    
def timeTillNextDownload( name, weeks=3 ):
    secs_in_week = 7 * 24 * 60 * 60
    min_time = secs_in_week * weeks
    
    if name not in getLeagues( getDoneLeagues() ):
        return -2e13
    
    dbase = gVars.main_database
    leagues_table = gVars.done_leagues_table
    conn = sql.connect( dbase )
    cur = conn.cursor()
    result = cur.execute('''SELECT downDate FROM {}
WHERE name={}'''.format( leagues_table,
                         quoted(name) 
                       )
                     )
    down_time = result.fetchall()[0][0]
    cur.close()
    conn.close()
    
    time_elapsed = time.time() - down_time
    weeks_left = (min_time - time_elapsed) / secs_in_week
    days_left = int( weeks_left * 7 )
    
    return days_left
    
def getClosestNames(wanted, available):
    """finds possible names for given names
    of leagues"""
    
    filtered_data = []
    raw_names = wanted
    possible_names = getLeagues(available)
    found_leagues = set()
    total_leagues = len(possible_names)

    for index, approx in enumerate( raw_names ):
        i = 0
        while i < total_leagues:
            if i in found_leagues: continue
            name = possible_names[i]
            if name.lower().startswith( approx.lower() ):
                filtered_data.append( available[i] )
            i += 1           
    return filtered_data
   
#=========================================================================
#
#                       INITITALIZATION CALLS
#
#=========================================================================
makeFolder( deepest_dir )
#makeFolder( test_folder )

if __name__=='__main__':
    n = u"""¡Hólà!,
    Mí nömbré ës Gürkïrpál §íñgh
    Yo son un programador
    ¿Habla inglés?
    """
    print getString(n)
 
