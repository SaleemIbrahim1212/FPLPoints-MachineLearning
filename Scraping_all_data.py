#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import warnings
import pandas as pd
warnings.filterwarnings('ignore')

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

def get_season_stats_per_player(all_player_links):
    dataframes = [] 
    from time import sleep
    import pandas as pd
    for i in range (len(all_player_links)):
        name, season = get_name_and_season(all_player_links[i])
        print(f"{name} {season} Premier league season.. {(i+1) / len(all_player_links)} Done" )
        player_stats_link = all_player_links[i]
        player_data  = requests.get(player_stats_link)
        #print(player_data)
        player_matches = pd.read_html(player_data.text, match="Match Logs")[0]
        player_matches.columns = player_matches.columns.droplevel()
        player_df = player_matches[player_matches['Comp'] == 'Premier League']
        player_df['name'] = name 
        player_df['season'] = season
        dataframes.append(player_df)
        sleep(5)
    players_df = pd.concat(dataframes)
    return players_df 


def get_name_and_season(url):
    name = url.split('/')[-1].replace("-Match-Logs","")
    name = name.replace('-', ' ')
    season = url.split('/')[7]
    season = season.replace('-', '/')
    #print(f"{name} {season} premier league")
    return name, season 

def get_players_overall_stats(team_urls):
    all_player_links = []
    for i in range(len(team_urls)):
        data = requests.get(team_urls[i])
        soup = BeautifulSoup(data.text)
        squadlog = soup.select('table.stats_table')[0]
        squad_info = pd.read_html(squadlog.text, match="Standard Stats")[0]
        all_player_links.extend(squad_info)
    return all_player_links