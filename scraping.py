import requests
from bs4 import BeautifulSoup

def get_team_links(league_year):
    league_url = f'https://fbref.com/en/comps/9/{league_year}/{league_year}-Premier-League-Stats' 
    data = requests.get(league_url)
    soup = BeautifulSoup(data.text)
    league_standings  = soup.select('table.stats_table')[0]
    links = league_standings.find_all('a')
    links = [l.get('href') for l in links]
    links = [ l for l in links if '/squads/']
    team_links = [f'https://fbref.com{l}' for l in links ]
    return team_links 


    