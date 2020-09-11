import time

from kivy.clock import Clock
from kivy.core.window import Window
from AllPlayers.RLBot import RLBot
from AllPlayers.RandomBot import RandomBot
from AllPlayers.ERLBot import ERLBot

# Contains the agents which play against each other
# Also initialises players

class PlayerHub:
    def __init__(self):
        self.playingField = None
        self.playerOne = None
        self.playerTwo = None

        self.gamesPlayed = 0

        # One iteration = one turn for p1 and one turn for p2
        # For consistency of who is going to make the first move in every game
        # it is necessary to stop the turn exchange earlier
        self.endTurnExchange = False

        # Boolean which is set from statView to interrupt training
        self.stopTraining = False

        self.trainingIteration = 0
        self.trainingMaxIteration = 0
        self.startingPolicy = 0

        # Callback for progress bar and qLabel
        self.progressCallback = None
        self.qLabelCallback = None

        # Variable for changing starting turn policy
        # False = p1; True = p2
        self.firstMove = False

    # This function is called from the StatView after pressing the 'Start!' Button
    # Initialising variables and creating bots
    def setUpTraining(self, bot1, bot2, iterations, playerOneValueTuple, playerTwoValueTuple):
        # bot1, bot2 -> integer: 0 -> StBot; 1 -> AltBot; 2 -> RandomBot
        # startingPolicy -> integer: 0 = P1 starts; 1 = P2 starts; 2 = taking turns with starting move, P1 begins

        self.creatingPlayers(bot1, bot2, playerOneValueTuple, playerTwoValueTuple)

        self.trainingMaxIteration = iterations

        # Resetting player stats and field
        self.playingField.resetPlayingField()
        self.resetGameCounter()
        self.printGameStatIntoWindow('        ')

        Clock.max_iteration = 33
        Clock.schedule_interval(lambda dt: self.takeTurns(), -1)

        # Show playing field every x times
        self.playingField.showEveryXTurns = 1

    def takeTurns(self):
        if self.startingPolicy == 0:
            self.playerOne.makeMove()
            if self.endTurnExchange == False:
                self.playerTwo.makeMove()
            else:
                # game has ended, resetting field
                self.playingField.resetPlayingField()

        elif self.startingPolicy == 1:
            self.playerTwo.makeMove()
            if self.endTurnExchange == False:
                self.playerOne.makeMove()
            else:
                # game has ended, resetting field
                self.playingField.resetPlayingField()

        else:
            # firstMove = False -> p1 is starting
            # firstMove = True -> p2 is starting
            if self.firstMove == False:
                self.playerOne.makeMove()
                if self.endTurnExchange == False:
                    self.playerTwo.makeMove()
                else:
                    # game has ended, resetting field
                    self.playingField.resetPlayingField()
            else:
                self.playerTwo.makeMove()
                if self.endTurnExchange == False:
                    self.playerOne.makeMove()
                else:
                    # game has ended, resetting field
                    self.playingField.resetPlayingField()
        if self.endTurnExchange:
            self.gamesPlayed += 1
        self.endTurnExchange = False

        # After taking turns check for training end
        self.trainingIteration+=1
        # Update progress bar
        self.progressCallback(self.trainingIteration)
        if self.stopTraining == True or self.trainingIteration == self.trainingMaxIteration:
            self.stopTraining = False
            self.trainingIteration = 0
            self.progressCallback(self.trainingIteration)
            self.playingField.resetPlayingField()
            self.playingField.showFieldCount = 0
            self.playingField.showEveryXTurns = 1
            self.initPlayingAgainstHuman()
            return False

    def setQLabelCB(self, cb):
        self.qLabelCallback = cb

    # Bot vs. Human
    # Initialising a RandomBot if there is
    def makeTurn(self):
        if self.playerOne is None:
            self.playerOne = RandomBot(self.playingField, 'X')
        if self.playerTwo is None:
            self.playerTwo = RandomBot(self.playingField, 'O')

        # Before each move the qTable entry for the last state is updated
        self.printTable()
        self.playerOne.makeMove()
        if self.endTurnExchange:
            self.playingField.resetPlayingField()
            if self.firstMove == False:
                self.printTable()
                self.playerOne.makeMove()
        self.endTurnExchange = False

    # Method called from PlayingField
    # For a Draw, both EnhancedRLBot players propagate draw Values
    def propagateDraw(self):
        if type(self.playerOne) == ERLBot:
            self.playerOne.propagateAllTurns(self.playerOne.rewardDraw)
        if type(self.playerTwo) == ERLBot:
            self.playerTwo.propagateAllTurns(self.playerTwo.rewardDraw)

    # Printing last state from
    def printTable(self):
        if isinstance(self.playerOne, RLBot):
            qList = self.playerOne.printTable()
            self.qLabelCallback(qList)

    def printGameStatIntoWindow(self, winner):
        p1Wins = self.playerOne.gamesWon
        p2Wins = self.playerTwo.gamesWon
        # P1 -> X; P2 -> O
        Window.set_title('TTT' + ' - X:' + str(p1Wins) + ' - O:' + str(p2Wins) + ' - Last winner: ' + winner + ' Games played: ' + str(self.gamesPlayed))

    def setProgressCB(self, callback):
        self.progressCallback = callback

    def punishLoser(self, winner):
        if self.playerOne.symbol != winner:
            self.playerOne.punish()
        else:
            self.playerTwo.punish()

    def stopTrainingSession(self):
        self.stopTraining = True

    def setPlayingField(self, playingField):
        self.playingField = playingField

    def setExplorationRate(self, value, change):
        if isinstance(self.playerOne, RLBot) and change == 1:
            self.playerOne.rho = value
        if isinstance(self.playerTwo, RLBot) and change == 2:
            self.playerTwo.rho = value

    def setDiscountRate(self, value, change):
        if isinstance(self.playerOne, RLBot) and change == 1:
            self.playerOne.gamma = value
        if isinstance(self.playerTwo, RLBot) and change == 2:
            self.playerTwo.gamma = value

    def setLearningRate(self, value, change):
        if isinstance(self.playerOne, RLBot) and change == 1:
            self.playerOne.alpha = value
        if isinstance(self.playerTwo, RLBot) and change == 2:
            self.playerTwo.alpha = value

    def creatingPlayers(self, bot1, bot2, playerOneValueTuple, playerTwoValueTuple):
        # If the last bot in the player position is the same kind, just the starting variables are changed
        # bot1, bot2 -> integer: 0 -> StBot; 1 -> AltBot; 2 -> RandomBot
        # Creating bot1
        if bot1 == 0:
            if not type(self.playerOne) == RLBot or self.playerOne is None:
                self.playerOne = RLBot(self.playingField, 'X', *playerOneValueTuple)
        elif bot1 == 1:
            if not type(self.playerOne) == ERLBot or self.playerOne is None:
                self.playerOne = ERLBot(self.playingField, 'X', *playerOneValueTuple)
        else:
            self.playerOne = RandomBot(self.playingField, 'X')
        # Creating bot2
        if bot2 == 0:
            if not type(self.playerTwo) == RLBot or self.playerTwo is None:
                self.playerTwo = RLBot(self.playingField, 'O', *playerTwoValueTuple)
        elif bot2 == 1:
            if not type(self.playerTwo) == ERLBot or self.playerTwo is None:
                self.playerTwo = ERLBot(self.playingField, 'O', *playerTwoValueTuple)
        else:
            self.playerTwo = RandomBot(self.playingField, 'O')

    def resetGameCounter(self):
        self.playerOne.gamesWon = 0
        self.playerTwo.gamesWon = 0

    def setStartingPolicy(self, value):
        self.startingPolicy = value

    def changeStartingPlayer(self):
        # startingPolicy -> integer: 0 = P1 starts; 1 = P2 starts; 2 = taking turns with starting move, P1 begins
        if self.startingPolicy == 2:
            if self.firstMove == False:
                self.firstMove = True
            else:
                self.firstMove = False

    def clearStateField(self):
        if isinstance(self.playerOne, ERLBot):
            self.playerOne.lastStates.clear()
        if isinstance(self.playerTwo, ERLBot):
            self.playerTwo.lastStates.clear()

    def initPlayingAgainstHuman(self):
        self.firstMove = False
        if self.startingPolicy == 0 or self.startingPolicy == 2:
            self.makeTurn()

    def resetQTables(self):
        if self.playerOne:
            if isinstance(self.playerOne, RLBot):
                self.playerOne.resetQTables()
        if self.playerTwo:
            if isinstance(self.playerTwo, RLBot):
                self.playerTwo.resetQTables()