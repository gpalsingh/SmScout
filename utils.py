# -*- coding: utf-8 -*-

import re

try:
    import BeautifulSoup as bs
except:
    import bs4 as bs
import os
import time
import variables
import sqlite3 as sql
import sys
import platform

# =========================================================================
#
#                       GLOBAL VARIABLES
#
# =========================================================================
transL = {'e': {'è', 'é', 'ê', 'ë', 'ē'},
          'y': {'ÿ', 'ý'},
          'u': {'ù', 'ú', 'û', 'ü', 'ū'},
          'i': {'ì', 'í', 'î', 'ï', 'ī'},
          'o': {'ò', 'ó', 'ô', 'õ', 'ö', 'ō', 'œ', 'ø'},
          'a': {'à', 'á', 'â', 'ã', 'ä', 'å', 'ā', 'æ'},
          's': {'§', 'ß'},
          'c': {'ç'}, 'n': {'ñ'}
          }

transU = {'E': {'È', 'É', 'Ê', 'Ë', 'Ē'},
          'Y': {'Ý', 'Ÿ'},
          'U': {'Ù', 'Ú', 'Û', 'Ü', 'Ū'},
          'I': {'Ì', 'Í', 'Î', 'Ï', 'Ī'},
          'O': {'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ō', 'Œ', 'Ø'},
          'A': {'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Ā', 'Æ'},
          'S': {'§', 'SS'},
          'c': {'Ç'}, 'n': {'Ñ'}
          }

transC = {'': {'¡', '¿'}, '"': {'“', '”', '˝'},
          }

homepage = variables.homepage
deepest_dir = variables.database_folder
test_folder = variables.test_folder
colors = {'red': "\033[31m",
          'white': "\033[37m",
          'green': "\033[32m",
          'blue': "\033[34m",
          'cyan': "\033[36m",
          'yellow': "\033[33m",
          'magenta': "\033[35m",
          'reset': "\033[0m"}

handle = sys.stdout


def remove_colors():
    global colors
    for x in colors.keys():
        colors[ x ] = ''


if (hasattr(handle, "isatty") and handle.isatty()) or \
        ('TERM' in os.environ and os.environ[ 'TERM' ] == 'ANSI'):
    if platform.system() == 'Windows' and not ('TERM' in os.environ and os.environ[ 'TERM' ] == 'ANSI'):
        remove_colors()
else:
    remove_colors()


# =========================================================================
#
#                       FUNCTION DEFINITIONS
#
# =========================================================================

def to_ascii(inp):
    if isinstance(inp, unicode):
        st = inp.encode('utf-8')
    else:
        st = str(inp)
    for dictionary in [ transL, transU, transC ]:
        for asc, lat in dictionary.items():
            for let in lat:
                if repr(st).count('\\') == 0:
                    return st
                if let in st:
                    st = st.replace(let, asc)
    return st


def get_string_tag(tag):
    name = tag.string.encode('utf-8').strip()
    if '(' in name:
        regex_str = r'[^(]+'
        without_brackets = re.search(regex_str, name)
        name = without_brackets.group(0).strip()
    return name


def get_string(st):
    if isinstance(st, bs.Tag):
        st = get_string_tag(st)
    return to_ascii(st)


def get_link(tag, field='href'):
    href = tag.get(field)
    return homepage + href


def extract_anchor(tag, field='href'):
    text = get_string(tag)
    link = get_link(tag, field)
    return text, link


def pick_one(the_dict):
    choice_dict = {}
    tot_choices = 0
    for num, name in enumerate(sorted(the_dict.keys())):
        choice_dict.update({num: the_dict[ name ]})
        print num, name
        tot_choices += 1
    print 'Pick one to fetch data'
    res = 'asq+bsq=csq'
    while not res.isdigit() or int(res) >= tot_choices:
        res = raw_input('Enter no > ')

    choice = choice_dict[ int(res) ]
    return res, choice


def make_folder(flist):
    now_on = os.path.abspath(os.curdir)
    os.chdir('/')
    if isinstance(flist, str):
        flist = flist.split('/')
        while '' in flist:
            flist.remove('')
    full_path = os.path.join(*flist)

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    os.chdir(now_on)

    return full_path


def quoted(st):
    st = str(st)
    if st[ -1 ] == '"':
        return "'" + st + "'"
    return '"' + st + '"'


def to_dict(st):
    if isinstance(st, str):
        return eval(st)
    elif isinstance(st, dict):
        return st
    else:
        return None


def get_insert_query(dict_str, cols, cols_str, table):
    basic_str = """INSERT INTO {}
    ({})
    VALUES ({});"""
    data = to_dict(dict_str)
    values = [ quoted(data[ x ]) for x in cols ]
    val_str = ', '.join(values)

    insert_str = basic_str.format(quoted(table), cols_str, val_str)
    return insert_str


def colored(st, clr):
    return colors[ clr ] + get_string(st) + colors[ 'white' ]


