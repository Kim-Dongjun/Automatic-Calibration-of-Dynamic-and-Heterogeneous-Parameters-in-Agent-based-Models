import numpy as np
import csv

class postProcess():
    def __init__(self, hyperParameters):
        self.hyperParameters = hyperParameters

    def getDifferences(self, simResult, trueResult):
        # Postprocess trueValidationResult
        differences = np.zeros((self.hyperParameters.numCandidate,self.hyperParameters.numTimeStep,
                                self.hyperParameters.numOutputDim))
        for candidate in range(self.hyperParameters.numCandidate):
            differences[candidate] = simResult[candidate] - trueResult
        return differences

    def postProcessSimulationResult(self, simResultRaw):
        simResult = np.zeros((self.hyperParameters.numCandidate,self.hyperParameters.numTimeStep, self.hyperParameters.numOutputDim))#[[[0.0]*len(simResultRaw[0][0][0])]*len(simResultRaw[0][0])]*len(simResultRaw)
        simResultCov = np.zeros((self.hyperParameters.numCandidate,self.hyperParameters.numTimeStep,self.hyperParameters.numOutputDim, self.hyperParameters.numOutputDim))#[[[0.0] * len(simResultRaw[0][0][0])] * len(simResultRaw[0][0])] * len(simResultRaw)
        for candidate in range(self.hyperParameters.numCandidate):
            for time in range(self.hyperParameters.numTimeStep):
                simResult[candidate][time] = np.mean(simResultRaw[candidate][time],1)
                simResultCov[candidate][time] = np.cov(simResultRaw[candidate][time])
        return simResult, simResultCov

    def calculateSummaryStatistics(self, itrCalibration):
        fileCommonName = self.hyperParameters.dir + "iteration_" + str(itrCalibration) + "/TransactionNumber_candidate_"
        fileCommonIndexName = self.hyperParameters.dir + "iteration_" + str(itrCalibration) + "/PriceIndex_candidate_"
        simResult = np.zeros((self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep, self.hyperParameters.numOutputDim, self.hyperParameters.numReplication))
        for candidate in range(self.hyperParameters.numCandidate):
            transactions = self.calculateTransactions(fileCommonName + str(candidate) + "_replication_")
            prices = self.calculatePrices(fileCommonIndexName + str(candidate) + "_replication_")
            for time in range(self.hyperParameters.numTimeStep):
                simResult[candidate][time] = np.transpose(np.concatenate((prices[time], transactions[time]), axis=1))
        return simResult

    def calculatePrices(self, filename):
        prices = np.zeros((self.hyperParameters.numTimeStep, self.hyperParameters.numReplication, 4))
        idxs = [2,3,8,9]
        for rep in range(self.hyperParameters.numReplication):
            file = open(filename + str(rep) + ".csv", 'r')
            lines = file.readlines()
            file.close()
            for idx in range(len(idxs)):
                line = [float(x) for x in lines[idxs[idx]].split(',')[1:]]
                for time in range(self.hyperParameters.numTimeStep):
                    prices[time][rep][idx] = line[time]
        return prices

    def calculateTransactions(self, filename):
        totalHouseholds = 19560603
        transactions = np.zeros((self.hyperParameters.numTimeStep, self.hyperParameters.numReplication, 4))
        for rep in range(self.hyperParameters.numReplication):
            file = open(filename + str(rep) + ".csv", 'r')
            lines = file.readlines()
            file.close()
            for line in lines[1:]:
                line = line.split(',')
                line[-1] = line[-1][:-1]
                if line[9] == 'sale':
                    if line[5] == '2':
                        if line[4] == '0':
                            # Capital Apt Sale
                            transactions[int(line[0])-1][rep][0] += 1
                        else:
                            # NonCapital Apt Sale
                            transactions[int(line[0])-1][rep][2] += 1
                else:
                    if line[5] == '2':
                        if line[4] == '0':
                            # Capital Apt Rent
                            transactions[int(line[0])-1][rep][1] += 1
                        else:
                            # NonCapital Apt Rent
                            transactions[int(line[0])-1][rep][3] += 1
        transactions *= (totalHouseholds / float(self.hyperParameters.numAgents))
        return transactions