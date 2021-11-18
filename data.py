import requests
import json
from nba_api.stats.endpoints import cumestatsplayer
from nba_api.stats.static import players, teams

players_dict = players.get_players()
team_dict = teams.get_teams()

# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/cumestatsplayer.md [PLAYER]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/cumestatsteam.md [TEAM]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/shotchartdetail.md [SHOT]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/boxscoresummaryv2.md [GAME]

player = cumestatsplayer.CumeStatsPlayer(GameIDs='21700807', PlayerID='2544', LeagueID='00', Season='2019-20', SeasonType='Regular+Season')
# player = requests.get()
# team = requests.get()
# shot = requests.get()
# game = requests.get()
# print(players_dict)
print(player)