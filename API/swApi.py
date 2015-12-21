#-*- coding: utf-8 -*-

#=========================================================================
#
#                       IMPORT STATEMENTS
#
#=========================================================================
from Utils import smUtils
from Utils import gVars
import requests
try:
    import BeautifulSoup as bs
except:
    import bs4 as bs
import re

#=========================================================================
#
#                      GLOBAL VARIABLES
#
#=========================================================================
homepage = gVars.homepage
files = gVars.files
test_folder= gVars.test_folder

#=========================================================================
#
#                           TODO
#
#=========================================================================
# FIX FIRST AND LAST NAME SAVING PROBLEM

#=========================================================================
#
#                       CLASS DEFINITIONS
#
#=========================================================================
class Page(object):
    def __init__( self, url=homepage ):
        self.URL = url
        
    def getSoup(self):
        """returns: soup from URL"""
        if hasattr(self, 'soup'): return self.soup
        handle = requests.get( self.URL )
        self.HTML = handle.content
        self.soup = bs.BeautifulSoup( self.HTML )
        handle.close()
        return self.soup
        
class HomePage( Page ):
    def getLeaguesList( self ):
        """returns: ( Nation name, link ) dictionary"""
        lists = self.getSoup()('select')
        domLeagues = lists[1]
        options = domLeagues('option')
        nations = options[1:]
        maps = [ smUtils.extractAnchor(x,'value') for x in nations ]
        nameToLink = dict( maps )
        return nameToLink
        
class LeaguePage( Page ):
    def getNation( self ):
        """returns: name of nation in which league is played"""
        if hasattr(self,'nation'): return self.nation
        title = self.getSoup().find('title')
        line = smUtils.getString(title)
        name = line.split(' - ')[2]
        self.nation = name
        return self.nation
        
    def getName( self ):
        """returns: name of league"""
        if hasattr(self, 'lname'): return self.lname
        tag = self.getSoup().find('h1')
        self.lname = smUtils.getString( tag.text )
        return self.lname
        
    def getLeagues( self ):
        """returns: {League name : link} dict"""
        if hasattr(self,'leagues'): return leagues
        tree = self.getSoup()('ul','left-tree')
        links = tree[0]('a')
        nations = links[:1]
        if len(links)>2: nations += links[2:]
        name_and_link = [ smUtils.extractAnchor(x) for x in nations ]
        self.leagues = dict( name_and_link )
        return self.leagues
        
    def getTable( self ):
        """returns: LeagueTable object"""
        return LeagueTable( self.getSoup(), self.getName() )
        
class LeagueTable():
    tableClass = "leaguetable sortable table detailed-table"
    team_class = "text team large-link" 
     
    def __init__( self, page_soup, league_name ):
        """extracts table tags from parent's soup
        page_soup : soup of League
        league_name : name of league
        """
        self.soup = page_soup.find('table', self.tableClass )
        self.lname = league_name
        
    def getTeams( self ):
        """generator method yields Team instances"""
        rows = self.soup('tr')[1:-2]
       
        for tag in rows:
            yield Team(tag, self.lname)
        
class Team( Page ):
    linkClass="text team large-link"
    matchesClass="number total mp"
    winsClass="number total won total_won"
    drawsClass="number total drawn total_drawn"
    lostClass="number total lost total_lost"
    gdClass="number gd"
    pointsClass="number points" 
    squadClass = 'squad-container'
    
    def __init__( self, team_tag, league_name ):
        """sets: tag, name and URL"""
        self.tag = team_tag
        a = self.tag.find('a')        
        self.name, self.URL = smUtils.extractAnchor(a)             
        self.lname = league_name
        
    def getPlayers(self):
        """generator which yields Player objects"""
        div = self.getSoup().find('div', self.squadClass )
        if div is None:
            yield None
        cats = [smUtils.getString(x).strip('s') for x in div('th')]
        bodies = div('tbody')
        grps = [ x('td', {'style':'vertical-align: top;'}) for x in bodies ]
        
        for grp,pos in zip(grps, cats)[:-1]: #last one is coaches
            #print 'Getting players - ', pos
            for pl in grp:
                yield Player( pl, pos, self.name, self.lname )
    
