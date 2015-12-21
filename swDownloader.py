#-*- coding: utf-8 -*-

import os, sys
import shutil
import argparse
import swNavigation as nav
import tablesBuilder as tBuilder
from API import swApi as api
from Utils import leagueSaver as lSav
from Utils import smUtils
from Utils import gVars

parser = argparse.ArgumentParser(prog='Downloads data for leagues')
group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--verbose', help='Enable extra text'
                    , action='store_true', default=True) 
group.add_argument('-q', '--quiet', help='Disable extra text'
                    ,action='store_true', default=False)
parser.add_argument('-n', '--new-session', dest='new'
                    , help='Force data download from beginning'
                    , default=False, action='store_true')
parser.add_argument('-a', '--age', help='Minimum age of players'
                    ,type=int, default=21)
parser.add_argument('-m', '--mins', help='''Minimum numbers of
minutes that the player should have played ( this season )'''
                    , type=int, default=200)
parser.add_argument('-g', '--goals', help='''Minimum numbers of
goals the player should have scored( this season )'''
                    , type=int, default=0)                                                                 

args = parser.parse_args()
files_dir = gVars.files
verbose = args.verbose and not args.quiet
min_age = args.age
min_mins = args.mins
min_goals = args.goals
new_session = args.new
weeks_between_downloads = 3

#=========================================================================
#
#                               TODO
#
#=========================================================================
#add sm ratings

#=========================================================================
#
#                               UI
#
#=========================================================================
try:
    nat_num, nation_URL = nav.chooseNation()
    league_num, league = nav.chooseLeague( nation_URL )
except:
    print smUtils.colored('Working internet connection required', 'red')
    sys.exit(0)
league_name = league.getName()
league_nation = league.getNation()
table = league.getTable()

#=========================================================================
#
#                           LOGGING
#
#=========================================================================
time_remaining = smUtils.timeTillNextDownload( league_name, weeks_between_downloads )
if time_remaining>0 and not new_session:
    msg = "\nToo soon to download again.\n"
    msg += "You should wait at least {} days more".format( time_remaining )
    msg += " to get some useful new data."
    print smUtils.colored( msg, 'red' )
    sys.exit(0) 

league_dir = smUtils.makeFolder( [files_dir,league_nation,league_name] )
session_dir = os.path.join(league_dir, 'lastSession') 

options_file = league.getNation().lower() +'.txt'
options_file_path = os.path.abspath(os.curdir) + '/' + options_file

with open(options_file_path, 'w') as choices_file:  #save the options
    choices_file.write( str(nat_num) + '\n' )
    choices_file.write( str(league_num) + '\n' )
    choices_file.write( 'yes' + '\n' )
    
print smUtils.colored('''
Saved file as {} with the given options.
Next time you can just use:
python {} < {}'''.format( options_file, sys.argv[0], options_file )
, 'green')

if os.path.exists( session_dir ):
    if not new_session and time_remaining<0:
        print '\n\n'+'Incomplete session found'
        print 'Continue ? (y/n)'
        new_session = raw_input().lower().startswith('n')
else:
    os.mkdir( session_dir )
    new_session = True
    
player_log = open( os.path.join(session_dir, 'player_log.txt'), 'a+')
team_log = open( os.path.join(session_dir, 'team_log.txt'), 'a+')
player_log.seek(0)
team_log.seek(0)
if new_session:
    for f in [player_log, team_log]:
        f.truncate()
        f.flush()
    players_done = []
    teams_done = []
else:
    players_done = player_log.read().split('\n')
    teams_done = team_log.read().split('\n')

lSav.saveLeagueDone( league_nation, league_name, league_dir, 0 )	

#=========================================================================
#
#                           DOWNLOADER
#
#=========================================================================    
print '\nDownloading', smUtils.colored( league_nation, 'blue' )
print '\t    --', smUtils.colored(league_name, 'yellow'),'\n'

for team in table.getTeams():
    team_name = team.name
    if team_name in teams_done: continue
    team_file = open( os.path.join(league_dir, team_name+'.txt'), 'a')
    if new_session:
        team_file.seek(0)
        team_file.truncate()
    print '\nGetting data for', smUtils.colored( team_name, 'blue' )
    
    for player in team.getPlayers():
        if player is None:
            if verbose:
                try:
                    print '\t'+smUtils.colored('No stats data availabele for {}'.format( player.name ), 'red')
                except:
                    print '\t'+smUtils.colored('No player data availabele for {}'.format( team_name ), 'red')
                    break
            continue
        if player.name in players_done: continue
        
        if verbose:
            print '\n',player.name,':'
        if player.eligible(min_age, min_mins, min_goals, verbose):
                team_file.write( str(player) + '\n' )
                team_file.flush()
                if verbose:
                    print '\t'+smUtils.colored('Saved\n', 'green')
        player_log.write( player.name+'\n' )
        player_log.flush()
    
    team_file.close()
    player_log.seek(0)
    player_log.truncate()
    player_log.flush()
    team_log.write( team_name+'\n' )
    team_log.flush()
    
player_log.close()
team_log.close()	 
shutil.rmtree(session_dir)

print smUtils.colored('''Download complete!
Writing to database''', 'green' )
num = tBuilder.buildTable( league_nation, league_name, league_dir, True )
print "Total", smUtils.colored(num, 'blue'), "players found in", smUtils.colored(league_name, 'blue')




