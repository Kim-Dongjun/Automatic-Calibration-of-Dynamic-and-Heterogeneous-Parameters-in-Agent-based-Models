import numpy as np

def fitnessCalculator(simResult, trueResult):
    #maxValue = []
    #for summaryStatisticsDim in range(len(trueResult)):
    #    maxValue.append(max(trueResult[summaryStatisticsDim]))
    error = 0
    print("simulation result shape : ", np.array(simResult).shape)
    print("trueResult shape : ", np.array(trueResult).shape)
    for candidate in range(len(simResult)):
        for summaryStatisticsDim in range(len(simResult[0])):
            for time in range(len(simResult[0][0])):
                error += abs(simResult[candidate][summaryStatisticsDim][time] - trueResult[summaryStatisticsDim][time]) / trueResult[summaryStatisticsDim][time]
    error = error / (len(simResult[0]) * len(simResult[0][0]))
    return -error