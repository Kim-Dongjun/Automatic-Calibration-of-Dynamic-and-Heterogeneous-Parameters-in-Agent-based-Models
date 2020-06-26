import os
import csv
import numpy as np


def simulationPerformance(running_folder, trueResult, numCandidate):
    file = open(running_folder + '/SimulationResult.csv','r')
    lines = file.readlines()
    file.close()
    performance = []
    simResult = []
    for candidate in range(numCandidate):
        simResult.append([])
        for summaryStatisticsDim in range(len(trueResult)):
            line = lines[candidate * len(trueResult) + summaryStatisticsDim].split(',')
            line[-1] = line[-1][:-1]
            line = [float(x) for x in line]
            simResult[candidate].append(line)
    for candidate in range(numCandidate):
        performance.append(calculateMAPE(simResult[candidate],trueResult))
    return performance

def calculateMAPE(simResult,trueResult):
    error = 0
    for summaryStatisticsDim in range(len(simResult)):
        for time in range(len(simResult[0])):
            error += abs(simResult[summaryStatisticsDim][time] - trueResult[summaryStatisticsDim][time]) / trueResult[summaryStatisticsDim][time]
    error /= (float(len(simResult)) * float(len(simResult[0])))
    return error

def getPerformance(cycle, running_folder, trueResult, dynamicNumberIterations, heterogeneousNumberIterations, numCandidate):
    dirs = []
    totalIterations = dynamicNumberIterations + heterogeneousNumberIterations
    for itr in range(totalIterations):
        dirs.append(running_folder + "/iteration_" + str(totalIterations * cycle + itr))
    performance = []
    for itr in range(dynamicNumberIterations):
        performance.append(simulationPerformance(dirs[itr], trueResult, numCandidate))
    return dirs, performance

def getHeterogeneousPerformance(cycle, running_folder, trueResult, dynamicNumberIterations, heterogeneousNumberIterations, numCandidate):
    dirs = []
    totalIterations = dynamicNumberIterations + heterogeneousNumberIterations
    for itr in range(totalIterations):
        dirs.append(running_folder + "/iteration_" + str(totalIterations * cycle + itr))
    performance = []
    for itr in range(dynamicNumberIterations, dynamicNumberIterations+heterogeneousNumberIterations):
        performance.append(simulationPerformance(dirs[itr], trueResult, 1))
    return dirs, performance

def findOptimalParameter(cycle, running_folder, trueResult, numCandidate, dynamicNumberIterations, heterogeneousNumberIterations, numEstParams, numTimeStep):
    dirs, performance = getPerformance(cycle, running_folder, trueResult, dynamicNumberIterations, heterogeneousNumberIterations, numCandidate)
    print("performance : ", performance)
    minErrorIdx = np.argmin(performance)
    minIteration = minErrorIdx // numCandidate
    #minCandidate = np.argmin(performance[minIteration])
    minCandidate = minErrorIdx % numCandidate
    print("minIteration, minCandidate : ", minIteration, minCandidate)
    file = open(dirs[minIteration] + '/DynamicParameter_Candidate_' + str(minCandidate) + '.csv','r')
    lines = file.readlines()
    file.close()
    dynamicParameter = np.zeros((numEstParams,numCandidate,numTimeStep))
    for estParam in range(len(lines)):
        dynamicParameter[estParam][0] = [float(x) for x in lines[estParam].split(',')]
    for estParam in range(numEstParams):
        for candidate in range(1,numCandidate):
            temp = np.random.random()
            for time in range(numTimeStep):
                dynamicParameter[estParam][candidate][time] = temp
    return dynamicParameter

def findOptimalHeterogeneousParameter(cycle, running_folder, trueResult, numCandidate, dynamicNumberIterations, heterogeneousNumberIterations, heterogeneousParameter):
    dirs, performance = getHeterogeneousPerformance(cycle, running_folder, trueResult, dynamicNumberIterations, heterogeneousNumberIterations, numCandidate)
    print("performance : ", performance)
    minErrorIdx = np.argmin(performance)
    print("minErrorIdx : ", minErrorIdx)
    file = open(dirs[minErrorIdx + dynamicNumberIterations] + '/HeterogeneousParameter.csv','r')
    lines = file.readlines()
    file.close()
    heterogeneousParameter = np.zeros((len(heterogeneousParameter),len(heterogeneousParameter[0])))
    num = 0
    for line in lines:
        print("line : ", line)
        heterogeneousParameter[num] = [float(x) for x in line.split(',')]
        num += 1
    return heterogeneousParameter


if __name__ == '__main__':
    trueResult = [[100.0, 100.331, 100.884, 101.657, 102.32, 102.983, 103.425, 103.978, 104.53, 105.083, 105.635, 105.967, 105.967, 105.967, 105.967, 106.077, 106.188, 106.409, 106.63, 106.851, 107.072, 107.514, 107.845, 107.956], [100.0, 100.687, 101.604, 102.864, 103.895, 104.926, 105.613, 106.3, 107.216, 108.133, 108.935, 109.507, 109.851, 110.08, 110.309, 110.653, 110.882, 111.226, 111.569, 111.798, 112.027, 112.257, 112.6, 112.715], [100.0, 100.206, 100.514, 101.028, 101.336, 101.747, 101.953, 102.261, 102.569, 102.878, 103.289, 103.392, 103.392, 103.392, 103.289, 103.186, 103.186, 103.083, 102.98, 102.878, 102.878, 102.98, 103.083, 103.083], [100.0, 100.209, 100.626, 101.148, 101.566, 101.983, 102.192, 102.401, 102.818, 103.132, 103.445, 103.758, 103.862, 103.967, 104.071, 104.175, 104.175, 104.175, 104.175, 104.175, 104.28, 104.384, 104.593, 104.697], [24276.0, 27658.0, 41414.0, 44055.0, 39336.0, 36754.0, 37515.0, 32341.0, 29219.0, 36331.0, 31659.0, 26599.0, 18082.0, 17004.0, 22838.0, 25828.0, 30447.0, 33492.0, 38024.0, 36559.0, 33950.0, 40068.0, 35279.0, 28279.0], [31240.0, 38488.0, 44971.0, 35637.0, 32300.0, 34227.0, 32907.0, 32373.0, 27845.0, 34030.0, 32502.0, 34070.0, 27944.0, 38821.0, 36631.0, 31126.0, 31744.0, 30724.0, 31651.0, 36386.0, 32016.0, 37112.0, 36345.0, 35201.0], [33142.0, 30227.0, 37898.0, 39428.0, 35049.0, 35424.0, 36597.0, 30083.0, 27215.0, 33809.0, 33182.0, 29275.0, 21613.0, 21221.0, 26341.0, 29056.0, 25922.0, 25760.0, 25882.0, 27903.0, 27649.0, 34140.0, 33537.0, 30217.0], [20604.0, 23017.0, 26456.0, 21257.0, 19381.0, 21323.0, 21854.0, 20243.0, 17836.0, 21358.0, 20788.0, 22980.0, 20991.0, 26611.0, 25280.0, 22044.0, 22565.0, 21762.0, 20408.0, 21945.0, 18374.0, 21271.0, 22094.0, 22248.0]]
    dynamicParameter = findOptimalParameter('D:\Research\주택모델SIM모델\주택모델-buy0.5\PyMRDEVS_for calibration\MultiThreadWorkingPlace\Combined_Calibration_Results\Experiment_25',\
                                            trueResult, 3)
    print(dynamicParameter)