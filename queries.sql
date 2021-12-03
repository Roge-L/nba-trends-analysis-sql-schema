-- get number of 3s attempted per season
-- SELECT count(*) 
-- FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player)
-- WHERE shotDistance >= 24
-- GROUP BY year;
--   year   | count
-- ---------+--------
--  2011-12 | 243970
--  2012-13 | 285057
--  2013-14 | 314183
--  2014-15 | 343314
--  2015-16 | 358630
--  2016-17 | 372894
--  2017-18 | 374841
--  2018-19 | 373824
--  2019-20 | 347252
--  2020-21 | 322142

-- 3pts made by season
-- SELECT count(*) 
-- FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player)
-- WHERE shotDistance >= 24 AND shotResult=TRUE
-- GROUP BY year;
--   year   | count
-- ---------+--------
--  2011-12 |  86296
--  2012-13 | 100702
--  2013-14 | 110944
--  2014-15 | 121191
--  2015-16 | 126558
--  2016-17 | 131819
--  2017-18 | 132243
--  2018-19 | 132268
--  2019-20 | 122745
--  2020-21 | 113895

-- 2pts attempted by season
-- SELECT count(*) 
-- FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player)
-- WHERE shotDistance < 24
-- GROUP BY year;
--   year   |  count
-- ---------+---------
--  2011-12 |  857233
--  2012-13 |  977055
--  2013-14 | 1055952
--  2014-15 | 1139168
--  2015-16 | 1179269
--  2016-17 | 1180258
--  2017-18 | 1159613
--  2018-19 | 1116006
--  2019-20 |  992986
--  2020-21 |  934237

-- 2pts made by season
-- SELECT count(*) 
-- FROM Shot NATURAL JOIN (SELECT playerID, year FROM Player)
-- WHERE shotDistance < 24 AND shotResult=TRUE
-- GROUP BY year;
--   year   | count
-- ---------+--------
--  2011-12 | 417068
--  2012-13 | 475560
--  2013-14 | 516345
--  2014-15 | 558291
--  2015-16 | 580702
--  2016-17 | 582578
--  2017-18 | 574662
--  2018-19 | 554844
--  2019-20 | 494492
--  2020-21 | 467405

-- fouls per Game
-- SELECT year, ROUND(avg(PF)::numeric, 1) as avg_pf
-- FROM Player
-- GROUP BY year
-- ORDER BY year DESC;

-- fta per game
-- SELECT year, sum(FTA) FROM Player
-- GROUP BY year
-- ORDER BY year ASC;
--   year   |  sum
-- ---------+-------
--  2011-12 | 44472
--  2012-13 | 54533
--  2013-14 | 58029
--  2014-15 | 56198
--  2015-16 | 57469
--  2016-17 | 56855
--  2017-18 | 53325
--  2018-19 | 56758
--  2019-20 | 48943
--  2020-21 | 47135

-- SELECT year, sum(PF * GP) FROM Player GROUP BY year ORDER BY year ASC;
--   year   |  sum
-- ---------+-------
--  2011-12 | 38742
--  2012-13 | 48686
--  2013-14 | 50892
--  2014-15 | 49791
--  2015-16 | 49785
--  2016-17 | 48979
--  2017-18 | 48804
--  2018-19 | 51377
--  2019-20 | 43986
--  2020-21 | 41661

-- top 5 scorers per season, ppg, 3pt%
-- SELECT playerName, year, PTS, ThreePTA, FGA, ROUND(percent_threes::numeric, 3)
-- FROM (
--   SELECT 
--     playerName, 
--     year, 
--     PTS, 
--     ThreePTA,
--     FGA,
--     CASE
--       WHEN FGA = 0 THEN 0
--       ELSE CAST(ThreePTA AS FLOAT) / CAST(FGA AS FLOAT)
--     END as percent_threes,
--   ROW_NUMBER() OVER (PARTITION BY year ORDER BY PTS DESC)
--   AS rn
--   FROM Player
-- ) tmp 
-- WHERE rn <= 3
-- ORDER BY year, PTS DESC;

-- get freq of shots by range, 2020-2021 season
-- SELECT 2 * s.d AS distance_ft, count(t.shotDistance)
-- FROM 
--   generate_series(0, 20) s(d) LEFT OUTER JOIN (
--     SELECT * FROM 
--     (SELECT playerID, year FROM Player) p NATURAL JOIN Shot
--     WHERE year='2020-21'
--   ) t ON s.d = floor(t.shotDistance / 2)
-- GROUP BY s.d
-- ORDER BY s.d;

-- get freq of shots by range, 2011-2012 season
-- SELECT 2 * s.d AS distance_ft, count(t.shotDistance)
-- FROM 
--   generate_series(0, 20) s(d) LEFT OUTER JOIN (
--     SELECT * FROM 
--     (SELECT playerID, year FROM Player) p NATURAL JOIN Shot
--     WHERE year='2011-12'
--   ) t ON s.d = floor(t.shotDistance / 2)
-- GROUP BY s.d
-- ORDER BY s.d;

-- get min, avg, max scores for games in each season
-- SELECT year, min(homeScore), ROUND(avg(homeScore)::numeric, 1), max(homeScore)
-- FROM Game
-- GROUP BY year
-- ORDER BY year DESC;

-- sum of all stats by year
-- SELECT 
--   year, 
--   ROUND(avg(PTS)::numeric, 1) AS PTS,
--   ROUND(avg(ThreePTM / GP)::numeric, 1) AS ThreePTM,
--   ROUND(avg(FTM / GP)::numeric, 1) AS FTM,
--   ROUND(avg(AST)::numeric, 1) AS AST,
--   ROUND(avg(REB)::numeric, 1) AS REB,
--   ROUND(avg(STL)::numeric, 1) AS STL,
--   ROUND(avg(BLK)::numeric, 1) AS BLK,
--   ROUND(avg(TOV)::numeric, 1) AS TOV
-- FROM Player
-- GROUP BY year
-- ORDER BY year DESC;

-- percentages of clutch shots in tight games compared to average
-- SELECT year, fg_pct, clutch_fg_pct FROM
--   (SELECT year, ROUND((CAST(sum(shotResult::integer) AS FLOAT) / CAST(count(*) AS FLOAT))::numeric, 3) AS clutch_fg_pct
--   FROM Shot NATURAL JOIN (
--     SELECT * FROM Game
--     WHERE ABS(homeScore - awayScore) <= 6
--   ) g
--   GROUP BY year) sq1
  
--   NATURAL JOIN

--   (SELECT year, ROUND((CAST(sum(shotResult::integer) AS FLOAT) / CAST(count(*) AS FLOAT))::numeric, 3) AS fg_pct
--   FROM Shot NATURAL JOIN Game
--   GROUP BY year) sq2;

-- winning and losing teams 3pt%