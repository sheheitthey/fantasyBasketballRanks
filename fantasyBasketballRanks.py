#!/usr/bin/python

from recipe500261 import namedtuple
import csv
from stats import *
from math import *
import re

PlayerRecord = namedtuple('PlayerRecord',
                          'firstName, lastName, season, games, gamesStarted,\
                           minutes, fgMade, fgAtt, fgPct, pt3Made, pt3Att,\
                           pt3Pct, ftMade, ftAtt, ftPct, steals, turnovers,\
                           offRebounds, defRebounds, totRebounds, assists,\
                           blocks, fouls, flagFouls, techFouls, ejected,\
                           points')

# Just the stuff potentially relevant in fantasy, and without redundancy.
FantasyPlayer = namedtuple('FantasyPlayer',
                           'name, gamesPlayed, gamesStarted, minutes, fgMade,\
                            fgAtt, pt3Made, pt3Att, ftMade, ftAtt, steals,\
                            turnovers, offRebounds, defRebounds, assists,\
                            blocks, points')

def nameFormat(name):
    fullLen = 30
    diff = fullLen - len(name)
    ret = name

    for i in range(0, diff):
        ret += " "

    return ret

def readFantasyPlayer(playerRecord):
    return FantasyPlayer(\
        nameFormat(playerRecord.firstName + " " + playerRecord.lastName),\
        int(playerRecord.games),\
        int(playerRecord.gamesStarted),\
        int(playerRecord.minutes),\
        int(playerRecord.fgMade),\
        int(playerRecord.fgAtt),\
        int(playerRecord.pt3Made),\
        int(playerRecord.pt3Att),\
        int(playerRecord.ftMade),\
        int(playerRecord.ftAtt),\
        int(playerRecord.steals),\
        int(playerRecord.turnovers),\
        int(playerRecord.offRebounds),\
        int(playerRecord.defRebounds),\
        int(playerRecord.assists),\
        int(playerRecord.blocks),\
        int(playerRecord.points)
    )

def floatFormat(num):
    numTimes100 = int(num * 100.0)
    ret = str(float(numTimes100) / 100.0)

    if numTimes100 >= 0:
        ret = " " + ret

    if numTimes100 % 10 == 0:
        ret += "0"
        #if numTimes100 % 100 == 0:
            #ret += "0"

    return ret

def addPlayerStats(allStats, player):
    [allFgPct, allFtPct, allThrees, allPoints, allRebounds, allAssists, \
     allSteals, allBlocks, allTurnovers, allFgAtt, allFtAtt] = allStats

    fgPct = 0.0
    ftPct = 0.0
    threes = 0.0
    points = 0.0
    rebounds = 0.0
    assists = 0.0
    steals = 0.0
    blocks = 0.0
    turnovers = 0.0

    if player.gamesPlayed > 0:
        if player.fgAtt > 0:
            fgPct = float(player.fgMade) / float(player.fgAtt)
        if player.ftAtt > 0:
            ftPct = float(player.ftMade) / float(player.ftAtt)
        threes = float(player.pt3Made) / float(player.gamesPlayed)
        points = float(player.points) / float(player.gamesPlayed)
        rebounds = float(player.offRebounds + player.defRebounds) / \
                   float(player.gamesPlayed)
        assists = float(player.assists) / float(player.gamesPlayed)
        steals = float(player.steals) / float(player.gamesPlayed)
        blocks = float(player.blocks) / float(player.gamesPlayed)
        turnovers = float(player.turnovers) / float(player.gamesPlayed)

    # Only qualify stuff if there are enough attempts...probably not necessary
    if player.gamesPlayed > 50:
        if player.fgAtt > 10:
            allFgPct.append(fgPct)
            allFgAtt.append(player.fgAtt)
        if player.ftAtt > 10:
            allFtPct.append(ftPct)
            allFtAtt.append(player.ftAtt)
        if threes > 0:
            allThrees.append(threes)
        if points > 0:
            allPoints.append(points)
        if rebounds > 0:
            allRebounds.append(rebounds)
        if assists > 0:
            allAssists.append(assists)
        if steals > 0:
            allSteals.append(steals)
        if blocks > 0:
            allBlocks.append(blocks)
        if turnovers > 0:
            allTurnovers.append(turnovers)

