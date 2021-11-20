DROP SCHEMA IF EXISTS PhaseTwo CASCADE;
CREATE SCHEMA PhaseTwo;
SET search_path TO PhaseTwo;

DROP TABLE IF exists Player CASCADE;
DROP TABLE IF exists Team CASCADE;
DROP TABLE IF exists Shot CASCADE;
DROP TABLE IF exists Game CASCADE;

CREATE TABLE Team (
    teamID INT NOT NULL PRIMARY KEY, 
    teamName TEXT NOT NULL
);

CREATE TABLE Game (
    gameID INT NOT NULL PRIMARY KEY,
    teamID INT NOT NULL, 
    oppTeamID INT NOT NULL, 
    homeScore INT NOT NULL, 
    awayScore INT NOT NULL,
    FOREIGN KEY (teamID) REFERENCES Team(teamID)
);

CREATE TABLE Player (
    playerID INT NOT NULL,
    playerName TEXT NOT NULL, 
    teamID INT NOT NULL, 
    year TEXT NOT NULL, 
    GP INT NOT NULL, 
    PTS FLOAT NOT NULL, 
    FGA INT NOT NULL, 
    FGM INT NOT NULL, 
    FGpercentage FLOAT NOT NULL, 
    eFGpercentage FLOAT NOT NULL, 
    ThreePTA INT NOT NULL, 
    ThreePTM INT NOT NULL, 
    ThreePTpercentage FLOAT NOT NULL, 
    FTA INT NOT NULL,
    FTM INT NOT NULL, 
    FTpercentage FLOAT NOT NULL, 
    AST FLOAT NOT NULL, 
    REB FLOAT NOT NULL, 
    STL FLOAT NOT NULL, 
    BLK FLOAT NOT NULL, 
    TOV FLOAT NOT NULL, 
    PF FLOAT NOT NULL,
    PRIMARY KEY (playerID, teamID, year),
    FOREIGN KEY (teamID) REFERENCES Team(teamID),
    UNIQUE(playerID, teamID, year)
);

CREATE TABLE Shot (
    shotID BIGINT NOT NULL, 
    playerID INT NOT NULL,
    shotDistance INT NOT NULL,
    gameID INT NOT NULL, 
    clutchTime BOOLEAN NOT NULL,
    shotResult BOOLEAN NOT NULL,
    PRIMARY KEY (shotID),
    FOREIGN KEY (gameID) REFERENCES Game(gameID)
);