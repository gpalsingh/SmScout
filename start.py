# -*- coding: utf-8 -*-

import os
from sys import exit, argv
import shutil
import argparse
import utils
import variables
import api

# =========================================================================
#
#                            ARGUMENT PARSER
#
# =========================================================================
parser = argparse.ArgumentParser(prog='Downloads data for leagues')
group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--verbose', help='Enable extra text',
                   action='store_true', default=True)
group.add_argument('-q', '--quiet', help='Disable extra text',
                   action='store_true', default=False)
parser.add_argument('-n', '--new-session', dest='new',
                    help='Force data download from beginning',
                    default=False, action='store_true')
parser.add_argument('-a', '--age', help='Minimum age of players',
                    type=int, default=21)
parser.add_argument('-m', '--mins', help='''Minimum numbers of
minutes that the player should have played ( this season )''',
                    type=int, default=200)
parser.add_argument('-g', '--goals', help='''Minimum numbers of
goals the player should have scored( this season )''',
                    type=int, default=0)

# =========================================================================
#
#                               VARIABLES
#
# =========================================================================
args = parser.parse_args()
files_dir = variables.files
verbose = args.verbose and not args.quiet
min_age = args.age
min_mins = args.mins
min_goals = args.goals
new_session = args.new
weeks_between_downloads = 3


# =========================================================================
#
#                               NAVIGATION
#
# =========================================================================
def choose_nation():
    home = api.HomePage()
    nation_and_link = home.get_leagues_list()
    resp = utils.pick_one(nation_and_link)
    return resp


def choose_league(url):
    page = api.LeaguePage(url)
    print '\nGetting data. Please wait...'
    the_name = page.get_name()
    print '\nCurrently on ', the_name
    league_and_link = page.get_leagues()
    n, new_url = utils.pick_one(league_and_link)
    if new_url == page.URL:
        return n, page
    else:
        return n, api.LeaguePage(new_url)


# =========================================================================
#
#                               UI
#
# =========================================================================
league, nat_num, league_num = [None] * 3
try:
    nat_num, nation_URL = choose_nation()
    league_num, league = choose_league(nation_URL)
except:
    print utils.colored('Working internet connection required', 'red')
    exit(0)
league_name = league.get_name()
league_nation = league.get_nation()
table = league.get_table()

# =========================================================================
#
#                           LOGGING
#
# =========================================================================
time_remaining = utils.time_till_next_download(league_name, weeks_between_downloads)
if time_remaining > 0 and not new_session:
    msg = "\nToo soon to download again.\n"
    msg += "You should wait at least {} days more".format(time_remaining)
    msg += " to get some useful new data."
    print utils.colored(msg, 'red')
    exit(0)

league_dir = utils.make_folder([files_dir, league_nation, league_name])

session_dir = os.path.join(league_dir, "lastSession")

options_file = league.get_nation().lower() + ".txt"
options_file_path = os.path.abspath(os.curdir) + '/' + options_file

with open(options_file_path, 'w') as choices_file:  # save the options
    choices_file.write(str(nat_num) + '\n')
    choices_file.write(str(league_num) + '\n')
    choices_file.write('yes' + '\n')

print utils.colored('''
Saved file as {} with the given options.
Next time you can just use:
python {} < {}'''.format(options_file, argv[0], options_file), 'green')

if os.path.exists(session_dir):
    if not new_session and time_remaining < 0:
        print '\n\n' + 'Incomplete session found'
        print 'Continue ? (y/n)'
        new_session = raw_input().lower().startswith('n')
else:
    os.mkdir(session_dir)
    new_session = True

players_log = open(os.path.join(session_dir, 'player_log.txt'), 'a+')
teams_log = open(os.path.join(session_dir, 'team_log.txt'), 'a+')
players_log.seek(0)
teams_log.seek(0)
if new_session:
    for f in [ players_log, teams_log ]:
        f.truncate()
        f.flush()
    players_done = []
    teams_done = []
else:
    players_done = players_log.read().split('\n')
    players_log.seek(0)
    teams_done = teams_log.read().split('\n')
    teams_log.seek(0)

utils.save_league_done(league_nation, league_name, league_dir, 0)

# =========================================================================
#
#                           DOWNLOADER
#
# =========================================================================
print '\nDownloading', utils.colored(league_nation, 'blue')
print '\t    --', utils.colored(league_name, 'yellow'), '\n'

for team in table.get_teams():
    team_name = team.name
    if team_name in teams_done:
        continue
    team_file = open(os.path.join(league_dir, team_name + '.txt'), 'a')

    if new_session:
        team_file.seek(0)
        team_file.truncate()
        team_file.flush()
    print '\nGetting data for', utils.colored(team_name, 'blue')

    for player in team.get_players():
        if player is None:
            try:
                t = '\t' + utils.colored('No stats data availabele for {}'.format(player.name), 'red')
                if verbose:
                    print t
            except:
                t = '\t' + utils.colored('No player data availabele for {}'.format(team_name), 'red')
                if verbose:
                    print t
                break
            continue
        if player.name in players_done:
            continue

        if verbose:
            print '\n', player.name, ':'
        if player.eligible(min_age, min_mins, min_goals, verbose):
            team_file.write(str(player) + '\n')
            team_file.flush()
            if verbose:
                print '\t' + utils.colored('Saved\n', 'green')
        players_log.write(player.name + '\n')
        players_log.flush()

    team_file.close()
    players_log.seek(0)
    players_log.truncate()
    players_log.flush()
    teams_log.write(team_name + '\n')
    teams_log.flush()

players_log.close()
teams_log.close()
shutil.rmtree(session_dir)

print utils.colored('''Download complete!
Writing to database''', 'green')
num = utils.build_table(league_nation, league_name)
if num != False:
    print "Total", utils.colored(num, 'blue'), "players found in", utils.colored(league_name, 'blue')
else:
    print 'Not a single suitable player found.'
