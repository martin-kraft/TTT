from AllPlayers.RLBot import RLBot

# Uses the altered Q-Learning version:
# Calculate Q's after after win, draw or lose to all previous moves in the game
class ERLBot(RLBot):
    def __init__(self, playingField, symbol, alpha, gamma, rho):
        RLBot.__init__(self, playingField, symbol, alpha, gamma, rho)

        self.lastStates = []

    def makeMove(self):
        oldState = tuple(self.playingField.occupiedFields)
        action = self.selectAction(oldState)
        reward = self.calcReward(self.playingField.executeAction(action, self.symbol))
        nextState = tuple(self.playingField.occupiedFields)
        possibleMoves = self.playingField.possibleMoves()

        self.lastStates.append((oldState, nextState, action, reward, possibleMoves))

        if reward == self.rewardWin:
            self.propagateAllTurns(reward)

    def punish(self):
        if self.lastStates:
            self.propagateAllTurns(self.rewardLose)

    def propagateAllTurns(self, reward):
        # After each iteration of the while loop alteredReward changes
        alteredReward = reward
        while self.lastStates:
            # Adding the reward to the last turn
            tempList = list(self.lastStates[-1])
            tempList[3] = alteredReward
            self.lastStates[-1] = tuple(tempList)

            self.calcQuality(*self.lastStates[-1])

            alteredReward *= self.gamma

            del self.lastStates[-1]