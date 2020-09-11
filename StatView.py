import sys
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.pagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button


# Controller for game settings, collects and creates
class StatView(PageLayout):
    def __init__(self, playerHub):
        PageLayout.__init__(self)
        self.playerHub = playerHub

        # Std values
        self.bot1 = 0
        self.bot2 = 0

        self.isTraining = False

        self.qLabels = self.getIDsFromQLabels()

        # For Keyboard shortcuts
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)

    def keyboard_closed(self):
        print('My keyboard have been closed!')
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard = None

    # Handling keyboard input
    def on_keyboard_down(self, window, keycode, text, modifiers):
        # Start or cancel training
        if keycode[1] == 's':
            self.initTraining()
        # Reset the tables
        elif keycode[1] == 't':
            self.resetQTables()

    # Initialise training, if not training
    # If training, stop training
    def initTraining(self):
        if self.isTraining == False:
            iterations = self.ids.textInput.text
            if iterations == '':
                iterations = 50000
            else:
                iterations = int(iterations)

            # Gathering all initial Values
            learnRate = self.ids.alphaSlider1.value
            discountRate = self.ids.gammaSlider1.value
            explorationRate = self.ids.explorationSlider1.value
            playerOneValues = (learnRate, discountRate, explorationRate)

            learnRate1 = self.ids.alphaSlider2.value
            discountRate1 = self.ids.gammaSlider2.value
            explorationRate1 = self.ids.explorationSlider2.value
            playerTwoValues = (learnRate1, discountRate1, explorationRate1)

            self.ids.progress.max = iterations

            self.playerHub.setProgressCB(self.setProgress)
            self.playerHub.setQLabelCB(self.fillQStates)

            self.playerHub.setUpTraining(self.bot1, self.bot2, iterations, playerOneValues,playerTwoValues)
            self.isTraining = True
        else:
            self.playerHub.stopTrainingSession()
            self.isTraining = False

    # Returning a list of Labels which are created vie TTT.kv
    def getIDsFromQLabels(self):
        listOfLabelIDs = []
        listOfLabelIDs.append(self.ids.q0)
        listOfLabelIDs.append(self.ids.q1)
        listOfLabelIDs.append(self.ids.q2)
        listOfLabelIDs.append(self.ids.q3)
        listOfLabelIDs.append(self.ids.q4)
        listOfLabelIDs.append(self.ids.q5)
        listOfLabelIDs.append(self.ids.q6)
        listOfLabelIDs.append(self.ids.q7)
        listOfLabelIDs.append(self.ids.q8)

        return listOfLabelIDs

    # Filling quality table after each turn
    def fillQStates(self, qualityList):
        index = 0
        maxValue = -sys.maxsize-1
        listOfValues = []
        noState = '**!**'
        fieldOcc = '***'
        occField = self.playerHub.playingField.occupiedFields
        if qualityList:
            # Finding the elements with highest value and putting them into a list
            for q in qualityList:
                # Reset the color of the label and update the button text
                self.qLabels[index].color = 1,1,1,1
                self.qLabels[index].text = str(round(q, 2))

                # 0 values should not be considered if the corresponding place is occupied
                if isinstance(occField[index], int):
                    if q > maxValue:
                        maxValue = q
                        listOfValues.clear()
                        listOfValues.append(self.qLabels[index])
                    if q == maxValue:
                        listOfValues.append(self.qLabels[index])

                else:
                    # Fields which are taken
                    self.qLabels[index].text = fieldOcc
                    self.qLabels[index].color = 0.9, 0, 0.9, 1

                index += 1
        else:
            # If state not visited, reset all values and color
            for label in self.qLabels:
                label.text = noState
                label.color = 0.1, 0.9, 0.9, 1

        # Mark the q's with highest value
        for label in listOfValues:
            if label.text != fieldOcc:
                label.color = 0.1, 0.9, 0.1, 1

    # Handling the progress on the progress bar
    # Send to PlayerHub instance as callback
    def setProgress(self, value):
        if value == self.ids.progress.max:
            value = 0
            self.isTraining = False
        self.ids.progress.value = value

    # Handling Reset table button
    def resetQTables(self):
        self.playerHub.resetQTables()
        # Feedback for deleting tables
        box = BoxLayout(orientation='vertical')
        button = Button(text='OK', size_hint=(1, .25))
        box.add_widget(Label(text='All tables were reset!'))
        box.add_widget(button)
        popup = Popup(title='', content=box, size_hint=(None, None), size=(400, 400))
        button.bind(on_press = popup.dismiss)
        popup.open()

    #--- More handle methods for slider und buttons
    def setPlayer1(self, value):
        # Value -> integer: 0 -> StBot; 1 -> AltBot; 2 -> RandomBot
        self.bot1 = value

    def setPlayer2(self, value):
        # Value -> integer: 0 -> StBot; 1 -> AltBot; 2 -> RandomBot
        self.bot2 = value

    def setStarting(self, value):
        self.playerHub.setStartingPolicy(value)

    def explorationChange(self, value, change):
        self.playerHub.setExplorationRate(value, change)
        print('Exploration: ' + str(value) +' '+ str(change))

    def learningChange(self, value, change):
        self.playerHub.setLearningRate(value, change)
        print('Learning: ' + str(value) +' ' + str(change))

    def discountChange(self, value, change):
        self.playerHub.setDiscountRate(value, change)
        print('Disco: ' + str(value) +' '+ str(change))

