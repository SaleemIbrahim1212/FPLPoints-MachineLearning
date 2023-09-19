import requests
from bs4 import BeautifulSoup
import pandas as pd 
from time import sleep


'''
Returns all the teams for the particular season given 
'''
def get_team_links(league_year):
    league_url = f'https://fbref.com/en/comps/9/{league_year}/{league_year}-Premier-League-Stats' 
    data = requests.get(league_url)
    print(data)
    soup = BeautifulSoup(data.text)
    league_standings = soup.select('table.stats_table')[0]
    links = league_standings.find_all('a')
    links = [l.get('href') for l in links]
    links = [ l for l in links if '/squads/' in l]
    team_links = [f'https://fbref.com{l}' for l in links ]
    return team_links 

'''
Takes in the team links and extracts the team name of the player of that particular season out of it 
'''
def get_squads_name(team_link):
    squad = [] 
    for team in team_link: 
        team_name = team.split("/")[-1]
        cleaned_team = team_name.replace("Stats", "")
        squad.append(cleaned_team)
    return squad




def get_team_statistics(league_year, teams):
    all_team_stats =[]
    for i in range(len(teams)):
        link = f"https://fbref.com/en/squads/b8fd03ef/{league_year}/matchlogs/c9/schedule/{teams[i]}Scores-and-Fixtures-Premier-League"
        data = requests.get(link)
        print(data)
        team_stats =pd.read_html(data.text, match="Scores & Fixtures")[0]
        team_stats['team_name'] = teams[i].replace("-", " ")
        team_stats['season'] = league_year.replace('-','/')
        all_team_stats.append(team_stats)
        sleep(5)
    return all_team_stats

        


'''
Returns the player links for each player based on the team url links provided 
'''
def get_players_links(team_urls):
    all_player_links = []
    for i in range(len(team_urls)):
        data = requests.get(team_urls[i])
        soup = BeautifulSoup(data.text)
        matchlog = soup.select('table.stats_table')[0]
        player_links = matchlog.find_all('a')    
        player_links = [l.get('href') for l in player_links]
        player_links = [l for l in player_links if '/matchlogs/' in l]
        player_links = [f'https://fbref.com{l}' for l in player_links]
        all_player_links.extend(player_links)
    return all_player_links

'''
Gets all the stats for each player, on each match based on the player links, 
it takes in the player links and scrapes 

Input: all_player_links, links in the format of the player ie 
'''
def get_season_stats_per_player(all_player_links):
    dataframes = [] 
    for i in range (len(all_player_links)):
        name, season = get_name_and_season(all_player_links[i])
        print(f"{name} {season} Premier league season.. {((i+1) / len(all_player_links) )  * 100} Done" )
        player_stats_link = all_player_links[i]
        player_data  = requests.get(player_stats_link)
        #print(player_data)
        player_matches = pd.read_html(player_data.text, match="Match Logs")[0]
        player_matches.columns = player_matches.columns.droplevel()
        player_df = player_matches[player_matches['Comp'] == 'Premier League']
        player_df['name'] = name 
        player_df['season'] = season
        dataframes.append(player_df)
        print('Sleeping for 5 secs')
        sleep(5)
    players_df = pd.concat(dataframes)
    return players_df 

'''
Helper function that takes in the links and spits out the name and season 
'''
def get_name_and_season(url):
    name = url.split('/')[-1].replace("-Match-Logs","")
    name = name.replace('-', ' ')
    season = url.split('/')[7]
    season = season.replace('-', '/')
    #print(f"{name} {season} premier league")
    return name, season 


'''
Gets all the data for the player based on the year provided
'''
def get_player_data(team_years):
    all_season_stats = [] 
    players_link = get_players_links(team_years)
    all_season_stats.append( get_season_stats_per_player(players_link)) 
    player_data = pd.concat(all_season_stats)
    return player_data    
    