def readAllPlayersAndStats(fileName):
    csvReader = csv.reader(open(fileName, "rb"))

    allFgPct = []
    allFtPct = []
    allThrees = []
    allPoints = []
    allRebounds = []
    allAssists = []
    allSteals = []
    allBlocks = []
    allTurnovers = []
    allFgAtt = []
    allFtAtt = []

    allPlayers = []
    allStats = [allFgPct, allFtPct, allThrees, allPoints, allRebounds, \
                allAssists, allSteals, allBlocks, allTurnovers, allFgAtt, \
                allFtAtt]

    playerNum = 0
    for playerRow in csvReader:
        if playerNum > 0:
            player = readFantasyPlayer(PlayerRecord._make(playerRow))
            allPlayers.append(player)
            addPlayerStats(allStats, player)
        playerNum += 1

    # Factor of 1.55 picked so that the top half of players picked for 12 teams
    # of 13 players each should have positive overall scores.
    numPlayersPicked = int(1.55*12*13)
    allFgPct = sorted(allFgPct)[-numPlayersPicked:]
    allFtPct = sorted(allFtPct)[-numPlayersPicked:]
    allThrees = sorted(allThrees)[-numPlayersPicked:]
    allPoints = sorted(allPoints)[-numPlayersPicked:]
    allRebounds = sorted(allRebounds)[-numPlayersPicked:]
    allAssists = sorted(allAssists)[-numPlayersPicked:]
    allSteals = sorted(allSteals)[-numPlayersPicked:]
    allBlocks = sorted(allBlocks)[-numPlayersPicked:]
    allTurnovers = sorted(allTurnovers)[:numPlayersPicked]
    #allFgAtt = sorted(allFgAtt)[-numPlayersPicked:]
    #allFtAtt = sorted(allFtAtt)[-numPlayersPicked:]

    allStats = [allFgPct, allFtPct, allThrees, allPoints, allRebounds, \
                allAssists, allSteals, allBlocks, allTurnovers, allFgAtt, \
                allFtAtt]

    return [allPlayers, allStats]

def replacePlayer(allPlayers, name, player):
    for i in range(0, len(allPlayers)):
        pattern = '.*' + name + '.*'
        if re.match(pattern, allPlayers[i].name, re.IGNORECASE):
            allPlayers[i] = player
            break

def scalePlayerByMinutes(player, minutesPerGame):
    minutes = minutesPerGame * player.gamesPlayed
    factor = float(minutes) / float(player.minutes)
    fgMade = int(factor * player.fgMade)
    fgAtt = int(factor * player.fgAtt)
    pt3Made = int(factor * player.pt3Made)
    pt3Att = int(factor * player.pt3Att)
    ftMade = int(factor * player.ftMade)
    ftAtt = int(factor * player.ftAtt)
    steals = int(factor * player.steals)
    turnovers = int(factor * player.turnovers)
    offRebounds = int(factor * player.offRebounds)
    defRebounds = int(factor * player.defRebounds)
    assists = int(factor * player.assists)
    blocks = int(factor * player.blocks)
    points = int(factor * player.points)

    return FantasyPlayer(player.name, player.gamesPlayed, player.gamesStarted,\
                         minutes, fgMade, fgAtt, pt3Made, pt3Att, ftMade,\
                         ftAtt, steals, turnovers, offRebounds, defRebounds,\
                         assists, blocks, points)

def replaceScaledPlayerByMinutes(allPlayers, name, minutesPerGame):
    player = getPlayerByName(allPlayers, name)
    newPlayer = scalePlayerByMinutes(player, minutesPerGame)
    replacePlayer(allPlayers, name, newPlayer)

