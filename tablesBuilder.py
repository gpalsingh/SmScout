# -*- coding:utf-8 -*-
import utils
import variables
import sqlite3 as sql
import os
import sys
import argparse

# =========================================================================
#
#                       GLOBAL VARIABLES
#
# =========================================================================
column_and_type_dict = None
all_leagues = utils.get_done_leagues()
v = True


# =========================================================================
#
#                       FUNCTIONS
#
# =========================================================================
def get_league_players(path):
    for fil in os.listdir(path):
        if fil.endswith('.txt'):
            han = open(os.path.join(path, fil), 'r')
            for lin in han.readlines():
                yield lin.strip()
            han.close()


def get_columns(dStr):

    data = utils.to_dict(dStr)

    #                                 type(5) -> <type 'int'>
    column_and_type_dict = {x: str(type(data[x])).split("'")[1] for x in variables.attrs_to_save}
    column_and_type_dict.update(variables.extra_attrs_to_save)
    return column_and_type_dict


def league_exists(nation, name):
    for lg, nat, path in all_leagues:
        if lg == name and nat == nation:
            return True
    return False


def fill_league_table(name, nation, path):
    dbase = os.path.join(variables.database_folder, nation + '.db')
    conn = sql.connect(dbase)
    cur = conn.cursor()
    player_generator = get_league_players(path)
    count = 0

    try:
        first_player_str = player_generator.next()
    except:
        print 'Not a single player found in ', utils.colored(name, 'red')
        return False

    column_and_type = get_columns(first_player_str)
    columns = column_and_type.keys()
    columns_str = ', '.join(columns)
    column_and_type['name'] += ' UNIQUE'
    utils.make_table(name, column_and_type, cur)

    for player_str in player_generator:
        query = utils.get_insert_query(player_str, columns, columns_str, name)
        try:
            cur.execute(query)
            count += 1
        except:
            print utils.colored('Duplicate entry found', 'red')
        conn.commit()

    return count


def build_table(nation, league_name, path, overwrite=False):  # main function
    if v:
        print 'Writing data for', utils.colored(nation, 'yellow'), '>', utils.colored(league_name, 'blue')

    leagues = utils.get_leagues(all_leagues)

    if league_name not in leagues:
        print >> sys.stderr, utils.colored('Error: Download data for {} first'.format(league_name), 'red')
        return False

    if not overwrite and league_exists(nation, league_name):
        res = raw_input('''Data already exists for {}\nOverwrite? (yes/no): '''.format(league_name)
                        )
        if not res.lower().startswith('y'):
            return False

    return fill_league_table(league_name, nation, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('-l', '--leagues',
                        help='give list of leagues',
                        nargs='+', default=[])
    parser.add_argument('-o', '--overwrite',
                        help='overwrite all previous data',
                        action='store_true')
    group.add_argument('-v', '--verbose', action='store_true',
                       help='Turn on extra text', default=True)
    group.add_argument('-q', '--quiet', action='store_false',
                       help='Turn off extra text')

    args = parser.parse_args()
    v = args.verbose
    user_leagues = args.leagues

    if user_leagues:
        leagues_data = utils.get_closest_names(user_leagues, all_leagues)
    else:
        leagues_data = all_leagues

    for lg, nat, path in leagues_data:
        success = build_table(nat, lg, path, args.overwrite)
        if not v:
            continue
        if success:
            print utils.colored("Wrote data for {:d} players".format(success), 'green')
        else:
            print utils.colored("Operation Failed!", 'red')
        print ''

    if len(leagues_data) == 0:
        print utils.colored("You should download some data first", 'red')
