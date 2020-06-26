import numpy as np

class postProcess():
    def __init__(self, hyperParameters):
        self.hyperParameters = hyperParameters

    def getDifferences(self, simResult, trueResult):
        # Postprocess trueValidationResult
        if len(trueResult[0]) != len(simResult[0][0]):
            for dimension in range(len(trueResult)):
                trueResult[dimension] = trueResult[dimension][:len(simResult[0][0])]

        # get Difference
        differences = np.zeros((len(simResult),len(simResult[0]),len(simResult[0][0])))#[[[0]*len(simResult[0][0])]*len(simResult[0])]*len(simResult)
        for candidate in range(len(simResult)):
            for resultDim in range(len(simResult[0])):
                for time in range(len(simResult[0][0])):
                    differences[candidate][resultDim][time] = simResult[candidate][resultDim][time] - trueResult[resultDim][time]
        return differences

    def readCandidateReplicationFile(self, itrCalibration):
        Low = []
        Middle = []
        High = []
        Gini = []
        for candidate in range(self.hyperParameters.numCandidate):
            Low_temp = []
            Middle_temp = []
            High_temp = []
            Gini_temp = []
            for replication in range(self.hyperParameters.numReplication):
                try:
                    file = open(self.hyperParameters.dir + "iteration_" + str(itrCalibration) + '/SimulationResult_candidate_' + str(
                        candidate) + '_replication_' + str(replication) + '.csv' ,'r')
                    lines = file.readlines()
                    file.close()
                    Low_temp.append([float(x) for x in lines[0].split(',')])
                    Middle_temp.append([float(x) for x in lines[1].split(',')])
                    High_temp.append([float(x) for x in lines[2].split(',')])
                    Gini_temp.append([float(x) for x in lines[3].split(',')])
                except:
                    pass
            Low.append(Low_temp)
            Middle.append(Middle_temp)
            High.append(High_temp)
            Gini.append(Gini_temp)
        return [Low, Middle, High, Gini]

    def postProcessSimulationResult(self, simResultRaw):
        simResult = []
        simResultCov = []
        Low_avg, Low_std = mean(simResultRaw[0])  # Shape(output) = numTimeStep * numCandidate
        Middle_avg, Middle_std = mean(simResultRaw[1])
        High_avg, High_std = mean(simResultRaw[2])
        Gini_avg, Gini_std = mean(simResultRaw[3])
        simResult.append(Low_avg)  # Shape(self.simResult) = 4 * numTimeStep * numCandidate
        simResult.append(Middle_avg)
        simResult.append(High_avg)
        simResult.append(Gini_avg)
        simResultCov.append(Low_std)
        simResultCov.append(Middle_std)
        simResultCov.append(High_std)
        simResultCov.append(Gini_std)
        simResult = np.transpose(np.array(simResult), [2, 0, 1])  # [2,0,1], [1,0,2], [1,2,0], [0,2,1], [2,1,0]
        simResultCov = np.transpose(np.array(simResultCov), [2, 0, 1])
        return simResult, simResultCov

    def mean(self, list):
        temp_list = []
        cov_list = []
        for candidate in range(len(list)):
            temp_mean = []
            temp_cov = []
            for time in range(len(list[0][0])):
                temp = []
                for replication in range(len(list[0])):
                    temp.append(list[candidate][replication][time])
                temp_mean.append(np.mean(temp))
                temp_cov.append(np.sqrt(np.cov(temp)))
            temp_list.append(temp_mean)
            cov_list.append(temp_cov)
        temp_list = np.transpose(temp_list).tolist()
        cov_list = np.transpose(cov_list).tolist()
        return temp_list[1:], cov_list[1:]