def makePlayerFromAverages(name, minutesPerGame, fgMadePerGame, fgAttPerGame,\
                           pt3MadePerGame, pt3AttPerGame, ftMadePerGame,\
                           ftAttPerGame, offReboundsPerGame,\
                           defReboundsPerGame, assistsPerGame,\
                           turnoversPerGame, stealsPerGame, blocksPerGame,\
                           pointsPerGame):
    gamesPlayed = 82
    gamesStarted = 82
    minutes = int(gamesPlayed * minutesPerGame)
    fgMade = int(gamesPlayed * fgMadePerGame)
    fgAtt = int(gamesPlayed * fgAttPerGame)
    pt3Made = int(gamesPlayed * pt3MadePerGame)
    pt3Att = int(gamesPlayed * pt3AttPerGame)
    ftMade = int(gamesPlayed * ftMadePerGame)
    ftAtt = int(gamesPlayed * ftAttPerGame)
    steals = int(gamesPlayed * stealsPerGame)
    turnovers = int(gamesPlayed * turnoversPerGame)
    offRebounds = int(gamesPlayed * offReboundsPerGame)
    defRebounds = int(gamesPlayed * defReboundsPerGame)
    assists = int(gamesPlayed * assistsPerGame)
    blocks = int(gamesPlayed * blocksPerGame)
    points = int(gamesPlayed * pointsPerGame)

    return FantasyPlayer(name, gamesPlayed, gamesStarted,\
                         minutes, fgMade, fgAtt, pt3Made, pt3Att, ftMade,\
                         ftAtt, steals, turnovers, offRebounds, defRebounds,\
                         assists, blocks, points)

def printAverageStats(allStats, scoreFreqs, scoreThreshold):
    [allFgPct, allFtPct, allThrees, allPoints, allRebounds, allAssists,\
     allSteals, allBlocks, allTurnovers, allFgAtt, allFtAtt] = allStats
    [fgFreq, ftFreq, threesFreq, pointsFreq, reboundsFreq, assistsFreq,\
     stealsFreq, blocksFreq, turnoversFreq] = scoreFreqs

    print "FG%\t" + str(mean(allFgPct)) + " +/- " +\
            str(standardDeviation(allFgPct))
    print "FT%\t" + str(mean(allFtPct)) + " +/- " +\
            str(standardDeviation(allFtPct))
    print "3PTM\t" + str(mean(allThrees)) + " +/- " +\
            str(standardDeviation(allThrees))
    print "PPG\t" + str(mean(allPoints)) + " +/- " +\
            str(standardDeviation(allPoints))
    print "REB\t" + str(mean(allRebounds)) + " +/- " +\
            str(standardDeviation(allRebounds))
    print "AST\t" + str(mean(allAssists)) + " +/- " +\
            str(standardDeviation(allAssists))
    print "STL\t" + str(mean(allSteals)) + " +/- " +\
            str(standardDeviation(allSteals))
    print "BLK\t" + str(mean(allBlocks)) + " +/- " +\
            str(standardDeviation(allBlocks))
    print "TO\t" + str(mean(allTurnovers)) + " +/- " +\
            str(standardDeviation(allTurnovers))

    fgPct = mean(allFgPct) + scoreThreshold * standardDeviation(allFgPct)
    ftPct = mean(allFtPct) + scoreThreshold * standardDeviation(allFtPct)
    threes = mean(allThrees) + scoreThreshold * standardDeviation(allThrees)
    points = mean(allPoints) + scoreThreshold * standardDeviation(allPoints)
    rebounds = mean(allRebounds) +\
               scoreThreshold * standardDeviation(allRebounds)
    assists = mean(allAssists) + scoreThreshold * standardDeviation(allAssists)
    steals = mean(allSteals) + scoreThreshold * standardDeviation(allSteals)
    blocks = mean(allBlocks) + scoreThreshold * standardDeviation(allBlocks)
    turnovers = mean(allTurnovers) -\
                scoreThreshold * standardDeviation(allTurnovers)

    print ""
    # Don't display the percentages frquencies because their scores aren't quite
    # their standard deviations, so fgPct and ftPct are computed wrong
    #print "FG%\t" + str(fgPct) + " achieved by " + str(fgFreq)
    #print "FT%\t" + str(ftPct) + " achieved by " + str(ftFreq)
    print "3PTM\t" + str(threes) + " achieved by " + str(threesFreq)
    print "PTS\t" + str(points) + " achieved by " + str(pointsFreq)
    print "REB\t" + str(rebounds) + " achieved by " + str(reboundsFreq)
    print "AST\t" + str(assists) + " achieved by " + str(assistsFreq)
    print "STL\t" + str(steals) + " achieved by " + str(stealsFreq)
    print "BLK\t" + str(blocks) + " achieved by " + str(blocksFreq)
    print "TO\t" + str(turnovers) + " achieved by " + str(turnoversFreq)

