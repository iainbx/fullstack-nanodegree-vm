#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#


import math
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


def countMatches():
    """Returns the number of matches played."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(player1) FROM matches;")
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
    """Returns a list of the players and their win records.

    The list is sorted by rank ascending and opponent match wins descending.
    Rank is calulated as player matches - wins - draws / 2.
    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains
        (id, name, wins, draws, played, byes, opponent_wins, rank):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        draws: the number of matches the player has drawn
        played: the number of matches the player has played
        byes: the number of byes the player was given
        opponent_wins: the number of matches the players opponents have won
        rank: the ranking of the player = played - wins - draws/2
    """
    conn = connect()
    c = conn.cursor()
    sql = """SELECT id, name, wins, draws, opponent_wins, played, byes, rank
                FROM standings ORDER BY rank, opponent_wins DESC;"""
    c.execute(sql)
    standings = c.fetchall()
    conn.close()
    return standings


def reportMatch(player1, player2, winner=None):
    """Records the outcome of a single match between two players.

    Args:
      player1:  the id number of the player 1
      player2:  the id number of the player 2
      winner:   the id number of the player who won, or None for a draw
    """
    conn = connect()
    c = conn.cursor()
    sql = "INSERT INTO matches (player1,player2,winner) VALUES (%s,%s,%s);"
    c.execute(sql, (player1, player2, winner))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Each player appears in only one pairing.
    Each player is paired with another player with an equal or nearly-equal
    win record, that is, a player adjacent to him or her in the standings.
    No player rematches are allowed.
    If there is an odd number of players, the lowest ranking player,
    that has not yet received a bye in a previous round, is given a bye.
    The bye player is added to the pairings list as a player who plays himself.
    If the lowest rank cannot be given a bye because it stops a complete set
    of pairings to be made, then the next lowest rank without a previous bye
    is attempted, and so on.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # Create list for pairings.
    pairs = []

    player_count = countPlayers()

    # If odd number of players, get a list of possible bye players,
    # from which to award a bye.
    if player_count % 2 != 0:
        possible_bye_players = possibleByePlayers()

    # Get a list of possible pairings from the possible_pairings view,
    # sorted by rank.
    possible_pairs = possiblePairings()

    # Need to loop because 1st pairing attempt may fail when byes are involved.
    # May need to try setting different players as the bye player to get a
    # complete set of pairings.
    while len(pairs) < int(math.ceil(float(player_count)/2)):
        # clear list of pairings
        del pairs[:]
 
        # add lowest ranked possible bye player, if we have an odd number of players
        if player_count % 2 != 0:
            if len(possible_bye_players) > 0:
                bye_player = possible_bye_players.pop()
                pairs.append((bye_player[0],bye_player[1],bye_player[0],bye_player[1]))
            else:
                raise ValueError("No players are eligible for a bye.")

        # add pairs to list, only adding each player once
        for (id1, name1, id2, name2) in possible_pairs:
            if any(id1 in (p[0], p[2]) or id2 in (p[0], p[2]) for p in pairs):
                continue
            pairs.append((id1, name1, id2, name2))
    
        if (len(pairs) < int(math.ceil(float(player_count)/2))
            and player_count % 2 == 0):
            raise ValueError("Pairing failed.")
           
    return pairs


def possibleByePlayers():
    """Get the list of players that have not had a bye.

    Returns:
      A list of tuples of players (id, name) ordered by rank.
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, name FROM standings WHERE byes = 0 ORDER BY rank;")
    possible_bye_players = c.fetchall()
    conn.close()
    return possible_bye_players


def possiblePairings():
    """Get the list of possible pairings for a round.

    Returns:
      A list of tuples of player pairings (id1, name1, id2, name2) ordered by rank.
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id1, name1, id2, name2 FROM possible_pairings	ORDER BY rank1, rank2;")
    possible_pairs = c.fetchall()
    conn.close()
    return possible_pairs
