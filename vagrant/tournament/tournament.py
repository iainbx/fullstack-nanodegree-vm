#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")
 
 
def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(id) FROM players;")
    row = c.fetchone()
    conn.close()
    return row[0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO Players (name) VALUES (%s);", (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches, byes):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        byes: the number of byes the player was given
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, name, wins, played, byes FROM standings ORDER BY wins DESC;")
    standings = c.fetchall()
    conn.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO matches (player1,player2,winner) VALUES (%s,%s,%s);", (winner,loser,winner))
    conn.commit()
    conn.close()

 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # create list for pairings
    pairs = []
    
    # if uneven number of players, give lowest ranked player that has not had a bye, a bye
    if countPlayers() % 2 != 0:
        pair = getByePairing()
        if pair:
            pairs.append(pair)
        
    # get a list of possible pairings from the possible_pairings view, and sort by wins
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id1, name1, id2, name2 FROM possible_pairings	ORDER BY wins1 DESC, wins2 DESC;")
    possible_pairs = c.fetchall()
    conn.close()
   
    # add pairs to list, only adding each player once
    for (id1, name1, id2, name2) in possible_pairs:
        add_pair = True
        for pair in pairs:
            if id1 in (pair[0], pair[2]) or id2 in (pair[0], pair[2]):
                # one of the players in the pair is already paired with another player
                add_pair = False
                break
        if add_pair:
            pairs.append((id1, name1, id2, name2))
        
    return pairs


def getByePairing():
    """
    Select lowest ranking player, that has not had a bye, for a bye
    
    Returns:
    A tuple for a bye pairing (id1, name1, id2, name2)
    where id1 = id2 and name1 = name2
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, name FROM standings WHERE byes = 0 ORDER BY wins ASC LIMIT 1;")
    player = c.fetchone()
    conn.close()
    if len(player) == 2:
        return (player[0], player[1], player[0], player[1])
    else:
        return None


