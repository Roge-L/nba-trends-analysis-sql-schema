import requests
import json
import csv
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints.playerdashboardbyyearoveryear import PlayerDashboardByYearOverYear

# players_dict = players.get_players()
# team_dict = teams.get_teams()

# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/cumestatsplayer.md [PLAYER]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/cumestatsteam.md [TEAM]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/shotchartdetail.md [SHOT]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/boxscoresummaryv2.md [GAME]

# player = cumestatsplayer.CumeStatsPlayer(player_id='2544', game_ids=[])
# player = requests.get()
# team = requests.get()
# shot = requests.get()
# game = requests.get()
# print(players_dict)
# print(player)


def get_all_players():
  d = players.get_players()
  export_csv(d, 'players.csv')


def get_all_teams():
  t = teams.get_teams()
  data = []
  for team in t:
    data.append({"teamID": team['id'], "teamName": team['full_name']})
  export_csv(data, 'teams.csv')


def export_csv(data, filename, headers=None):
  # data is a list of objects
  # assume data is non-empty
  with open(filename, 'w', newline='\n') as csvfile:
    if headers is None:
      fieldnames = list(data[0].keys())
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      for entry in data:
        writer.writerow(entry)

    else:
      writer = csv.DictWriter(csvfile, fieldnames=headers)
      writer.writeheader()
      for entry in data:
        dct = {}
        for i in range(len(headers)):
          dct[headers[i]] = entry[i]
        writer.writerow(dct)


def experimental():
  p = PlayerDashboardByYearOverYear(200746)
  response = p.nba_response.get_data_sets()['ByYearPlayerDashboard']
  export_csv(response['data'], "example.csv", response['headers'])


# get_all_players()
# get_all_teams()
experimental()
