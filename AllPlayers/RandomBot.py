# RandomBot which makes random move
from AllPlayers.Player import Player
import random

class RandomBot(Player):
    def __init__(self, playingField, symbol):
        Player.__init__(self, playingField, symbol)

    def makeMove(self):
        randomMove = random.choice(self.playingField.possibleMoves())
        potentialWinner = self.playingField.executeAction(randomMove, self.symbol)
        if potentialWinner == self.symbol:
            self.gamesWon += 1

    def punish(self):
        pass

