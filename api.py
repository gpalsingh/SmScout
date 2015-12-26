# -*- coding: utf-8 -*-

# =========================================================================
#
#                       IMPORT STATEMENTS
#
# =========================================================================
import utils
import variables
import requests

try:
    import BeautifulSoup as bs
except:
    import bs4 as bs
import re

# =========================================================================
#
#                      GLOBAL VARIABLES
#
# =========================================================================
homepage = variables.homepage
files = variables.files
test_folder = variables.test_folder

# =========================================================================
#
#                       CLASS DEFINITIONS
#
# =========================================================================
class Page(object):
    def __init__(self, url=homepage):
        self.URL = url

    def get_soup(self):
        if hasattr(self, 'soup'):
            return self.soup
        handle = requests.get(self.URL)
        self.HTML = handle.content
        self.soup = bs.BeautifulSoup(self.HTML)
        handle.close()
        return self.soup


class HomePage(Page):
    def get_leagues_list(self):
        lists = self.get_soup()('select')
        dom_leagues = lists[ 1 ]
        options = dom_leagues('option')
        nations = options[ 1: ]
        maps = [ utils.extract_anchor(x, 'value') for x in nations ]
        name_to_link = dict(maps)
        return name_to_link


class LeaguePage(Page):
    def get_nation(self):
        if hasattr(self, 'nation'): return self.nation
        title = self.get_soup().find('title')
        line = utils.get_string(title)
        name = line.split(' - ')[ 2 ]
        self.nation = name
        return self.nation

    def get_name(self):
        if hasattr(self, 'lname'): return self.lname
        tag = self.get_soup().find('h1')
        self.lname = utils.get_string(tag.text)
        return self.lname

    def get_leagues(self):
        if hasattr(self, 'leagues'):
            return leagues
        tree = self.get_soup()('ul', 'left-tree')
        links = tree[ 0 ]('a')
        nations = links[ :1 ]
        if len(links) > 2:
            nations += links[ 2: ]
        name_and_link = [ utils.extract_anchor(x) for x in nations ]
        self.leagues = dict(name_and_link)
        return self.leagues

    def get_table(self):
        return LeagueTable(self.get_soup(), self.get_name())


class LeagueTable:
    tableClass = "leaguetable sortable table detailed-table"
    team_class = "text team large-link"

    def __init__(self, page_soup, league_name):
        self.soup = page_soup.find('table', self.tableClass)
        self.lname = league_name

    def get_teams(self):
        rows = self.soup('tr')[ 1:-2 ]

        for tag in rows:
            yield Team(tag, self.lname)


class Team(Page):
    linkClass = "text team large-link"
    matchesClass = "number total mp"
    winsClass = "number total won total_won"
    drawsClass = "number total drawn total_drawn"
    lostClass = "number total lost total_lost"
    gdClass = "number gd"
    pointsClass = "number points"
    squadClass = 'squad-container'

    def __init__(self, team_tag, league_name):
        self.tag = team_tag
        a = self.tag.find('a')
        self.name, self.URL = utils.extract_anchor(a)
        self.lname = league_name

    def get_players(self):
        div = self.get_soup().find('div', self.squadClass)
        if div is None:
            yield None
        cats = [ utils.get_string(x).strip('s') for x in div('th') ]
        bodies = div('tbody')
        grps = [ x('td', {'style': 'vertical-align: top;'}) for x in bodies ]

        for grp, pos in zip(grps, cats)[ :-1 ]:  # last one is coaches
            # print 'Getting players - ', pos
            for pl in grp:
                yield Player(pl, pos, self.name, self.lname)


