import random
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window

# Contains playing field and game logic
class PlayingField(GridLayout):

    def __init__(self, playerHub):
        GridLayout.__init__(self)
        # List with numbers from 0 to 8, also functions as state for RL
        self.occupiedFields = None

        self.actualField = None
        self.initField(3)
        self.lasMove = None

        # Refresh play field every x turns
        self.showEveryXTurns = 1
        self.showFieldCount = 0

        self.playerHub = playerHub
        self.playerHub.setPlayingField(self)

    def initField(self, rowCols):
        self.rows = rowCols
        self.actualField = [[None for _ in range(rowCols)] for _ in range(rowCols)]
        self.occupiedFields = [i for i in range(rowCols*rowCols)]
        counterID = 0
        for row in range(rowCols):
            for col in range(rowCols):
                button = Button()
                button.id = str(counterID)
                counterID += 1
                button.font_size = 64
                self.actualField[row][col] = button
                button.bind(on_press = self.handleClick)
                self.add_widget(button)

    # Assign symbol to clicked button; for human interaction with the field
    def handleClick(self, instance):
        # Check if box empty
        if instance.text is '':
            # Placing the symbol
            self.occupiedFields[int(instance.id)] = 'O'

            # Check game status after each turn
            potentialWinner = self.checkGameState()
            if potentialWinner == '' or potentialWinner == 'X' or potentialWinner ==  'O':
                self.resetPlayingField()

            self.playerHub.makeTurn()

    # Checking the playing field if three symbols of the same kind are in a vertical, horizontal or diagonal grouping
    # Also checking for a draw
    # Returns winner which is the last set symbol
    def checkGameState(self):
        # Using occupiedField for text representation
        # Better to have a text representation of the gaming field which is then drawn every now and then
        # to the graphic representation for unloading the user interface

        # Convert 1d list into 2d representation
        fieldToText = [self.occupiedFields[i:i+self.rows] for i in range(0, len(self.occupiedFields), self.rows)]
        # Fill in the numbers with ''
        fieldToText = [['' if isinstance(element, int) else element for element in row] for row in fieldToText]

        winner = None

        ## Draw
        counter = 0
        for elements in self.occupiedFields:
            if elements == 'X' or elements == 'O':
                counter += 1
                if counter == (len(self.actualField) * len(self.actualField[0])):
                        winner = ''

        ## Vertical
        for symbolIndex in range(len(self.actualField[0])):
            # Each value in the first list represents the potential symbol (player) which wins
            potentialWinner = fieldToText[0][symbolIndex]
            potentialWinner = [potentialWinner] * len(self.actualField[0])

            # Each entry in result represents a whole column of the field
            allCols = zip(*fieldToText)
            result = list(allCols)
            if potentialWinner[symbolIndex] != '' and tuple(potentialWinner) == result[symbolIndex]:
                winner = potentialWinner[0]

        ## Horizontal
        for row in fieldToText:
                potentialWinner = row[0] * len(self.actualField[0])
                if row == list(potentialWinner):
                    winner = potentialWinner[0]

        ## Diagonal: \
        for row in fieldToText:
            potentialWinner = row[0] * len(self.actualField[0])
            if [row[index] for index, row in enumerate(fieldToText)] == list(potentialWinner):
                winner = potentialWinner[0]

        ## Diagonal: /
        for row in fieldToText:
            potentialWinner = row[len(self.actualField[0]) - 1] * len(self.actualField[0])
            if [row[~index] for index, row in enumerate(fieldToText)] == list(potentialWinner):
                winner = potentialWinner[0]

        if winner:
            # print('Winner is: ' + winner)
            #Window.set_title('TTT - Last winner: ' + winner)

            # Between the players, the field is the third party
            # If a RL-Agent makes a move, he is not getting punished -> only draw or win is possible in his move
            self.playerHub.punishLoser(winner)
            self.playerHub.endTurnExchange = True
            self.playerHub.changeStartingPlayer()

            # Adjusting the argument which is given to the print function to reduce twitching of the window title
            if winner == 'X':
                winnerRep = 'X       '
            else:
                winnerRep = 'O       '

            self.playerHub.printGameStatIntoWindow(winnerRep)

        elif winner == '':
            self.playerHub.endTurnExchange = True
            self.playerHub.printGameStatIntoWindow('Draw!')
            self.playerHub.propagateDraw()
            self.playerHub.changeStartingPlayer()

        return winner

    def resetPlayingField(self):
        for row in self.actualField:
            for col in row:
                col.text = ''
        self.occupiedFields = [i for i in range(len(self.occupiedFields))]

    # Called from all computer players, to calculate reward
    # Returns the potential winner
    def executeAction(self, position, symbol):
        self.occupiedFields[position] = symbol
        self.showFieldCount += 1
        if self.showFieldCount == self.showEveryXTurns:
            self.drawPlayingField()
            self.showFieldCount = 0
        return self.checkGameState()

    # Draw field from occupiedFields
    def drawPlayingField(self):
        indexCounter = 0
        for row in self.actualField:
            for col in row:
                if isinstance(self.occupiedFields[indexCounter], int):
                    col.text = ''
                else:
                    col.text = self.occupiedFields[indexCounter]
                    if col.text == 'X':
                        col.color = 1, 0, 0, 1
                    else:
                        col.color = 1, 1, 0, 1

                indexCounter += 1

    # Return a list with indices which represents all possible moves
    def possibleMoves(self):
        moves = []
        for entry in self.occupiedFields:
            if isinstance(entry, int):
                moves.append(entry)
        return moves