def getPlayerScores(player, allStats):
    [allFgPct, allFtPct, allThrees, allPoints, allRebounds, allAssists,\
     allSteals, allBlocks, allTurnovers, allFgAtt, allFtAtt] = allStats

    fgPct = 0.0
    ftPct = 0.0
    threes = 0.0
    points = 0.0
    rebounds = 0.0
    assists = 0.0
    steals = 0.0
    blocks = 0.0
    turnovers = 0.0

    fgPctMean = mean(allFgPct)
    fgPctDev = standardDeviation(allFgPct)
    ftPctMean = mean(allFtPct)
    ftPctDev = standardDeviation(allFtPct)
    threesMean = mean(allThrees)
    threesDev = standardDeviation(allThrees)
    pointsMean = mean(allPoints)
    pointsDev = standardDeviation(allPoints)
    reboundsMean = mean(allRebounds)
    reboundsDev = standardDeviation(allRebounds)
    assistsMean = mean(allAssists)
    assistsDev = standardDeviation(allAssists)
    stealsMean = mean(allSteals)
    stealsDev = standardDeviation(allSteals)
    blocksMean = mean(allBlocks)
    blocksDev = standardDeviation(allBlocks)
    turnoversMean = mean(allTurnovers)
    turnoversDev = standardDeviation(allTurnovers)

    if player.gamesPlayed > 0:
        if player.fgAtt > 0:
            fgPct = float(player.fgMade) / float(player.fgAtt)
        if player.ftAtt > 0:
            ftPct = float(player.ftMade) / float(player.ftAtt)
        threes = float(player.pt3Made) / float(player.gamesPlayed)
        points = float(player.points) / float(player.gamesPlayed)
        rebounds = float(player.offRebounds + player.defRebounds) / \
                   float(player.gamesPlayed)
        assists = float(player.assists) / float(player.gamesPlayed)
        steals = float(player.steals) / float(player.gamesPlayed)
        blocks = float(player.blocks) / float(player.gamesPlayed)
        turnovers = float(player.turnovers) / float(player.gamesPlayed)

    fgScore = (fgPct - fgPctMean) / fgPctDev
    ftScore = (ftPct - ftPctMean) / ftPctDev
    threesScore = (threes - threesMean) / threesDev
    pointsScore = (points - pointsMean) / pointsDev
    reboundsScore = (rebounds - reboundsMean) / reboundsDev
    assistsScore = (assists - assistsMean) / assistsDev
    stealsScore = (steals - stealsMean) / stealsDev
    blocksScore = (blocks - blocksMean) / blocksDev
    turnoversScore = ((-turnovers) - (-turnoversMean)) / turnoversDev

    # Goal for these weights is to curve-fit so that mean attempts gets a weight
    # of 0.5, 0 attempts gets a weight of 0.0, and max attemtpts gets a weight
    # of 1.0
    def computeAttemptsWeight(att, allAtt):
        meanAtt = mean(allAtt)
        weight = 0.0

        # Just do it with 2 line segments
        if att < meanAtt:
            weight = 0.5 * (att / meanAtt)
        else:
            weight = 0.5 + 0.5 * (att - meanAtt) / (max(allAtt) - meanAtt)

        return weight

    fgWeight = computeAttemptsWeight(player.fgAtt, allFgAtt)
    ftWeight = computeAttemptsWeight(player.ftAtt, allFtAtt) 
    fgScore *= fgWeight
    ftScore *= ftWeight

    score = fgScore + ftScore + threesScore +\
            pointsScore + reboundsScore + assistsScore +\
            stealsScore + blocksScore + turnoversScore

    # Just punt turnovers
    score -= turnoversScore

    # Drop lowest subscore
    #score -= min([fgScore, ftScore, threesScore, pointsScore, reboundsScore,\
    #              assistsScore, stealsScore, blocksScore, turnoversScore])

    return [score,\
            fgScore, ftScore, threesScore,\
            pointsScore, reboundsScore, assistsScore,\
            stealsScore, blocksScore, turnoversScore]

