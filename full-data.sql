\COPY Team from data/Team.csv with CSV HEADER;
\COPY Game from data/Game.csv with CSV HEADER;
\COPY Player from data/Player.csv with CSV HEADER;
\COPY Shot from data/Shot(0-500).csv with CSV HEADER;
\COPY Shot from data/Shot(500-1000).csv with CSV HEADER;
\COPY Shot from data/Shot(1000-1500).csv with CSV HEADER;
\COPY Shot from data/Shot(1500-2000).csv with CSV HEADER;
\COPY Shot from data/Shot(2000-2863).csv with CSV HEADER;

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
