# Abstract class
# A player has to move and punish himself
class Player:
    def __init__(self, playingField, symbol):
        self.playingField = playingField
        self.symbol = symbol
        self.gamesWon = 0

    def makeMove(self):
        pass

    def punish(self):
        pass