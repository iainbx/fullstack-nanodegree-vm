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

-- Create matches table
CREATE TABLE matches (
	player1 integer REFERENCES players (id),
	player2 integer REFERENCES players (id),
	winner integer REFERENCES players (id),
	PRIMARY KEY (player1, player2)
);

-- Create player win count view
CREATE VIEW player_wins AS
	SELECT players.id, players.name, COUNT(matches.winner) AS wins
	FROM players 
	LEFT OUTER JOIN matches ON players.id = matches.winner
	GROUP BY players.id;
	
-- Create player match count view
CREATE VIEW player_matches AS
	SELECT players.id, players.name, COUNT(matches.player1 + matches.player2) AS played
	FROM players 
	LEFT OUTER JOIN matches ON players.id = matches.player1 OR players.id = matches.player2
	GROUP BY players.id;

-- Create player standings view
CREATE VIEW standings AS
	SELECT players.id, players.name, player_wins.wins, player_matches.played
	FROM players 
	JOIN player_wins ON players.id = player_wins.id
	JOIN player_matches ON players.id = player_matches.id;

-- Create possible pairings view
-- Only list pairings that have not already played each other
CREATE VIEW possible_pairings AS
	SELECT a.id AS id1, a.name AS name1, a.wins AS wins1,
	b.id AS id2, b.name AS name2, b.wins AS wins2 
	FROM standings a 
	CROSS JOIN standings b 
	WHERE a.id != b.id
	AND b.id NOT IN (SELECT matches.player2 FROM matches WHERE matches.player1 = a.id)
	AND b.id NOT IN (SELECT matches.player1 FROM matches WHERE matches.player2 = a.id);