def getPlayerByName(players, name):
    pattern = '.*' + name + '.*'

    for player in players:
        if re.match(pattern, player.name, re.IGNORECASE):
            return player

    return None

def allPlayerScoresSortKey(playerScores):
    [player, scores] = playerScores
    [score, fgScore, ftScore, threesScore, pointsScore, reboundsScore,\
     assistsScore, stealsScore, blocksScore, turnoversScore] = scores

    return -score

def getAllPlayerScores(allPlayers, allStats):
    allPlayerScores = []

    for player in allPlayers:
        playerScores = getPlayerScores(player, allStats)
        allPlayerScores.append([player, playerScores])

    allPlayerScores = sorted(allPlayerScores, key = allPlayerScoresSortKey)

    return allPlayerScores

def printPlayerScores(playerScores, prefix):
    [player, scores] = playerScores
    [score, fgScore, ftScore, threesScore, pointsScore, reboundsScore,\
     assistsScore, stealsScore, blocksScore, turnoversScore] = scores

    print prefix + " " + player.name + "\t" + floatFormat(score) + "\t" +\
        floatFormat(fgScore) + "\t" + floatFormat(ftScore) + "\t" +\
        floatFormat(threesScore) + "\t" + floatFormat(pointsScore) + "\t" +\
        floatFormat(reboundsScore) + "\t" + floatFormat(assistsScore) + "\t" +\
        floatFormat(stealsScore) + "\t" + floatFormat(blocksScore) + "\t" +\
        floatFormat(turnoversScore)

def printPlayerScoresHeader(prefix):
    print prefix + " " + nameFormat("") +\
        "\tScore\t FG%\t FT%\t 3PTM\t PTS\t REB\t AST\t STL\t BLK\t TO"

def printAllPlayerScores(allPlayerScores):
    rank = 0

    #print "    " + nameFormat("") +\
    #    "\tScore\t FG%\t FT%\t 3PTM\t PTS\t REB\t AST\t STL\t BLK\t TO"
    printPlayerScoresHeader("   ")

    for playerScores in allPlayerScores:
        [player, scores] = playerScores
        rank += 1
        if player.gamesPlayed >= 40:
            printPlayerScores(playerScores, str(rank))

def getScoreFrequencies(allPlayerScores, threshold):
    [fgFreq, ftFreq, threesFreq, pointsFreq, reboundsFreq, assistsFreq,\
     stealsFreq, blocksFreq, turnoversFreq] = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for playerScores in allPlayerScores:
        [player, scores] = playerScores
        [score, fgScore, ftScore, threesScore, pointsScore, reboundsScore,\
         assistsScore, stealsScore, blocksScore, turnoversScore] = scores

        if fgScore >= threshold:
            fgFreq += 1
        if ftScore >= threshold:
            ftFreq += 1
        if threesScore >= threshold:
            threesFreq += 1
        if pointsScore >= threshold:
            pointsFreq += 1
        if reboundsScore >= threshold:
            reboundsFreq += 1
        if assistsScore >= threshold:
            assistsFreq += 1
        if stealsScore >= threshold:
            stealsFreq += 1
        if blocksScore >= threshold:
            blocksFreq += 1
        if turnoversScore >= threshold:
            turnoversFreq += 1

    scoreFreqs = [fgFreq, ftFreq, threesFreq, pointsFreq, reboundsFreq,\
                  assistsFreq, stealsFreq, blocksFreq, turnoversFreq]
    return scoreFreqs