def get_done_leagues():
    leagues_table = variables.done_leagues_table
    conn = sql.connect(variables.main_database)
    cur = conn.cursor()

    try:
        rows = cur.execute("SELECT name, nation, path FROM {} "
                           .format(leagues_table)
                           ).fetchall()
    except:
        rows = [ ]

    data = [ ]
    for row in rows:
        name, nation, path = row
        data.append([ str(x) for x in [ name, nation, path ] ])

    cur.close()
    conn.close()
    return data


def get_at_n(x, n):
    return [ t[ n ] for t in x ]


def get_leagues(x):
    return get_at_n(x, 0)


def get_nations(x):
    return get_at_n(x, 1)


def get_paths(x):
    return get_at_n(x, 2)


def time_till_next_download(name, weeks=3):
    secs_in_week = 7 * 24 * 60 * 60
    min_time = secs_in_week * weeks

    if name not in get_leagues(get_done_leagues()):
        return -2e13

    dbase = variables.main_database
    leagues_table = variables.done_leagues_table
    conn = sql.connect(dbase)
    cur = conn.cursor()
    result = cur.execute('''SELECT downDate FROM {}
WHERE name="{}"'''.format(leagues_table,
                          name
                          )
                         )
    down_time = result.fetchall()[ 0 ][ 0 ]
    cur.close()
    conn.close()

    time_elapsed = time.time() - down_time
    weeks_left = (min_time - time_elapsed) / secs_in_week
    days_left = int(weeks_left * 7)

    return days_left


def get_closest_names(wanted, available):
    filtered_data = [ ]
    raw_names = wanted
    possible_names = get_leagues(available)
    found_leagues = set()
    total_leagues = len(possible_names)

    for index, approx in enumerate(raw_names):
        i = 0
        while i < total_leagues:
            if i in found_leagues:
                continue
            name = possible_names[ i ]
            if name.lower().startswith(approx.lower()):
                filtered_data.append(available[ i ])
            i += 1
    return filtered_data


def save_league_done(nation_name, league_name, path, dtime=None):
    if dtime is None:
        from time import time
        dtime = str(time())

    dbase = variables.main_database
    table = variables.done_leagues_table

    conn = sql.connect(dbase)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE
        IF NOT EXISTS {}(
        name string(255),
        nation string(255),
        path string(255),
		downDate str(255)
		)'''.format(table)
                )

    past_entries = cur.execute('''SELECT * FROM "{}"
                                  WHERE name="{}"and nation="{}"'''.format(table,
                                                                           league_name,
                                                                           nation_name
                                                                           )
                               ).fetchall()

    num_past_entries = len(past_entries)
    if num_past_entries > 1:
        print colored('''Database corrupted !
Still continuing...''', 'red')
    if num_past_entries == 0:
        cur.execute('''INSERT INTO "{}"
            (name, nation, path, downDate)
            VALUES ( "{}", "{}", "{}", {} )'''
                    .format(table,
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
                    .format(table,
                            dtime,
                            league_name,
                            nation_name
                            )
                    )

    conn.commit()
    cur.close()
    conn.close()


# =========================================================================
#
#                       TABLE MAKERS
#
# =========================================================================





def get_type(thing):
    return re.search("<type '(.+)'>", str(type(thing))).groups()[ 0 ]


def build_table(nation, league_name):  # main function
    def get_league_players(path):
        for fil in os.listdir(path):
            if fil.endswith('.txt'):
                han = open(os.path.join(path, fil), 'r')
                for lin in han.readlines():
                    yield lin.strip()
                han.close()

    if v:
        print 'Writing data for', colored(nation, 'yellow'), '>', colored(league_name, 'blue')

    leagues = get_leagues(get_done_leagues())

    if league_name not in leagues:
        print >> sys.stderr, colored('Error: Download data for {} first'.format(league_name), 'red')
        return False

    path = os.path.join(*[ variables.files, nation, league_name ])
    dbase = os.path.join(variables.database_folder, nation + '.db')
    conn = sql.connect(dbase)
    cur = conn.cursor()
    player_generator = get_league_players(path)
    count = 0

    try:
        first_player_str = player_generator.next()
    except:
        print 'Not a single player found in ', colored(league_name, 'red')
        return False

    data = to_dict(first_player_str)
    column_and_type = {x: get_type(data[ x ]) for x in variables.attrs_to_save}
    column_and_type.update(variables.extra_attrs_to_save)
    columns = column_and_type.keys()
    columns_str = ', '.join(columns)
    column_and_type[ 'name' ] += ' UNIQUE'

    # make table
    base_strings = [ "{} {}".format(x, y) for x, y in column_and_type.items() ]
    init_string = ',\n'.join(base_strings)

    cur.execute('DROP TABLE IF EXISTS "{}"'.format(league_name))

    cur.execute("""CREATE TABLE "{}" ({});""".format(
            league_name,
            init_string)
    )

    for player_str in player_generator:
        query = get_insert_query(player_str, columns, columns_str, league_name)
        try:
            cur.execute(query)
            count += 1
        except:
            print colored('Duplicate entry found', 'red')
        conn.commit()

    return count


# =========================================================================
#
#                       INITIALIZATION CALLS
#
# =========================================================================
make_folder(deepest_dir)
column_and_type_dict = None
v = True
