DROP VIEW IF EXISTS FG_Threes CASCADE;
DROP VIEW IF EXISTS FG_Twos CASCADE;
DROP VIEW IF EXISTS FG_Proportions CASCADE;
DROP VIEW IF EXISTS Shot_Freq_Latest CASCADE;
DROP VIEW IF EXISTS Shot_Freq_Earliest CASCADE;

DROP VIEW IF EXISTS Top_5_Scorers CASCADE;
DROP VIEW IF EXISTSGame_Scores CASCADE;
DROP VIEW IF EXISTS Average_Player_Stats CASCADE;
DROP VIEW IF EXISTS Winning_Losing_FG CASCADE;

DROP VIEW IF EXISTS PF_Stats CASCADE;
DROP VIEW IF EXISTS FTA CASCADE;
DROP VIEW IF EXISTS Clutch_FG CASCADE;


-- get 3pts attempted, made, pct by season
CREATE VIEW FG_Threes AS
  SELECT 
    year, 
    threes_attempted, 
    threes_made, 
    ROUND((CAST(threes_made AS FLOAT) / CAST (threes_attempted AS FLOAT))::numeric, 3) AS threes_fg_pct 
  FROM
    (SELECT year, count(*) AS threes_attempted
    FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player) sq11
    WHERE shotDistance >= 24
    GROUP BY year) sq1
    
    NATURAL JOIN

    (SELECT year, count(*) AS threes_made
    FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player) sq21
    WHERE shotDistance >= 24 AND shotResult=TRUE
    GROUP BY year) sq2
  ORDER BY year DESC;

-- get 2s attempted, made, pct by season
CREATE VIEW FG_Twos AS
  SELECT 
    year, 
    twos_attempted, 
    twos_made, 
    ROUND((CAST(twos_made AS FLOAT) / CAST (twos_attempted AS FLOAT))::numeric, 3) AS twos_fg_pct 
  FROM
    (SELECT year, count(*) AS twos_attempted
    FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player) sq11
    WHERE shotDistance < 24
    GROUP BY year) sq1
    
    NATURAL JOIN

    (SELECT year, count(*) AS twos_made
    FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player) sq21
    WHERE shotDistance < 24 AND shotResult=TRUE
    GROUP BY year) sq2
  ORDER BY year DESC;

-- amalgamate previous two queries, get proportion of twos and threes 
CREATE VIEW FG_Proportions
  SELECT 
    year, 
    ROUND((CAST(threes_attempted AS FLOAT) / CAST((threes_attempted + twos_attempted) AS FLOAT))::numeric, 3) AS proportion_threes,
    ROUND((CAST(twos_attempted AS FLOAT) / CAST((threes_attempted + twos_attempted) AS FLOAT))::numeric, 3) AS proportion_twos  
  FROM FG_Twos NATURAL JOIN FG_Threes
  ORDER BY year DESC;

-- get freq of shots by range, 2020-2021 season
CREATE VIEW Shot_Freq_Latest AS
  SELECT 2 * s.d AS distance_ft, count(t.shotDistance)
  FROM 
    generate_series(0, 20) s(d) LEFT OUTER JOIN (
      SELECT * FROM 
      (SELECT playerID, year FROM Player) p NATURAL JOIN Shot
      WHERE year='2020-21'
    ) t ON s.d = floor(t.shotDistance / 2)
  GROUP BY s.d
  ORDER BY s.d;

-- get freq of shots by range, 2011-2012 season
CREATE VIEW Shot_Freq_Earliest AS
  SELECT 2 * s.d AS distance_ft, count(t.shotDistance)
  FROM 
    generate_series(0, 20) s(d) LEFT OUTER JOIN (
      SELECT * FROM 
      (SELECT playerID, year FROM Player) p NATURAL JOIN Shot
      WHERE year='2011-12'
    ) t ON s.d = floor(t.shotDistance / 2)
  GROUP BY s.d
  ORDER BY s.d;

-- correlation betweens games won and 3 point frequency

