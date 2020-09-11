import random
import sys

# Used by RLBot
class QTable:

    def __init__(self):
        # Dictionary; qTable<state<action, value>>
        self.qTable = {}

    # Update the table,
    # if state is not dictionary, it is created
    def update(self, state, action, value):
        if state not in self.qTable:
            self.qTable[state] = {action: 0.0}
        self.qTable[state][action] = value

    # Returning the quality for a specific state-action pair
    def getQuality(self, state, action):
        # State not visited -> initialize with standard value of 0.0
        if state not in self.qTable:
            self.qTable[state] = {action: 0.0}
        # Performed action for first time
        if action not in self.qTable[state]:
            self.qTable[state][action] = 0.0
        return self.qTable[state][action]

    # Helper method to initialise States and actions if needed
    def lazyInit(self, state, actions):
        if state not in self.qTable:
            for action in actions:
                self.qTable[state] = {action : 0.0}

    # Returning highest Quality from given state and actions
    def getBestQuality(self, state, actions):
        if state not in self.qTable:
            self.lazyInit(state, actions)
            return 0.0

        value = -sys.maxsize-1

        for action in actions:
            # Initialising the action for the given state
            if action not in self.qTable[state]:
                self.qTable[state][action] = 0.0
            if self.qTable[state][action] > value:
                value = self.qTable[state][action]

        return value

    # Collecting all actions which have the highest value
    # Multiple actions with same value allowed
    # Returning a random element from the list to explore more states
    def bestAction(self, state, actions):
        if state not in self.qTable:
            self.lazyInit(state, actions)
            return random.choice(actions)

        resultActionList = []
        valueMax = -sys.maxsize-1
        for action in actions:
            # Action previously not performed
            if action not in self.qTable[state]:
                self.qTable[state][action] = 0.0

            value = self.qTable[state][action]
            if self.qTable[state][action] > valueMax:
                valueMax = value
                resultActionList.clear()
                resultActionList.append(action)

            if value == valueMax:
                resultActionList.append(action)

        return random.choice(resultActionList)

    # Return the qualities for a specific state in list-form
    def printQ(self, state):
        if state in self.qTable:
            listOfQs = [0.0] * 9
            for i in range(len(listOfQs)):
                if i in self.qTable[state]:
                    listOfQs[i] = self.qTable[state][i]
            return listOfQs