def printScoreFrequencies(scoreFreqs):
    [fgFreq, ftFreq, threesFreq, pointsFreq, reboundsFreq, assistsFreq,\
     stealsFreq, blocksFreq, turnoversFreq] = scoreFreqs

    print("FG% frequency: " + str(fgFreq))
    print("FT% frequency: " + str(ftFreq))
    print("Threes frequency: " + str(threesFreq))
    print("Points frequency: " + str(pointsFreq))
    print("Rebounds frequency: " + str(reboundsFreq))
    print("Assists frequency: " + str(assistsFreq))
    print("Steals frequency: " + str(stealsFreq))
    print("Blocks frequency: " + str(blocksFreq))
    print("Turnovers frequency: " + str(turnoversFreq))


def addScores(scores1, scores2):
    [score1, fgScore1, ftScore1, threesScore1, pointsScore1, reboundsScore1,\
     assistsScore1, stealsScore1, blocksScore1, turnoversScore1] = scores1
    [score2, fgScore2, ftScore2, threesScore2, pointsScore2, reboundsScore2,\
     assistsScore2, stealsScore2, blocksScore2, turnoversScore2] = scores2
    [score, fgScore, ftScore, threesScore, pointsScore, reboundsScore,\
     assistsScore, stealsScore, blocksScore, turnoversScore] =\
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    score = score1 + score2
    fgScore = fgScore1 + fgScore2
    ftScore = ftScore1 + ftScore2
    threesScore = threesScore1 + threesScore2
    pointsScore = pointsScore1 + pointsScore2
    reboundsScore = reboundsScore1 + reboundsScore2
    assistsScore = assistsScore1 + assistsScore2
    stealsScore = stealsScore1 + stealsScore2
    blocksScore = blocksScore1 + blocksScore2
    turnoversScore = turnoversScore1 + turnoversScore2

    scores = [score, fgScore, ftScore, threesScore, pointsScore, reboundsScore,\
              assistsScore, stealsScore, blocksScore, turnoversScore]
    return scores

def printTeam(team):
    playerScores = team[0]
    [player, scores] = playerScores
    teamPlayer = FantasyPlayer(nameFormat("Team"), 0, 0, 0, 0, 0, 0, 0, 0, 0,\
                               0, 0, 0, 0, 0, 0, 0)
    teamScores = scores

    printPlayerScoresHeader("")
    printPlayerScores(playerScores, "")

    for playerScores in team[1:]:
        [player, scores] = playerScores
        # TODO: This doesn't really make sense...a sum of standard deviations
        # doesn't equal the standard deviation of the sums.
        teamScores = addScores(teamScores, scores)
        printPlayerScores(playerScores, "")

    print("")
    printPlayerScores([teamPlayer, teamScores], "")

def addPlayerByNameToTeam(team, allPlayerScores, name):
    pattern = '.*' + name + '.*'
    for playerScores in allPlayerScores:
        [player, scores] = playerScores
        if re.match(pattern, player.name, re.IGNORECASE):
            team.append(playerScores)
            break