class Player(Page):
    tableClass = 'playerstats career sortable table'
    minsClass = "number statistic game-minutes available"
    appsClass = "number statistic appearances available"
    linupsClass = "number statistic lineups available"
    subsClass = "number statistic subs-in available"
    subsonClass = "number statistic subs-out available"
    benchClass = "number statistic subs-on-bench available"
    goalsClass = "number statistic goals available"
    yellowsClass = "number statistic yellow-cards available"
    yellow2Class = "number statistic 2nd-yellow-cards available"
    redsClass = "number statistic red-cards available"
    ageDiv = {'style': 'padding-left: 27px;'}

    def __init__(self, tag, pos, tname, lname):
        self.tag = tag
        self.pos = pos
        self.team = tname
        self.sesApps, self.sesGoals = re.findall('> ([\d]+) <', str(self.tag))
        self.name, self.URL = utils.extract_anchor(self.tag.find('a'))
        self.age = self.__get_age()
        self.league_name = lname

    def __get_age(self):
        try:
            age = re.findall('([\d]{2}) years', str(self.tag))[ 0 ]
            return int(age)
        except:
            print '\t' + utils.colored('No age data available', 'red')
            return 500

    def __get_stats(self):
        if hasattr(self, 'seasons'):
            return self.seasons
        soup = self.get_soup()
        stats_table = soup.find('table', self.tableClass)
        seasons = stats_table('tr')
        self.seasons = seasons[ 1: ]
        return self.__get_stats()

    def __ext_tag(self, tag, stat_name):
        stats = tag
        stat_class = getattr(self, stat_name + 'Class')
        stat_tag = stats.find('td', stat_class)
        num_val = utils.get_string(stat_tag)
        try:
            return int(num_val)
        except:
            # shown on soccerwiki as "?"
            print '\t' + utils.colored('Stats not available yet', 'red')
            return 0

    def __is_same_league(self, season_tag, league_name):
        link = season_tag('a')[ 2 ]
        if utils.to_ascii(link.get('title').encode('utf-8')) == league_name:
            return True
        return False

    def get_stat(self, field):
        if hasattr(self, field):
            return getattr(self, field)

        league = self.league_name
        for ses in self.__get_stats():
            if self.__is_same_league(ses, league):
                val = self.__ext_tag(ses, field)
                setattr(self, field, val)
                return self.get_stat(field)

    def get_tot_stat(self, stat):
        field = 'tot' + stat
        league = self.league_name
        if hasattr(self, field): return getattr(self, field)

        tot = 0

        for season in self.__get_stats()[ :-1 ]:
            if self.__is_same_league(season, league):
                tot += self.__ext_tag(season, stat)
        setattr(self, field, tot)
        return self.get_tot_stat(stat)

    def get_career_stat(self, stat):
        field = 'career' + stat
        if hasattr(self, field): return getattr(self, field)
        totStatsTag = self.__get_stats()[ -1 ]
        val = self.__ext_tag(totStatsTag, stat)
        setattr(self, field, val)
        return self.get_career_stat(stat)

    def eligible(self, age=21, mins=200, goals=0, v=True):
        col = 'green' if self.age <= age else 'red'
        print '\tAge', ':', utils.colored(str(self.age), col)
        if self.age > age:
            return False
        col = 'green' if self.sesGoals >= goals else 'red'
        print '\tGoals', ':', utils.colored(str(self.sesGoals), col)
        if self.sesGoals < goals:
            return False
        col = 'green' if self.get_stat('mins') >= mins else 'red'
        print '\tMinutes', ':', utils.colored(str(self.get_stat('mins')), col)
        if self.get_stat('mins') < mins:
            return False

        return True

    def get_first_and_last_name(self):
        info = self.get_soup().find('dl')
        headings = [x.text.encode('utf-8') for x in info.findAll('dt')]
        values = [x.text.encode('utf-8') for x in info.findAll('dd')]
        attribs = dict(zip(headings, values))
        req_strs = {'First name', 'Last name'}

        for x in req_strs:
            if not x in attribs.keys():
                return 'Nil', 'Nil'

        return [utils.to_ascii(attribs[x]) for x in req_strs]

    def __str__(self):
        req = variables.attrs_required
        for x in req:
            self.get_stat(x)
            self.get_tot_stat(x)
            self.get_career_stat(x)
        fname, lname = self.get_first_and_last_name()

        to_save = {x: self.__dict__[ x ] for x in variables.attrs_to_save}
        to_save.update({'fname': fname, 'lname': lname, 'league_name':self.league_name})

        return to_save.__str__()
