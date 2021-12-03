import csv
import os
import time
import datetime
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints.leaguedashteamstats import LeagueDashTeamStats
from nba_api.stats.endpoints.leaguedashplayerstats import LeagueDashPlayerStats
from nba_api.stats.endpoints.shotchartdetail import ShotChartDetail
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder
from nba_api.stats.endpoints.playerprofilev2 import PlayerProfileV2

# 1612709909

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


def export_game_ids(lst, filename):
  with open(filename, 'w') as f:
    for a in lst:
      f.write("\n".join(["%s" % (a)]) + "\n")


def import_list(filename):
  # import an a-b tuple list from file
  lst = []
  with open(filename, 'r') as f:
    for line in f:
      lst.append(tuple(line.split()))
  return lst


def import_game_ids(filename):
  lst = []
  with open(filename, 'r') as f:
    for line in f:
      lst.append(line.strip())
    return lst


def get_nba_season(datestr):
  def t(_str):
    return datetime.datetime.strptime(_str, "%Y-%m-%d").date()

  date = t(datestr)
  seasons = [
    (t("2011-12-01"), t("2012-06-30"), "2011-12"),
    (t("2012-10-01"), t("2013-06-30"), "2012-13"),
    (t("2013-10-01"), t("2014-06-30"), "2013-14"),
    (t("2014-10-01"), t("2015-06-30"), "2014-15"),
    (t("2015-10-01"), t("2016-06-30"), "2015-16"),
    (t("2016-10-01"), t("2017-06-30"), "2016-17"),
    (t("2017-9-01"), t("2018-06-30"), "2017-18"),
    (t("2018-9-01"), t("2019-06-30"), "2018-19"),
    (t("2019-10-01"), t("2020-10-30"), "2019-20"),
    (t("2020-12-01"), t("2021-07-30"), "2020-21"),  
  ]

  for s in seasons:
    if s[0] <= date <=s[1]:
      return s[2]

  print(datestr)


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
      res = LeagueDashPlayerStats(season=season, league_id_nullable='00').league_dash_player_stats.get_dict()
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
      time.sleep(0.25)

    
    export_list(list(self.players), 'player-team.txt')


  def get_teams(self):
    # t = teams.get_teams()
    # data = []
    # for team in t:
    #   data.append(extract_keys(team, ['id', 'full_name'], ['teamID', 'teamName']))
    # export_csv(data, 'Team.csv')
    target_seasons = [
      "2020-21", "2019-20", "2018-19", "2017-18", "2016-17",
      "2015-16", "2014-15", "2013-14", "2012-13", "2011-12" 
    ]
    t = LeagueDashTeamStats(season=target_seasons[-1])
    teams = t.get_data_frames()[0]
    print(teams)


  def get_player_shots(self, start, stop):
    player_teams = import_list('player-team.txt')
    game_ids = set(import_game_ids('game-ids.txt'))
    hh = False

    progress = start
    for pt in player_teams[start:stop]:
      player = pt[0]
      team = pt[1]

      s = ShotChartDetail(team_id=team, player_id=player, context_measure_simple='FGA', timeout=30)
      shots = s.get_data_frames()[0].to_dict(orient='records')
      res = []
      for shot in shots:
        if shot['GAME_ID'] not in game_ids:
          continue
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
    res = LeagueGameFinder(season_nullable=','.join(target_seasons), league_id_nullable='00')
    games = res.get_data_frames()[0].to_dict(orient='records')
    data = []

    team_ids = set([
      1610612737,
      1610612738,
      1610612739,
      1610612740,
      1610612741,
      1610612742,
      1610612743,
      1610612744,
      1610612745,
      1610612746,
      1610612747,
      1610612748,
      1610612749,
      1610612750,
      1610612751,
      1610612752,
      1610612753,
      1610612754,
      1610612755,
      1610612756,
      1610612757,
      1610612758,
      1610612759,
      1610612760,
      1610612761,
      1610612762,
      1610612763,
      1610612764,
      1610612765,
      1610612766
    ])

    home_games = {}
    away_games = {}

    game_ids = []

    for game in games:
      isAway = '@' in game['MATCHUP']
      id = game['GAME_ID']
      if game['TEAM_ID'] not in team_ids:
        continue

      if not isAway:
        home_games[id] = game
      else:
        away_games[id] = game

    for key in list(home_games.keys()):
      if key not in home_games or key not in away_games:
        continue
      home = home_games[key]
      away = away_games[key]
      dct = {
        'gameID': home['GAME_ID'],
        'teamID': home['TEAM_ID'],
        'oppTeamID': away['TEAM_ID'],
        'homeScore': home['PTS'],
        'awayScore': away['PTS'],
        'year': get_nba_season(home['GAME_DATE'])
      }
      data.append(dct)
      game_ids.append(home['GAME_ID'])
    export_csv(data, 'Game.csv')
    export_game_ids(game_ids, 'game-ids.txt')
      

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
  # rm('./Game.csv')

  nba = NBA()
  # nba.get_player_stats()
  # nba.get_teams()
  # nba.get_player_shots(0, 500)
  # nba.get_player_shots(500, 1000)
  # nba.get_player_shots(1000, 1500)
  # nba.get_player_shots(1500, 2000)
  # nba.get_player_shots(2000, 2863)
  nba.get_games()


# will take about 2 hours!
generate_all()
# t = TeamDetails(team_id=1610612743)
# t = LeagueGameFinder(game_id_nullable='0022100003', league_id_nullable='00')
# t = PlayerProfileV2(player_id='204456')
# print(t.get_data_frames())
