#!/usr/bin/env python
#
# Test cases for tournament.py

import math
from random import randint
from tournament import *

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 8:
        raise ValueError("Each playerStandings row should have 8 columns.")
    [(id1, name1, wins1, draws, opponent_wins, matches1, byes1, rank), (id2, name2, wins2, draws2, opponent_wins2, matches2, byes2, rank2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, id1)
    reportMatch(id3, id4, id3)
    standings = playerStandings()
    for (i, n, w, d, o, m, b, r) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, id1)
    reportMatch(id3, id4, id3)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testByes():
    deleteMatches()
    deletePlayers()
    registerPlayer("Kirk")
    registerPlayer("Spock")
    registerPlayer("McCoy")
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For 3 players, swissPairings should return 2 pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    if pid1 != pid2 and pid3 != pid4:
         raise ValueError(
            "No bye was assigned by swissPairings in 3 player tournament.")
    print "9. Bye was assigined in 3 player tournament."


def testDraws():
    deleteMatches()
    deletePlayers()
    registerPlayer("Kirk")
    registerPlayer("Spock")
    registerPlayer("McCoy")
    registerPlayer("Scotty")
    pairings = swissPairings()
    for (id1, name1, id2, name2) in pairings:
        reportMatch(id1, id2)
    standings = playerStandings()
    for (id, name, wins, draws, opponent_wins, matches, byes, rank) in standings:
        if draws != 1:
            raise ValueError("Each player should have 1 draw recorded.")
    print "10. After reporting drawn matches, player standings shows draws."


def testOpponentWins():
    deleteMatches()
    deletePlayers()
    registerPlayer("Kirk")
    registerPlayer("Spock")
    registerPlayer("McCoy")
    registerPlayer("Scotty")
    pairings = swissPairings()
    for (id1, name1, id2, name2) in pairings:
        reportMatch(id1, id2, id1)
    standings = playerStandings()
    for (id, name, wins, draws, opponent_wins, matches, byes, rank) in standings:
        if wins + opponent_wins != 1:
            raise ValueError("After 1 match a player should have a win or an opponent win.")
    print "11. After 1 match, the player standings shows that each player has a win or an opponent win."


def test4PlayerTournament():
    testTournament(4)
    print "12. After a 4 player simulated tournament, player wins and matches are correct."


def test5PlayerTournament():
    testTournament(5)
    print "13. After a 5 player simulated tournament, player wins and matches are correct."


def testTournament(player_count):

    if player_count < 2 or player_count > 999:
        raise ValueError("Player count should be between 2 and 999")
        
    deleteMatches()
    deletePlayers()
   
    # Create a list of player names whose length equals player_count
    players = ["Player{0:03d}".format(x) for x in range(1,player_count+1)]
    
    # Simulate playing a tournament
    rounds_played = simTournament(players) 
    standings = playerStandings()
    
    for i, (id, name, wins, draws, opponent_wins, matches, byes, rank) in enumerate(standings):
        if matches != rounds_played:
            raise ValueError("Each player should have %s matches recorded." % rounds_played)
        if byes > 1:
            raise ValueError("A player should not have more than 1 bye.")
        if wins + draws > rounds_played:
            raise ValueError("Each player cannot have more wins + draws than rounds played.")
        if i == 0 and wins + draws == 0:
            raise ValueError("Top ranked player should at least have 1 win or draw.")
        elif i > 0 and wins == rounds_played:
            raise ValueError("Lower rankings should have less than %s wins." % rounds_played)
        elif i > 0 and i < len(players) -1 and wins + draws == 0:
            raise ValueError("Middle rankings should have more than 0 wins + draws.")
    
    matches_played = int(math.ceil(float(len(players))/2)) * rounds_played
    if countMatches() != matches_played:
        raise ValueError("The number of matches played in the tournament should be %s." % matches_played)


def simTournament(players):
    """Simulate playing a complete tournament of log2(player count) rounds."""
    for player in players:
        registerPlayer(player)
    
    # play log2(player count) rounds   
    rounds = int(math.ceil(math.log(len(players),2)))
    
    for x in range(rounds):
        simRound()
    
    return rounds
   
def simRound():
    """Simulate playing a single round of a tournament, with random match results."""
    pairings = swissPairings()
    for (id1, name1, id2, name2) in pairings:
        if id1 == id2:
            # bye, so just report it
            reportMatch(id1, id2, id1)
        else:
            # randomly select winner or draw
            x = randint(0,9)
            if x < 4:
                # id1 wins
                reportMatch(id1, id2, id1)
            elif x > 4:
                # id2 wins
                reportMatch(id1, id2, id2)
            else:
                # draw
                reportMatch(id1, id2)


def imFeelingLucky():
    """Simulate playing a tournament with a random number of players
        between 2 and 100.
    """
    x = randint(2,99)
    print("Simulating a random tournament with %s players..." % x)
    testTournament(x)
    standings = playerStandings()
    if standings[0][2] > standings[1][2]:
        print("After %s matches, %s wins" % (standings[0][5], standings[0][1]))


def justKeepTesting():
    while True:
        imFeelingLucky()


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testByes()
    testDraws()
    testOpponentWins()
    test3PlayerTournament()
    test4PlayerTournament()
    test5PlayerTournament()
    print "Success!  All tests pass!"


