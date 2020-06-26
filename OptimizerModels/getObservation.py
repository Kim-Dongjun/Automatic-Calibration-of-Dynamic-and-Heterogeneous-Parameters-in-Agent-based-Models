from SimulationModels.simulator import simulation

import os
import numpy as np

def getValidation(hyperParameters, dicParams):
    print("get validation data...")
    if hyperParameters.modelName == 'RealEstateMarketABM':
        file = open(os.getcwd() + '/SimulationModels/'+str(hyperParameters.modelName)+'/Validation/real_validation_data.csv','r')
        lines = file.readlines()
        file.close()
        validation = []
        for line in lines:
            validation.append(line.split(','))
        validation.pop(1)
        validation = np.transpose(validation)
        trueResult = np.zeros((hyperParameters.numTimeStep, hyperParameters.numOutputDim))
        for summaryStatistics in range(len(hyperParameters.outputDim)):
            for time in range(hyperParameters.numTimeStep):
                trueResult[time][summaryStatistics] = float(validation[2+hyperParameters.outputDim[summaryStatistics]][1+time])
        for summaryStatistics in range(len(hyperParameters.outputDim)):
            for time in range(hyperParameters.numTimeStep):
                trueResult[time][4+summaryStatistics] = float(validation[14 + hyperParameters.outputDim[summaryStatistics]][1+time])
    elif hyperParameters.modelName == 'WealthDistributionABM':
        simulator = simulation(hyperParameters, [])
        trueResult, _ = simulator.runParallelSimulation(-1, dicParams)
        trueResult = np.mean(trueResult, 0)
    return np.array(trueResult)