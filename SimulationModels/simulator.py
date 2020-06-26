from multiprocessing import Process
import SimulationModels.RealEstateMarketABM.Main_RealEstateMarketABM as RealEstateMarketModel
import SimulationModels.RealEstateMarketABM.postProcessSimulationResult as RealEstateMarketModelPost
import SimulationModels.WealthDistributionModel.Main_WealthDistributionModel as WealthDistributionModel
import SimulationModels.WealthDistributionModel.postProcessSimulationResult as WealthDistributionModelPost

class simulation():
    def __init__(self, hyperParams, agentClusters):
        self.hyperParams = hyperParams
        self.agentClusters = agentClusters
        if agentClusters == []:
            self.microResults = True
        else:
            self.microResults = False
        if self.hyperParams.modelName == 'WealthDistributionABM':
            self.Model = WealthDistributionModel
            self.post = WealthDistributionModelPost.postProcess(hyperParams)
        if self.hyperParams.modelName == 'RealEstateMarketABM':
            self.Model = RealEstateMarketModel
            self.post = RealEstateMarketModelPost.postProcess(hyperParams)


    def runParallelSimulation(self, itrCalibration, dicParams):
        currentThread = 0
        dynParam = dicParams['dynParamMin'] + dicParams['dynamicParameter'] \
                   * (dicParams['dynParamMax'] - dicParams['dynParamMin'])
        hetParam = dicParams['hetParamMin'] + dicParams['heterogeneousParameter']\
                   * (dicParams['hetParamMax'] - dicParams['hetParamMin'])

        totalSimulationExecution = self.hyperParams.numCandidate * self.hyperParams.numReplication

        while (currentThread < totalSimulationExecution):
            procs = []
            for proc in range(self.hyperParams.numThread):
                if currentThread < totalSimulationExecution:
                    pr = Process(target=self.Model.Model, args=(self.hyperParams, itrCalibration, currentThread, dynParam,
                                                           hetParam, self.agentClusters, self.microResults))
                    procs.append(pr)
                currentThread += 1

            for t in procs:
                t.start()
            for t in procs:
                t.join()

        simResultRaw = self.post.calculateSummaryStatistics(itrCalibration)
        simResult, simResultCov = self.post.postProcessSimulationResult(simResultRaw)

        return simResult, simResultCov