def main():
    [allPlayers, allStats] = readAllPlayersAndStats("nba_2009-10_stats.csv")

    """
    player = getPlayerByName(allPlayers, "amar'e")
    print(player)
    """

    """
    player = FantasyPlayer(nameFormat("Amar'e Stoudemire"), 80, 80, 80*30, \
                           80*100, 80*100, 80*25, 80*25, 80*25, 80*25, \
                           80*10, 80*0, 80*25, 80*25, 80*25, 80*10, 80*100)
    """
    # replaceScaledPlayerByMinutes(allPlayers, "amar'e", 100)
    replaceScaledPlayerByMinutes(allPlayers, 'lebron', 28)
    replaceScaledPlayerByMinutes(allPlayers, 'dwyane', 32)
    replaceScaledPlayerByMinutes(allPlayers, 'bosh', 32)
    replaceScaledPlayerByMinutes(allPlayers, 'danilo', 22)
    replaceScaledPlayerByMinutes(allPlayers, 'felton', 36)
    replaceScaledPlayerByMinutes(allPlayers, 'derozan', 26)
    replaceScaledPlayerByMinutes(allPlayers, 'luol', 30)
    replaceScaledPlayerByMinutes(allPlayers, 'joakim', 36)
    replaceScaledPlayerByMinutes(allPlayers, 'hibbert', 34)
    replaceScaledPlayerByMinutes(allPlayers, 'gooden', 22)
    replaceScaledPlayerByMinutes(allPlayers, 'salmons', 30)
    replaceScaledPlayerByMinutes(allPlayers, 'vince', 28)
    replaceScaledPlayerByMinutes(allPlayers, 'conley', 35)
    replaceScaledPlayerByMinutes(allPlayers, 'ariza', 33)
    replaceScaledPlayerByMinutes(allPlayers, 'duncan', 30)
    replaceScaledPlayerByMinutes(allPlayers, 'arron', 32)
    replaceScaledPlayerByMinutes(allPlayers, 'nene', 32)
    replaceScaledPlayerByMinutes(allPlayers, 'camby', 27)
    replaceScaledPlayerByMinutes(allPlayers, 'dorell', 25)
    replaceScaledPlayerByMinutes(allPlayers, 'channing', 22)

    player = makePlayerFromAverages(nameFormat("Devin Harris"), \
                                    32.9, 7.5, 12.5, 1.0, 1.5, 5.5, 7.0,\
                                    0.0, 4.5, 9.5, 3.5, 1.5, 0.0, 21.5)
    replacePlayer(allPlayers, 'devin harris', player)

    player = makePlayerFromAverages(nameFormat("Derrick Rose"),\
                                    34.5, 10.0, 25.0, 1.0, 5.0, 6.0, 7.5,\
                                    0.5, 3.5, 6.0, 2.0, 0.8, 0.5, 23.0)
    replacePlayer(allPlayers, 'derrick rose', player)

    player = makePlayerFromAverages(nameFormat("J.J. Hickson"),\
                                    25.3, 5.0, 10.0, 0.0, 0.0, 4.0, 5.0,\
                                    1.7, 4.0, 1.7, 2.0, 0.4, 0.5, 14.0)
    replacePlayer(allPlayers, 'j.j. hickson', player)

    """
    player = makePlayerFromAverages(nameFormat("Carlos Delfino"),\
                                    36.0, 6.0, 12.3, 4.0, 8.7, 1.2, 1.6,\
                                    0.0, 4.7, 1.3, 1.0, 1.5, 0.0, 16.7)
    replacePlayer(allPlayers, 'delfino', player)
    """

    player = makePlayerFromAverages(nameFormat("Brandon Jennings"),\
                                    38.5, 5.0, 12.3, 1.7, 5.0, 4.7, 6.0,\
                                    1.0, 4.0, 8.0, 1.7, 0.3, 0.0, 16.3)
    replacePlayer(allPlayers, 'jennings', player)

    player = makePlayerFromAverages(nameFormat("Gerald Wallace"),\
                                    41.0, 5.3, 12.0, 0.3, 1.0, 7.7, 10.0,\
                                    1.5, 7.5, 2.0, 3.0, 1.5, 1.1, 18.7)
    replacePlayer(allPlayers, 'gerald wallace', player)

    player = makePlayerFromAverages(nameFormat("Luis Scola"),\
                                    36, 10.0, 18.2, 0.0, 0.0, 5.3, 7.0,\
                                    2.0, 8.5, 2.0, 1.8, 0.7, 1.0, 18.0)
    replacePlayer(allPlayers, 'scola', player)

    player = makePlayerFromAverages(nameFormat("Russel Westbrook"),\
                                    36.0, 6.0, 14.0, 0.2, 1.2, 4.5, 5.7,\
                                    2.0, 4.0, 8.0, 3.3, 1.6, 0.4, 20.0)
    replacePlayer(allPlayers, 'westbrook', player)

    player = makePlayerFromAverages(nameFormat("Francisco Garcia"),\
                                    30.0, 4.5, 10.2, 1.4, 2.4, 2.3, 2.7,\
                                    0.9, 2.5, 2.3, 1.7, 1.2, 1.0, 12.7)
    replacePlayer(allPlayers, 'francisco garcia', player)

    # Add rookies
    player = makePlayerFromAverages(nameFormat("John Wall"),\
                                    38.0, 7.0, 17.0, 1.0, 1.5, 4.0, 5.0,\
                                    0.0, 3.0, 8.0, 3.0, 1.2, 0.0, 20.0)
    allPlayers.append(player)

    player = makePlayerFromAverages(nameFormat("Blake Griffin"),\
                                    33.0, 6.0, 12.0, 0.0, 0.0, 3.0, 5.5,\
                                    3.0, 6.5, 2.0, 1.0, 0.7, 0.0, 15.0)
    allPlayers.append(player)

    player = makePlayerFromAverages(nameFormat("DeMarcus Cousins"),\
                                    25.0, 4.3, 9.3, 4.7, 6.0, 1.3, 6.0,\
                                    1.3, 6.0, 2.3, 2.3, 0.7, 0.0, 13.3)
    allPlayers.append(player)

    allPlayerScores = getAllPlayerScores(allPlayers, allStats)
    outOfThisWorldThreshold = 4.0
    topFlightThreshold = 2.5
    greatContributorThreshold = 1.75
    goodContributorThreshold = 1.0
    nonLiabilityThreshold = 0.5
    #scoreThreshold = topFlightThreshold
    scoreThreshold = nonLiabilityThreshold
    scoreFreqs = getScoreFrequencies(allPlayerScores, scoreThreshold)
    printAverageStats(allStats, scoreFreqs, scoreThreshold)
    printAllPlayerScores(allPlayerScores)

    """
    team = []
    for i in range(0, (13+1)*12, 12):
        team.append(allPlayerScores[i])
    """

    """
    team = allPlayerScores[0:10]
    printTeam(team)
    print("\n")

    team = allPlayerScores[10:20]
    printTeam(team)
    print("\n")

    team = allPlayerScores[20:30]
    printTeam(team)
    print("\n")
    """

    team = []
    addPlayerByNameToTeam(team, allPlayerScores, "granger")
    addPlayerByNameToTeam(team, allPlayerScores, "kidd")
    addPlayerByNameToTeam(team, allPlayerScores, "iguodala")
    addPlayerByNameToTeam(team, allPlayerScores, "marc gasol")
    addPlayerByNameToTeam(team, allPlayerScores, "nene")
    addPlayerByNameToTeam(team, allPlayerScores, "garnett")
    addPlayerByNameToTeam(team, allPlayerScores, "jason terry")
    addPlayerByNameToTeam(team, allPlayerScores, "biedrins")
    addPlayerByNameToTeam(team, allPlayerScores, "kirilenko")
    addPlayerByNameToTeam(team, allPlayerScores, "garcia")
    addPlayerByNameToTeam(team, allPlayerScores, "j.r.")
    addPlayerByNameToTeam(team, allPlayerScores, "morrow")
    addPlayerByNameToTeam(team, allPlayerScores, "udrih")
    print("")
    printTeam(team)

if __name__ == "__main__":
    main()
