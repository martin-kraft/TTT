import random
from AllPlayers.Player import Player
from AllPlayers.QTable import QTable

class RLBot(Player):
    def __init__(self, playingField, symbol, alpha, gamma, rho):
        Player.__init__(self, playingField, symbol)
        self.alpha = alpha
        self.gamma = gamma
        self.rho = rho
        # Every agent has his own table
        self.qTable = QTable()

        # Last states used to calculate the new quality
        # Used to calculate the punishment if opponent wins the game
        self.lastStates = None
        
        self.rewardWin = 1.0
        self.rewardDraw = 0.0
        self.rewardLose = -1.0

    def makeMove(self):
        # Q(s, a) = (1 - alpha) Q(s, a) + alpha(reward + gamma * max(Q(s', a' )))
        oldState = tuple(self.playingField.occupiedFields)
        action = self.selectAction(oldState)
        reward = self.calcReward(self.playingField.executeAction(action, self.symbol))
        nextState = tuple(self.playingField.occupiedFields)
        possibleMoves = self.playingField.possibleMoves()

        self.lastStates = (oldState, nextState, action, self.rewardLose, possibleMoves)
        self.calcQuality(oldState, nextState, action, reward, possibleMoves)

    def printTable(self):
        return self.qTable.printQ(tuple(self.playingField.occupiedFields))

    def calcQuality(self, oldState, nextState, action, reward, possibleMoves):
        # Q(s, a) = (1 - alpha) Q(s, a) + alpha(reward + gamma * max(Q(s', a' )))
        oldQuality = self.qTable.getQuality(oldState, action)
        followStateQuality = self.qTable.getBestQuality(nextState, possibleMoves)
        newQuality = (1.0 - self.alpha) * oldQuality + self.alpha * (reward + self.gamma * followStateQuality)
        if newQuality != oldQuality:
            self.qTable.update(oldState, action, newQuality)

        return newQuality

    def selectAction(self, state):
        if random.random() < self.rho:
            result = random.choice(self.playingField.possibleMoves())
        else:
            result = self.qTable.bestAction(state, self.playingField.possibleMoves())
        return result

    # Parameter potentialWinner: '' = Draw; None = no winner; 'X' or 'O' = winning symbol
    def calcReward(self, potentialWinner):
        result = 0.0
        if potentialWinner == '':
            result = self.rewardDraw
        elif potentialWinner == self.symbol:
            result = self.rewardWin
            self.gamesWon += 1
        return result

    def punish(self):
        if self.lastStates:
           self.calcQuality(*self.lastStates)

    def resetQTables(self):
        self.qTable = QTable()