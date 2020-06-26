import os
import numpy as np

def readMicroResult(hyperparameters):
    normalizedSimMicroResultRaw = np.zeros((hyperparameters.numAgents, hyperparameters.numTimeStep * hyperparameters.dimAgentLevelStates))
    for replication in range(hyperparameters.numReplication):
        file = open(hyperparameters.dir + "MicroResults/MicroLog_" + str(replication) + ".csv", 'r')
        lines = file.readlines()
        AttributeValues = np.zeros((3,hyperparameters.numAgents * hyperparameters.numTimeStep))
        print(replication, len(lines))
        for i in range(len(lines)-1):
            line = lines[i+1].split(',')
            AttributeValues[0][i] = float(line[3])
            AttributeValues[1][i] = float(line[4])
            AttributeValues[2][i] = float(line[5])
        maxAttributeValues = np.zeros(3)
        maxAttributeValues[0] = np.max(AttributeValues[0])
        maxAttributeValues[1] = np.max(AttributeValues[1])
        maxAttributeValues[2] = np.max(AttributeValues[2])
        for line in lines[1:]:
            line = line.split(',')
            normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + 0] += int(float(line[0 + 2])) / float(hyperparameters.numReplication)
            for attribute in range(3):
                normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + attribute + 1] += int(float(line[attribute + 3])) / (float(hyperparameters.numReplication) * maxAttributeValues[attribute])
                #normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + attribute + 1] += int(float(line[attribute + 3])) / float(numReplication)
                #normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + attribute].append(int(float(line[attribute + 2])))
            normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + 3 + int(line[6])] += 1 / float(hyperparameters.numReplication)
            #normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + 3 + int(line[6])].append(1)
            normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + 7 + int(line[7])] += 1 / float(hyperparameters.numReplication)
            #normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + 7 + int(line[7])].append(1)
            # saving이 minus value가 될 수 있나?
            normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + 11] += int(line[8]) / float(hyperparameters.numReplication)
            #normalizedSimMicroResultRaw[int(line[1])][12 * int(line[0]) + 11].append(int(line[8]))
        file.close()
    #for agent in range(len(normalizedSimMicroResultRaw)):
    #    for dim in range(len(normalizedSimMicroResultRaw[0])):
    #        simMicroResult[agent][dim] = np.mean(normalizedSimMicroResultRaw[agent][dim])
    #        simMicroResultCov[agent][dim] = np.sqrt(np.cov(normalizedSimMicroResultRaw[agent][dim]))
    #return simMicroResult, simMicroResultCov
    return normalizedSimMicroResultRaw