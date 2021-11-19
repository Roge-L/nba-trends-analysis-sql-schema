import requests
import json
import csv
import os
from nba_api.stats.static import players, teams
# from nba_api.stats.endpoints.playerdashboardbyyearoveryear import PlayerDashboardByYearOverYear
from nba_api.stats.endpoints.leaguedashplayerstats import LeagueDashPlayerStats


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


def export_csv(data, filename, headers=None, mode="w"):
  # data is a list of objects
  # assume data is non-empty
  with open(filename, mode, newline='\n') as csvfile:
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


def extract_keys(data, keys, labels):
  # formatting tool for extracting and renaming keys
  dct = {}
  for key, label in zip(keys, labels):
    dct[label] = data[key]
  return dct


def get_player_stats():
  target_seasons = [
    "2020-21", "2019-20", "2018-19", "2017-18", "2016-17",
    "2015-16", "2014-15", "2013-14", "2012-13", "2011-12" 
  ]     

  def format_additional(dct):
    cats = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'PF']
    gp = dct['GP']
    for cat in cats:
      dct[cat] = round(dct[cat] / (1 if gp == 0 else gp), 1)
    dct['eFG%'] = round((dct['FGM'] - dct['3PTM'] +  1.5 * dct['3PTM']) / (1 if dct['FGA'] == 0 else dct['FGA']), 3)
    dct['year'] = season

  for season in target_seasons:
    results = []
    res = LeagueDashPlayerStats(season=season).league_dash_player_stats.get_dict()
    headers = res['headers']
    players = res['data']
    for player in players:
      dct = {}
      for header, stat in zip(headers, player):
        dct[header] = stat
      results.append(extract_keys(
        dct,
        ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'GP', 'PTS', 'FGA', 'FGM', 'FG_PCT', 'FG3A', 'FG3M', 'FG3_PCT', 'FTA', 'FTM', 'FT_PCT', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'PF'],
        ['playerID', 'playerName', 'teamID', 'GP', 'PTS', 'FGA', 'FGM', 'FG%', '3PTA', '3PTM', '3PT%', 'FTA', 'FTM', 'FT%', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'PF']
      ))
      format_additional(results[-1])
    export_csv(results, 'Player.csv', mode='a')


def get_all_teams():
  t = teams.get_teams()
  data = []
  for team in t:
    data.append(extract_keys(team, ['id', 'full_name'], ['teamID', 'teamName']))
  export_csv(data, 'Team.csv')


def rm(path):
  try:
    os.remove(path)
    os.remove('./Team.csv')
  except OSError:
    pass


def generate_all():
  rm('./Player.csv')
  rm('./Team.csv')
  get_player_stats()
  get_all_teams()


# may take a long time!
generate_all()
