import os
import numpy as np
import sys

class initializingParameters():
    def __init__(self, hyperParameters):
        self.hyperParameters = hyperParameters
        self.dic = {}

    def initializeParameters(self):
        # In case of Real Estate Market ABM, we have the real-world observation data for validation
        # In case of a hypothesized Wealth Distribution ABM, we create a validation data
        # with a set of synthetically generated parameters
        print("initializing parameter values...")
        if self.hyperParameters.modelName == 'RealEstateMarketABM':
            file = open(os.getcwd() + '/SimulationModels/' + self.hyperParameters.modelName + '/InputParameters/DynamicParameters.csv', 'r')
            lines = file.readlines()
            file.close()
            flag = 0
            numEstParams = 3
            paramMin = [0.,0.,0.]
            paramMax = [0.05,0.012,0.01]
            dynamicParameter = np.zeros((numEstParams, self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))
            if self.hyperParameters.dynamicUpdate != 'randomSearch':
                for estParam in range(3):
                    for candidate in range(self.hyperParameters.numCandidate):
                        temp = np.random.random()
                        for time in range(self.hyperParameters.numTimeStep):
                            if estParam in self.hyperParameters.dynParamList:
                                dynamicParameter[estParam][candidate][time] = temp
                            else:
                                if estParam == 0:
                                    if time == 0:
                                        dynamicParameter[0][candidate][time] = 1.
                                    if time in range(1, 3):
                                        dynamicParameter[0][candidate][time] = 0.8
                                    elif time in range(3, 6):
                                        dynamicParameter[0][candidate][time] = 0.5
                                    elif time in range(6, 12):
                                        dynamicParameter[0][candidate][time] = 0.4
                                    else:
                                        dynamicParameter[0][candidate][time] = 0.4
                                elif estParam == 1:
                                    dynamicParameter[estParam][candidate][time] = 0.3
                                elif estParam == 2:
                                    if time in range(4):
                                        dynamicParameter[estParam][candidate][time] = 0.3
                                    elif time in range(5, 12):
                                        dynamicParameter[estParam][candidate][time] = 0.0
                                    else:
                                        dynamicParameter[estParam][candidate][time] = 0.3
            elif self.hyperParameters.dynamicUpdate == 'randomSearch':
                for estParam in range(numEstParams):
                    for candidate in range(self.hyperParameters.numCandidate):
                        for time in range(self.hyperParameters.numTimeStep):
                            dynamicParameter[estParam][candidate][time] = np.random.random()
            heterogeneousParameter = [[0.7], [0.9]]
            paramMin = paramMin + [0.3,0.3]
            paramMax = paramMax + [0.9,0.9]
        elif self.hyperParameters.modelName == 'WealthDistributionABM':
            dynamicParameter = [0.75]
            regime1 = [x for x in range(10)] + [x for x in range(20, 30)] + [x for x in range(40, 50)]
            regime2 = [x for x in range(10, 20)] + [x for x in range(30, 40)]
            for time in range(self.hyperParameters.numTimeStep):
                if time in regime1:
                    dynamicParameter.append(0.75)
                else:
                    dynamicParameter.append(0.25)
            dynamicParameter = np.tile(np.array(dynamicParameter), self.hyperParameters.numCandidate).reshape(1,-1,self.hyperParameters.numTimeStep+1)
            heterogeneousParameter = [[0.9,0.1]]
            paramMin = [0, 0]
            paramMax = [2, 1]
        dynamicParameter = np.array(dynamicParameter)
        heterogeneousParameter = np.array(heterogeneousParameter)
        self.dic['dynamicParameter'] = dynamicParameter
        self.dic['heterogeneousParameter'] = heterogeneousParameter
        paramMin = np.array(paramMin)
        paramMax = np.array(paramMax)
        dynParamMin = np.transpose(np.tile(paramMin[:dynamicParameter.shape[0]], int(dynamicParameter.shape[1] * dynamicParameter.shape[2]))\
            .reshape(-1,dynamicParameter.shape[0])).reshape(dynamicParameter.shape[0],self.hyperParameters.numCandidate,-1)
        dynParamMax = np.transpose(np.tile(paramMax[:dynamicParameter.shape[0]], int(dynamicParameter.shape[1] * dynamicParameter.shape[2]))\
            .reshape(-1,dynamicParameter.shape[0])).reshape(dynamicParameter.shape[0],self.hyperParameters.numCandidate,-1)
        hetParamMin = np.tile(paramMin[dynamicParameter.shape[0]:], heterogeneousParameter.shape[1])\
            .reshape(heterogeneousParameter.shape[0],-1)
        hetParamMax = np.tile(paramMax[dynamicParameter.shape[0]:], heterogeneousParameter.shape[1]) \
            .reshape(heterogeneousParameter.shape[0], -1)
        self.dic['dynParamMin'] = dynParamMin
        self.dic['dynParamMax'] = dynParamMax
        self.dic['hetParamMin'] = hetParamMin
        self.dic['hetParamMax'] = hetParamMax

        return self.dic

    def initializeHeterogeneousParameters(self, dicParams, agentClusters):
        print("initializing heterogeneous parameters...")
        if agentClusters != []:
            numClusters = max(agentClusters) + 1
            hetParam = np.random.uniform(0,1,(dicParams['heterogeneousParameter'].shape[0],numClusters))
            dicParams['heterogeneousParameter'] = hetParam
            dicParams['hetParamMin'] = np.tile(dicParams['hetParamMin'],numClusters).reshape(hetParam.shape[0],numClusters)
            dicParams['hetParamMax'] = np.tile(dicParams['hetParamMax'], numClusters).reshape(hetParam.shape[0], numClusters)
        return dicParams