# Item Catalog Web Application
A Python module that uses a PostgreSQL database to manage a Swiss style tournament.<br/>
The module allows players to be registered, rounds of matches to be computed,
 match results to be recorded, and player standings to be viewed.

## Swiss Style
The Swiss system allows all players to play in each round of a tournament, whilst
keeping the number of rounds in the tournament small. 
It achieves this by pairing players with identical or similar tournament scores
 in each round, allowing a winner to be determined in fewer rounds.

The rules implemented in the pairing algorithm of this module are:
* Each player is paired with another player with the same score,
or as close as possible, in a round.
* Players can only play each other once in a tournament.
* All players play in each round, unless there is an odd number of players,
 in which case a player will receive a bye.
* A player can only have one bye in a tournament.
* A bye will be given to the lowest ranking player possible.
* A win scores one point and a draw scores half a point.
* In the case of a tied score at the end of a tournament, 
opponent match wins is tracked for each player, and can be
used to determine a winner.
* All decisions made by the algorithm are final.

## Prerequisites

The module requires **Python 2.7** and **SQLite** to to be already installed.<br/>
The module also depeneds on the **SQLAlchemy** Python module to access the database.
Flask microframework for Python.
Flask extensions:
Flask-SQLAlchemy
 -  pip install Flask-SQlAlchemy


## Installation
Clone this repository on the command line, to get the files.
```Shell
git clone https://github.com/iainbx/tournament-results.git
```

### Files
The repository contains the following files.
####tournament.sql
Contains the database schema used by the module.
####tournament.py
The Python module for managing a tournament.
####tournament_test.py
Unit tests and system tests for the tournament module.

###Database Setup
To create the tournament database in PostgreSQL, with it's tables and views,
run the following `psql` command on the command line.
```Shell
psql -f tournament.sql
```
## Usage

###Unit Tests
Once the database has been successfully created,
you can run the unit tests for the Python module with the following `python` command on the 
command line.
```Shell
python tournament_test.py
```

###System Tests
To perform a system test that will play a tournament with random match results,
 start the Python interpreter with the `python` command on the command line.
Then, enter the following commands in the interpreter to simulate a 3 player tournament.
```Python 
import tournament_test
tournament_test.simTournament(3)
``` 
Once the simulation has finished you can view the player standings in a readable format
by using the PostgreSQL interpreter. Start the interpreter in another 
command line window, or exit the Python interpreter using Ctrl-D. Then, type the `psql`
command on the command line. Next, enter the following commands in the interpreter 
to connect to the tournament database and query the standings view.
```PLpgSQL
\c tournament
select * from standings order by rank, opponent_wins desc;
```
The select query should return something like this,
with the highest ranking player listed first.
```
 id |   name    | wins | draws | opponent_wins | played | byes | rank
----+-----------+------+-------+---------------+--------+------+------
 81 | Player003 |    2 |     0 |             1 |      2 |    1 |    0
 79 | Player001 |    1 |     0 |             3 |      2 |    0 |    1
 80 | Player002 |    1 |     0 |             1 |      2 |    1 |    1
(3 rows)
```
To simulate a tournament with a random number of players and random match results, you can
call the _simTournament()_ function without any arguments. 
So, to simulate 3 random tournaments, you could do something like this in the Python
 interpreter.
```Python 
import tournament_test
for x in range(3):
    tournament_test.simTournament()

``` 
The _simTournament()_ function will produce output similar to this.
```
INFO:root:Simulating a tournament with 36 players...
INFO:root:Playing round 1
INFO:root:Playing round 2
INFO:root:Playing round 3
INFO:root:Playing round 4
INFO:root:Playing round 5
INFO:root:Playing round 6
INFO:root:After 6 rounds, Player030 wins tournament on omw's
INFO:root:Simulating a tournament with 63 players...
INFO:root:Playing round 1
INFO:root:Playing round 2
INFO:root:Playing round 3
INFO:root:Playing round 4
INFO:root:Playing round 5
INFO:root:Playing round 6
INFO:root:After 6 rounds, Player048 wins tournament on omw's
INFO:root:Simulating a tournament with 82 players...
INFO:root:Playing round 1
INFO:root:Playing round 2
INFO:root:Playing round 3
INFO:root:Playing round 4
INFO:root:Playing round 5
INFO:root:Playing round 6
INFO:root:Playing round 7
INFO:root:After 7 rounds, Player067 wins tournament
```
Note that the player and match data is removed from the database at the start of each
simulation, so the standings view will only show the results of the last tournament
simulated.

###Managing A Tournament
The tournament module contains the following functions for managing a tournament.

####registerPlayer(name)
Adds a player to the tournament by putting an entry in the players table.
An ID number is assigned to the player.
Different players may have the same names but will receive different ID numbers.

####countPlayers()
Returns the number of currently registered players.

####deletePlayers()
Clear out all the player records from the database.

####reportMatch(id1, id2, winner)
Stores the outcome of a single match between two players in the database.
Leave the winner argument blank to record a draw.
To record a bye for a player, set id1, id2 and winner to the ID of the player.

####deleteMatches()
Clear out all the match records from the database.

####playerStandings()
Returns a list of (id, name, wins, draws, played, byes, opponent_wins, rank)
for each player, sorted by rank ascending and opponent match wins descending.

####swissPairings()
Given the existing set of registered players and the matches they have played,
generates and returns a list of pairings according to the Swiss system. 
Each pairing is a tuple (id1, name1, id2, name2), giving the ID and name of 
the paired players. 

A typical use of the module, to manage a tournament, would look like the following
 on the command line.
```Shell
vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ python
Python 2.7.6 (default, Jun 22 2015, 18:00:18)
[GCC 4.8.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import tournament
>>> # delete data for previous tournament
... tournament.deleteMatches()
>>> tournament.deletePlayers()
>>> # register players
... tournament.registerPlayer("Kirk")
>>> tournament.registerPlayer("Spock")
>>> tournament.registerPlayer("McCoy")
>>> tournament.registerPlayer("Scotty")
>>> # get pairings for a round
... tournament.swissPairings()
[(263, 'Kirk', 264, 'Spock'), (265, 'McCoy', 266, 'Scotty')]
>>> # record that Kirk and Spock drew their match
... tournament.reportMatch(263,264,None)
>>> # record that McCoy beat Scotty
... tournament.reportMatch(265,266,265)
>>> # get pairings for next round
... tournament.swissPairings()
[(265, 'McCoy', 264, 'Spock'), (263, 'Kirk', 266, 'Scotty')]
>>> # record that Spock beat McCoy
... tournament.reportMatch(265,264,264)
>>> # record that Kirk and Scotty drew
... tournament.reportMatch(263,266,None)
>>> # see who won
... tournament.playerStandings()
[(264, 'Spock', 1L, 1L, Decimal('1'), 2L, 0L, 0.5), (263, 'Kirk', 0L, 2L, Decimal('1'), 2L, 0L, 1.0), (265, 'McCoy', 1L, 0L, Decimal('1'), 2L, 0L, 1.0), (266, 'Scotty', 0L, 1L, Decimal('1'), 2L, 0L, 1.5)]
>>> # Spock wins of course
```
