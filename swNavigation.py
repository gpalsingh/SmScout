from API import swApi as api
from Utils import smUtils
from Utils import gVars

def chooseNation():
    '''user picks nation of choice
    
    returns:    int, string
    '''
    home = api.HomePage()
    nation_and_link = home.getLeaguesList()
    resp = smUtils.pickOne( nation_and_link )
    return resp
    
def chooseLeague( url ):  
    '''user picks league
    
    url:    url of main league
    
    returns:    int, LeaguePage object
    '''
    page = api.LeaguePage( url )
    print '\nCurrently on ', page.getName()
    league_and_link = page.getLeagues()
    n, new_url = smUtils.pickOne( league_and_link )
    if new_url==page.URL:
        return n, page
    else:
        return n, api.LeaguePage( new_url )

if __name__=="__main__":
    url = chooseNation()
    print chooseLeague( url )
