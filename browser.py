#-*- coding: utf:8 -*-

import sys
import os.path
import argparse
import variables
import utils
import sqlite3 as sql
import time

class listAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("Only one value allowed")
        super(listAction, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_strings=None):
        setattr(namespace, self.dest, [self.svar, int(values)])
        
class goalsAction(listAction): svar='goals'
class minsAction(listAction): svar='mins'
class ageAction(listAction): svar='age'

#database variables   
columns = variables.extra_attrs_to_save.keys() + variables.attrs_to_save
columns_string = ', '.join( columns ) 
all_leagues_data = utils.get_done_leagues()
 
#parser arguments 
parser = argparse.ArgumentParser()
parser.add_argument('--list', help='List all available leagues, then exit.'
                    , action='store_true', default=False)
parser.add_argument('-l', '--leagues', nargs='*'
                    , help='Give names of leagues to browse.'
                    , default=[]) 
parser.add_argument('-A', '--all', help='show data for all leagues'
                    , action='store_true', default=False)
                    
sorting = parser.add_mutually_exclusive_group()                    
sorting.add_argument('-g', '--goals', help='sort by goals'
                     , action=goalsAction )
sorting.add_argument('-m', '--mins', help='sort by minutes'
                     , action=minsAction )
sorting.add_argument('-a', '--age', help='sort by age'
                     , action=ageAction )
                     
args = parser.parse_args()  
                                  
for s in [args.goals, args.age, args.mins]:
    sort_option = s
    if sort_option is not None:    break
else:   sort_option = ['mins', 0]

svar, least = sort_option
show_all_leagues = args.all
user_requested_leagues = args.leagues

if len(all_leagues_data)==0:
    print utils.colored("Download some data first") 
    sys.exit(0)

if args.list:
    print 'Data available for :'
    for lg, natn in available_leagues.items():
        print utils.colored('\t{}( {} )'.format(lg, natn), 'blue')
    sys.exit(0)
    
leagues_data = utils.get_closest_names( user_requested_leagues, all_leagues_data )    

if leagues_data==[] or show_all_leagues:
    if not show_all_leagues:
        print '''No leagues specified (-l option).
Show data for all leagues? (yes / no)'''
        if not raw_input().lower().startswith('y'):
            sys.exit(0)
    leagues_data = all_leagues_data



for league_name, league_nation, path in leagues_data:
    '''if league_name not in getLeagues(available_leagues):
        print >> sys.stderr, utils.colored('No data available for '+league, 'red')
        continue'''
    path_to_database = os.path.join(variables.database_folder, league_nation+'.db')
    conn = sql.connect( path_to_database )
    cur = conn.cursor()
        
    print utils.colored( 'Players\' data for ' + league_name + ' : \n', 'blue' )
    players = cur.execute('''SELECT {}
                             FROM "{}"
                             ORDER BY {} DESC;'''.format( columns_string,
                                                          league_name,
                                                          svar  
                                                  )
                ).fetchall()
    
    cur.close()
    conn.close()
                         
    for player in players:
        player_data = dict( zip(columns, player) )
        if player_data[ svar ]<least or player_data[ svar ]==0 :
            continue
        for row in columns:
            val = player_data[ row ]
            col_text = '{:15} : \t'.format( row.capitalize() )
            if row==svar:
                color = 'green' if least>0 else 'yellow'
                val_text = utils.colored(val, color)
            else: val_text = utils.to_ascii(val)
            
            print col_text + val_text
        
        print '\n'
        
        skip_rest = raw_input('Enter: continue, Others characters: Skip rest of the league, Ctrl+D: Exit : ')
        if not skip_rest == '':
            break  