-----------------------------------------------------------------------------------------------------

-- top 5 scorers per season, ppg, 3pt%
CREATE VIEW Top_5_Scorers AS
  SELECT playerName, year, PTS, ThreePTA, FGA, ROUND(percent_threes::numeric, 3)
  FROM (
    SELECT 
      playerName, 
      year, 
      PTS, 
      ThreePTA,
      FGA,
      CASE
        WHEN FGA = 0 THEN 0
        ELSE CAST(ThreePTA AS FLOAT) / CAST(FGA AS FLOAT)
      END as percent_threes,
    ROW_NUMBER() OVER (PARTITION BY year ORDER BY PTS DESC)
    AS rn
    FROM Player
  ) tmp 
  WHERE rn <= 3
  ORDER BY year, PTS DESC;

-- get min, avg, max scores for games in each season
CREATE VIEW Game_Scores AS
  SELECT year, min(homeScore), ROUND(avg(homeScore)::numeric, 1), max(homeScore)
  FROM Game
  GROUP BY year
  ORDER BY year DESC;

-- sum of all stats by year
CREATE VIEW Average_Player_Stats AS
  SELECT 
    year, 
    ROUND(avg(PTS)::numeric, 1) AS PTS,
    ROUND(avg(ThreePTM / GP)::numeric, 1) AS ThreePTM,
    ROUND(avg(FTM / GP)::numeric, 1) AS FTM,
    ROUND(avg(AST)::numeric, 1) AS AST,
    ROUND(avg(REB)::numeric, 1) AS REB,
    ROUND(avg(STL)::numeric, 1) AS STL,
    ROUND(avg(BLK)::numeric, 1) AS BLK,
    ROUND(avg(TOV)::numeric, 1) AS TOV
  FROM Player
  GROUP BY year
  ORDER BY year DESC;

-- winning and losing teams fg%, 3pt% (regular season and playoff)
CREATE VIEW Winning_Losing_FG AS
  SELECT year, teamName, home_wins + away_wins AS wins FROM
    (SELECT year, teamName, count(*) AS home_wins
    FROM Game NATURAL JOIN Team
    WHERE homeScore > awayScore
    GROUP BY year, teamName) sq1

    NATURAL JOIN

    (SELECT year, teamName, count(*) AS away_wins
    FROM Game JOIN Team ON oppTeamID = Team.teamID
    WHERE awayScore > homeScore
    GROUP BY year, teamName) sq2
  ORDER BY year, wins DESC;

-- offensive, defensive rating by year

-----------------------------------------------------------------------------------------------------

-- number of fouls per season, per player
CREATE VIEW PF_Stats AS
  SELECT year, ROUND(sum(PF * GP)::numeric, 0), ROUND(avg(PF)::numeric, 2) as avg_pf
  FROM Player 
  GROUP BY year 
  ORDER BY year ASC;

-- fta per game, per player per game
CREATE VIEW FT_Stats AS
  SELECT year, sum(FTA), ROUND(avg(CAST(FTA AS FLOAT) / CAST(GP AS FLOAT))::numeric, 2) as avg_fta
  FROM Player
  GROUP BY year
  ORDER BY year ASC;

-- percentages of clutch shots in tight games compared to average
CREATE VIEW Clutch_FG AS
  SELECT year, fg_pct, clutch_fg_pct FROM
    (SELECT year, ROUND((CAST(sum(shotResult::integer) AS FLOAT) / CAST(count(*) AS FLOAT))::numeric, 3) AS clutch_fg_pct
    FROM Shot NATURAL JOIN (
      SELECT * FROM Game
      WHERE ABS(homeScore - awayScore) <= 6
    ) g
    GROUP BY year) sq1
    
    NATURAL JOIN

    (SELECT year, ROUND((CAST(sum(shotResult::integer) AS FLOAT) / CAST(count(*) AS FLOAT))::numeric, 3) AS fg_pct
    FROM Shot NATURAL JOIN Game
    GROUP BY year) sq2;

-----------------------------------------------------------------------------------------------------