class Player(Page):
    tableClass = 'playerstats career sortable table' 
    minsClass="number statistic game-minutes available"
    appsClass="number statistic appearances available"
    linupsClass="number statistic lineups available"
    subsClass="number statistic subs-in available"
    subsonClass="number statistic subs-out available"
    benchClass="number statistic subs-on-bench available"
    goalsClass="number statistic goals available"
    yellowsClass="number statistic yellow-cards available"
    yellow2Class="number statistic 2nd-yellow-cards available"
    redsClass="number statistic red-cards available"
    ageDiv = {'style':'padding-left: 27px;'}
    
    def __init__(self, tag, pos, tname, lname):
        """sets: tag, pos , team, season goals, 
        season appearances, name, URL, age and name
        
        tag: player tag on league page
        pos: playing position
        tname: team's name of which player is a part
        lname: name of league in which player plays
        """
        self.tag = tag
        self.pos = pos
        self.team = tname
        self.sesApps, self.sesGoals = re.findall('> ([\d]+) <', str(self.tag) )
        self.name, self.URL = smUtils.extractAnchor( self.tag.find('a') )
        self.age = self.__getAge()        
        self.lname = lname
     
    def __getAge(self):
        """returns: age of player
        500 if no data available
        """
        try:
            age = re.findall('([\d]{2}) years', str(self.tag) )[0]   
            return int(age)
        except:
            print '\t'+smUtils.colored('No age data available', 'red')
            return 500
              
    def __getStats( self ):
        """returns: <tr> columns of each season's stats as list"""
        if hasattr(self, 'seasons'): return self.seasons
        soup = self.getSoup()
        statsTable = soup.find('table', self.tableClass)
        seasons = statsTable('tr')
        self.seasons = seasons[1:]
        return self.__getStats()       
         
    def __extTag( self, tag, statName ):
        """function to get individual stat
        
        tag: the season's tag
        statName: name of stat to extract
        
        returns: integer
            0 on error
        """
        stats = tag
        stat_class = getattr( self, statName+'Class' )
        statTag = stats.find('td', stat_class )
        numVal = smUtils.getString( statTag )
        try:
            return int(numVal)
        except:
            #shown on soccerwiki as "?"
            print '\t'+smUtils.colored('Stats not available yet', 'red')
            return 0 
    
    def __isSameLeague( self, season_tag, league_name ): 
            """determines if given tag is for the same league 
            returns: boolean
            """
            link = season_tag('a')[2]
            if smUtils.toAscii( link.get('title').encode('utf-8') ) == league_name:
                return True
            return False
         
    def getStat( self, field ):
        """ function to get a particular stat for this season
        
        field: "mins", "apps", "goals", etc.
        
        returns: stat for latest league as integer
        """
        if hasattr(self, field): return getattr(self, field)
        
        league = self.lname
        for ses in self.__getStats():
            if self.__isSameLeague( ses, league ):
                val = self.__extTag( ses, field )
                setattr(self, field, val)
                return self.getStat( field )
       
    def getTotStat( self, stat):
        """gives total of player's career for given stat
        in the same league as he is now
        
        stat: "mins", "apps", "goals", etc.
        
        returns: integer
        """
        field = 'tot' + stat
        league = self.lname
        if hasattr(self, field): return getattr(self, field)
        
        tot = 0   

        for season in self.__getStats()[:-1]:
            if self.__isSameLeague( season, league ):
                tot += self.__extTag(season, stat)
        setattr(self, field, tot)
        return self.getTotStat( stat )
        
                
    def getCareerStat( self, stat ):
        """gives total of player's full career for given stat
        
        stat: "mins", "apps", "goals", etc.
        
        returns: integer"""
        field = 'career'+stat
        if hasattr(self, field ): return getattr(self, field)
        totStatsTag = self.__getStats()[-1]
        val = self.__extTag( totStatsTag, stat )
        setattr( self, field, val )
        return self.getCareerStat( stat )
        
    def eligible(self, age=21, mins=200, goals=0, v=True ):
        col = 'green' if self.age<=age else 'red'
        print '\tAge', ':', smUtils.colored( str(self.age), col)
        if self.age>age:
             return False
        col = 'green' if self.sesGoals>=goals else 'red'
        print '\tGoals', ':', smUtils.colored( str(self.sesGoals), col)
        if self.sesGoals<goals:
            return False
        col = 'green' if self.getStat('mins')>=mins else 'red'
        print '\tMinutes', ':', smUtils.colored( str(self.getStat('mins')), col)
        if self.getStat('mins')<mins:
           return False
             
        return True

    def __getFirstAndLastName(self):
        """gets first and last name of player
        
        returns:    (first name, last name) tuple
        on error:   ('Nil', 'Nil')
        """
        info = self.getSoup().find('dl')
        attribs = info.text.encode('utf-8').split('\n')
        name = []
        
        for x in ['First name', 'Last name']:
            if x in attribs:
                i = attribs.index(x)
                name.append( smUtils.toAscii(attribs[i+1]) )
            else:
                return ('Nil', 'Nil')
                
        return name
    
    def __str__( self ):
        """makes dict for latest season's stats and player info"""
        req = gVars.attrs_required
        for x in req:
            self.getStat(x)
            self.getTotStat(x)
            self.getCareerStat(x)
        fname, lname = self.__getFirstAndLastName()
      
        toSave = { x:self.__dict__[x] for x in gVars.attrs_to_save }
        toSave.update({'fname':fname, 'lname':lname})
                             
        return toSave.__str__()
 
 
