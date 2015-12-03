-- Table definitions for the tournament project.


-- Create database
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;


-- Create players table
CREATE TABLE players (
	id serial PRIMARY KEY,
	name text
);


-- Create matches table.
-- Records the result of a match between 2 players.
-- A bye can be recorded for a player by inserting a row with columns player1 = player2 = winner = player
-- A draw can be recorded for a match by setting the column winner = null
CREATE TABLE matches (
	player1 integer REFERENCES players (id),
	player2 integer REFERENCES players (id),
	winner integer REFERENCES players (id),
	PRIMARY KEY (player1, player2)
);


-- Create player win count view.
CREATE VIEW player_wins AS
	SELECT players.id, players.name, COUNT(matches.winner) AS wins
	FROM players 
	LEFT OUTER JOIN matches ON players.id = matches.winner
	GROUP BY players.id;


-- Create player draw count view.
-- A draw is recorded in the matches tables by setting winner = null
CREATE VIEW player_draws AS
	SELECT players.id, players.name, COUNT(matches.player1) AS draws
	FROM players 
	LEFT OUTER JOIN matches 
	ON (players.id = matches.player1 OR players.id = matches.player2) AND matches.winner IS NULL
	GROUP BY players.id;


-- Create player match count view.
CREATE VIEW player_matches AS
	SELECT players.id, players.name, COUNT(matches.player1 + matches.player2) AS played
	FROM players 
	LEFT OUTER JOIN matches ON players.id = matches.player1 OR players.id = matches.player2
	GROUP BY players.id;


-- Create player bye count view.
-- A player bye is recorded in the matches table as player = player1 = player2 = winner.
CREATE VIEW player_byes AS
	SELECT players.id, players.name, COUNT(matches.player1) AS byes
	FROM players 
	LEFT OUTER JOIN matches ON players.id = matches.player1 AND players.id = matches.player2
	GROUP BY players.id;


-- Create player standings view.
CREATE VIEW standings AS
	SELECT players.id, players.name, 
	player_wins.wins, player_draws.draws, player_matches.played, player_byes.byes
	FROM players 
	JOIN player_wins ON players.id = player_wins.id
	JOIN player_draws ON players.id = player_draws.id
	JOIN player_matches ON players.id = player_matches.id
	JOIN player_byes ON players.id = player_byes.id;


-- Create possible pairings view.
-- Only return pairings that have not already played each other.
CREATE VIEW possible_pairings AS
	SELECT a.id AS id1, a.name AS name1, a.wins AS wins1,
	b.id AS id2, b.name AS name2, b.wins AS wins2 
	FROM standings a 
	CROSS JOIN standings b 
	WHERE a.id != b.id
	AND b.id NOT IN (SELECT matches.player2 FROM matches WHERE matches.player1 = a.id)
	AND b.id NOT IN (SELECT matches.player1 FROM matches WHERE matches.player2 = a.id);


