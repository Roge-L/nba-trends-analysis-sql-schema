import csv
import os
import time
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints.leaguedashplayerstats import LeagueDashPlayerStats
from nba_api.stats.endpoints.shotchartdetail import ShotChartDetail
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder
from nba_api.stats.endpoints.boxscorematchups import BoxScoreMatchups

# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/cumestatsplayer.md [PLAYER]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/cumestatsteam.md [TEAM]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/shotchartdetail.md [SHOT]
# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/boxscoresummaryv2.md [GAME]


def export_csv(data, filename, headers=None, mode="w", hasHeader=False):
  # data is a list of objects
  # assume data is non-empty
  with open(filename, mode, newline='\n') as csvfile:
    if len(data) == 0:
      return

    if headers is None:
      fieldnames = list(data[0].keys())
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      if not hasHeader:
        writer.writeheader()
      for entry in data:
        writer.writerow(entry)

    else:
      writer = csv.DictWriter(csvfile, fieldnames=headers)
      if not hasHeader:
        writer.writeheader()
      for entry in data:
        dct = {}
        for i in range(len(headers)):
          dct[headers[i]] = entry[i]
        writer.writerow(dct)


def extract_keys(data, keys, labels, defaults=[]):
  # formatting tool for extracting and renaming keys
  # set key as None and pass generator function in defaults if value is dynamically generated
  dct = {}
  defaults = iter(defaults)
  for key, label in zip(keys, labels):
    if key is None:
      dct[label] = next(defaults)(data)
    else:
      dct[label] = data[key]
  return dct


def export_list(lst, filename):
  # export a-b tuple list to file 
  with open(filename, 'w') as f:
    for a, b in lst:
      f.write("\n".join(["%s %s" % (a, b)]) + "\n")


def import_list(filename):
  # import an a-b tuple list from file
  lst = []
  with open(filename, 'r') as f:
    for line in f:
      lst.append(tuple(line.split()))
  return lst


class NBA:
  # players = set([(1629690, 1610612741)]) # list of (playerID, teamID) tuples
  players = set()

  def get_player_stats(self):
    target_seasons = [
      "2020-21", "2019-20", "2018-19", "2017-18", "2016-17",
      "2015-16", "2014-15", "2013-14", "2012-13", "2011-12" 
    ]     

    def format_additional(dct):
      cats = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'PF']
      gp = dct['GP']
      for cat in cats:
        dct[cat] = round(dct[cat] / (1 if gp == 0 else gp), 1)

    hh = False
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
          ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', None, 'GP', 'PTS', 'FGA', 'FGM', 'FG_PCT', None, 'FG3A', 'FG3M', 'FG3_PCT', 'FTA', 'FTM', 'FT_PCT', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'PF'],
          ['playerID', 'playerName', 'teamID', 'year', 'GP', 'PTS', 'FGA', 'FGM', 'FG%', 'eFG%', '3PTA', '3PTM', '3PT%', 'FTA', 'FTM', 'FT%', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'PF'],
          [
            lambda _: season,
            lambda dct: round((dct['FGM'] - dct['FG3M'] +  1.5 * dct['FG3M']) / (1 if dct['FGA'] == 0 else dct['FGA']), 3),
          ]
        ))
        format_additional(results[-1])
        self.players.add((dct['PLAYER_ID'], dct['TEAM_ID']))
      export_csv(results, 'Player.csv', mode='a', hasHeader=hh)
      hh = True
      time.sleep(0.5)

    
    export_list(list(self.players), 'player-team.txt')


  def get_all_teams(self):
    t = teams.get_teams()
    data = []
    for team in t:
      data.append(extract_keys(team, ['id', 'full_name'], ['teamID', 'teamName']))
    export_csv(data, 'Team.csv')


  def get_player_shots(self, start, stop):
    player_teams = import_list('player-team.txt')
    hh = False

    progress = start
    for pt in player_teams[start:stop]:
      player = pt[0]
      team = pt[1]
      s = ShotChartDetail(team_id=team, player_id=player, context_measure_simple='FGA', timeout=30)
      shots = s.get_data_frames()[0].to_dict(orient='records')
      res = []
      for shot in shots:
        res.append(extract_keys(shot, 
          [None, 'PLAYER_ID', 'SHOT_DISTANCE', 'GAME_ID', None, 'SHOT_MADE_FLAG'], 
          ['shotID', 'playerID', 'shotDistance', 'gameID', 'clutchTime', 'shotResult'],
          [
            lambda dct: int(str(dct['GAME_ID']) + str(dct['GAME_EVENT_ID'])), 
            lambda dct: 1 if dct['PERIOD'] == 4 and dct['MINUTES_REMAINING'] < 3 else 0
          ]
        ))
      export_csv(res, f'Shot({start}-{stop}).csv', mode='a', hasHeader=hh)
      hh = True
      print(progress)
      progress += 1
      time.sleep(0.5)


  def get_games(self):
    target_seasons = [
      "2020-21", "2019-20", "2018-19", "2017-18", "2016-17",
      "2015-16", "2014-15", "2013-14", "2012-13", "2011-12" 
    ]
    res = LeagueGameFinder(season_nullable=','.join(target_seasons))
    games = res.get_data_frames()[0].to_dict(orient='records')
    data = []

    home_games = {}
    away_games = {}

    for game in games:
      isAway = '@' in game['MATCHUP']
      id = game['GAME_ID']
      if not isAway:
        home_games[id] = game
      else:
        away_games[id] = game

    for key in list(home_games.keys()):
      home = home_games[key]
      away = away_games[key]
      dct = {
        'gameID': home['GAME_ID'],
        'teamID': home['TEAM_ID'],
        'oppTeamID': away['TEAM_ID'],
        'homeScore': home['PTS'],
        'awayScore': away['PTS']
      }
      data.append(dct)
    export_csv(data, 'Game.csv')
      

def rm(path):
  try:
    os.remove(path)
    os.remove('./Team.csv')
  except OSError:
    pass


def generate_all():
  # rm('./Player.csv')
  # rm('./Team.csv')
  # rm('./Shot(0-500).csv')
  # rm('./Shot(500-1000).csv')
  # rm('./Shot(1000-1500).csv')
  # rm('./Shot(1500-2000).csv')
  # rm('./Shot(2000-2863).csv')
  rm('./Game.csv')

  nba = NBA()
  # nba.get_player_stats()
  # nba.get_all_teams()
  # nba.get_player_shots(0, 500)
  # nba.get_player_shots(500, 1000)
  # nba.get_player_shots(1500, 2000)
  # nba.get_player_shots(2000, 2863)
  nba.get_games()


# will take about 2 hours!
generate_all()
