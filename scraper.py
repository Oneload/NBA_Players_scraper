import requests 
from requests.adapters import Retry, HTTPAdapter
import pandas
from bs4 import BeautifulSoup as BS4
from progress.bar import IncrementalBar as bar
import json

#Using request session
requests = requests.Session()
retry = Retry(total=10)
requests.mount('https://', HTTPAdapter(max_retries=retry))

#Gathering data from page 'https://www.basketball-reference.com/players/'
players_by_first_letter_raw: str = requests.get('https://www.basketball-reference.com/players/').text
players_by_first_letter_soup: BS4 = BS4(players_by_first_letter_raw, 'html.parser')
players_by_first_letter_links_tag_ul: BS4 = players_by_first_letter_soup.find('ul', {'class': 'page_index'})
players_by_first_letter_links_tags_li = players_by_first_letter_links_tag_ul.find_all('li')


players_by_first_letter_links: list = []

tag: BS4
for tag in players_by_first_letter_links_tags_li:
    try:
        letter_link = tag.find('a')['href']
    except TypeError:
        pass
       
    players_by_first_letter_links.append(letter_link)
    
    with open('letter_links.txt', 'w+') as file:
        for link in players_by_first_letter_links:
            file.writelines(f'{link}\n')
    

#Gathering players links from <>players_by_first_letter_links_tags<>
players_links_list: list = []

with open('letter_links.txt', 'r') as file:
    letter_link: str
    file = file.readline()
    for letter_link in file:
        players_links_raw: str = requests.get(f'https://www.basketball-reference.com{letter_link.rstrip()}').text
        players_links_soup: BS4 = BS4(players_links_raw, 'html.parser')
        players_links_tags: BS4 = players_links_soup.find('tbody').find_all('tr')
        
        player_link_tag: BS4
        for player_link_tag in players_links_tags:
            player_link: str = player_link_tag.find('a')['href']
            players_links_list.append(player_link)

with open('player_links.txt', 'w+') as file:
    for link in players_links_list:
        file.writelines(f'{link}\n')
        
#Gathering data for players pages and write JSON
data_json: dict = json.load(open('data.json', 'r'))

with open('player_links.txt', 'r') as file:
    file = file.readlines()
    bar = bar('LIST', max=len(file))
    for player_link in file:
        if player_link not in data_json:
            player_data_raw: str = requests.get(f'https://www.basketball-reference.com{player_link.rstrip()}').text
            player_data_soup: BS4 = BS4(player_data_raw, 'html.parser')
            
            name_div: BS4 = player_data_soup.find('div', {'id': 'meta'}).find_all('div')[-1]
            name: str = name_div.find('h1').text

            
            games_played_div: BS4 = player_data_soup.find('span', {'data-tip': "Games"})
            if games_played_div != None:
                games_played: str = games_played_div.find_next('p').find_next().text
            else:
                games_played = None
            
            points_div: BS4 = player_data_soup.find('span', {'data-tip': "Points"})
            if points_div != None:
                points: str = points_div.find_next('p').find_next().text
            else:
                points = None
            
            totalrebounds_div: BS4 = player_data_soup.find('span', {'data-tip': "Total Rebounds"})
            if totalrebounds_div != None:
                totalrebounds: str = totalrebounds_div.find_next('p').find_next().text
            else:
                totalrebounds = None
            
            assists_div: BS4 = player_data_soup.find('span', {'data-tip': "Assists"})
            if assists_div != None:
                assists: str = assists_div.find_next('p').find_next().text
            else:
                assists = None
            
            fieldgoalperc_div: BS4 = player_data_soup.find('span', {'data-tip': "Field Goal Percentage"})
            if fieldgoalperc_div != None:
                fieldgoalperc: str = fieldgoalperc_div.find_next('p').find_next().text
            else:
                fieldgoalperc = None
            
            threepointsfieldgoalperc_div: BS4 = player_data_soup.find('span', {'data-tip': "3-Point Field Goal Percentage"})
            if threepointsfieldgoalperc_div != None:
                threepointsfieldgoalperc: str = threepointsfieldgoalperc_div.find_next('p').find_next().text
            else:
                threepointsfieldgoalperc = None
            
            freethroughperc_div: BS4 = player_data_soup.find('span', {'data-tip': "Free Throw Percentage"})
            if freethroughperc_div != None:
                freethroughperc: str = freethroughperc_div.find_next('p').find_next().text
            else:
                freethroughperc = None
            
            effectivefieldgoalperc_div: BS4 = player_data_soup.find('span', {'data-tip': "<strong>Effective Field Goal Percentage</strong><br>This statistic adjusts for the fact that a 3-point field goal is worth one more point than a 2-point field goal."})
            if effectivefieldgoalperc_div != None:
                effectivefieldgoalperc: str = effectivefieldgoalperc_div.find_next('p').find_next().text
            else:
                effectivefieldgoalperc = None
            
            playereffrating_div: BS4 = player_data_soup.find('span', {'data-tip': "<b>Player Efficiency Rating</b><br>A measure of per-minute production standardized such that the league average is 15."})
            if playereffrating_div != None:
                playereffrating: str = playereffrating_div.find_next('p').find_next().text
            else:
                playereffrating = None
            
            winshares_div: BS4 = player_data_soup.find('span', {'data-tip': "<b>Win Shares</b><br>An estimate of the number of wins contributed by a player."})
            winshares: str = winshares_div.find_next('p').find_next().text
            
            player_data: dict = {f'{player_link}':{
                                'name': name,
                                'games_played': games_played,
                                'points': points,
                                'totalrebounds': totalrebounds,
                                'assists': assists,
                                'fieldgoalperc': fieldgoalperc,
                                'threepointsfieldgoalperc': threepointsfieldgoalperc,
                                'freethroughperc': freethroughperc,
                                'effectivefieldgoalperc': effectivefieldgoalperc,
                                'playereffrating': playereffrating,
                                'winshares': winshares,
                                }
                        }
            
            data_json.update(player_data)
            json.dump(data_json, open('data.json', 'w'))
        bar.next()
    bar.finish()

