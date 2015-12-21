#-*- coding:utf-8 -*-
from Utils import smUtils
from Utils import gVars
import swNavigation as nav
import sqlite3 as sql
import os
import sys
import argparse

#=========================================================================
#
#                           TODO
#
#=========================================================================
#start fixing from main function

#=========================================================================
#
#                       GLOBAL VARIABLES
#
#=========================================================================
column_and_type_dict = None
all_leagues = smUtils.getDoneLeagues()
v = True

#=========================================================================
#
#                       FUNCTIONS
#
#=========================================================================
def getLeaguePlayers( path ):
    """gets the players data from given league
    
    path:   location where league data was saved
    
    yields:     player dict as string
    """
    for fil in os.listdir( path ):
        if fil.endswith('.txt'):
            han = open( os.path.join( path, fil), 'r' )
            for lin in han.readlines():
                yield lin.strip()
            han.close()
 
            
def getColumns( dStr ):
    """makes a {columns : type} dict
    
    dStr:   player data string
    
    returns:    dict
    """
    global column_and_type_dict
    if not column_and_type_dict==None:
        return column_and_type_dict
    data = smUtils.toDict( dStr )
    
    #                                 type(5) -> <type 'int'>
    column_and_type_dict = {  x : str(type(data[x])).split("'")[1] for x in gVars.attrs_to_save }
    column_and_type_dict.update( gVars.extra_attrs_to_save ) 
    return column_and_type_dict

    
def leagueExists( nation, name ):
    """tells if data was saved for same league
    in the past or not
    """    
    for lg, nat, path in all_leagues:
        if lg==name and nat==nation:
            return True
    return False
        

def fillLeagueTable( name, nation, path ):
    """writes data to table for given league
  
    returns:    numbers of players saved
    """    
    dbase = os.path.join( gVars.database_folder, nation+'.db' )
    conn = sql.connect(dbase)
    cur = conn.cursor()
    player_generator = getLeaguePlayers( path )
    count = 0
    
    try:
        first_player_str = player_generator.next()
    except:
        print 'Not a single player found in ', smUtils.colored( name, 'red' )
        return False
        
    column_and_type = getColumns( first_player_str )
    columns = column_and_type.keys()
    columns_str = ', '.join( columns )
    column_and_type[ 'name' ] += ' UNIQUE'
    smUtils.makeTable( name, column_and_type, cur )
    
    for player_str in player_generator:
        query = smUtils.getInsertQuery( player_str, columns, columns_str, name )
        try:
            cur.execute( query )
            count += 1
        except:
            print smUtils.colored( 'Duplicate entry found', 'red' )
        conn.commit()
        
    return count
        
def buildTable( nation, league_name, path, overwrite=False ): #main function 
    """writes one league's data to sql table
    returns:    integer
    """
    if v:
        print 'Writing data for',smUtils.colored( nation , 'yellow' ),'>',smUtils.colored( league_name, 'blue' )
        
    leagues = smUtils.getLeagues( all_leagues )
    
    if league_name not in leagues:
        print >> sys.stderr, smUtils.colored('Error: Download data for {} first'.format(league_name), 'red') 
        return False
    
    if not overwrite and leagueExists( nation, league_name ):
        res = raw_input('''Data already exists for {}\nOverwrite? (yes/no): '''.format(league_name)
                        )
        if not res.lower().startswith('y'):
            return False
        
    return fillLeagueTable( league_name, nation, path ) 

if __name__=="__main__":    
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    
    parser.add_argument('-l','--leagues'
                        ,help='give list of leagues'
                        ,nargs = '+', default=[])
    parser.add_argument('-o','--overwrite'
                        ,help='overwrite all previous data'
                        ,action='store_true')
    group.add_argument('-v', '--verbose', action='store_true'
                       ,help='Turn on extra text', default=True)
    group.add_argument('-q', '--quiet', action='store_false'
                        ,help='Turn off extra text')

    args = parser.parse_args()
    v = args.verbose      
    user_leagues = args.leagues
    
    if user_leagues == []:
        leagues_data = all_leagues
    else:
        leagues_data = smUtils.getClosestNames( user_leagues, all_leagues )

    for lg, nat, path in leagues_data:
        success = buildTable(nat, lg, path, args.overwrite)
        if not v: continue
        if success :
            print smUtils.colored("Wrote data for {:d} players".format(success), 'green')    
        else:
            print smUtils.colored("Operation Failed!", 'red')
        print ''
        
    if len(leagues_data)==0:
        print smUtils.colored("You should download some data first", 'red')
           
