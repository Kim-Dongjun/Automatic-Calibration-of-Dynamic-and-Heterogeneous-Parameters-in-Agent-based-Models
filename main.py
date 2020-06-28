from SimulationModels.simulator import simulation
from OptimizerModels.Optimizer import optimizer
from OptimizerModels.InitializingParameters import initializingParameters
from OptimizerModels.findOptimalParameter import findOptimalParameter
from OptimizerModels.HeterogeneousCalibration.AgentClustering import agentCluster
import OptimizerModels.getObservation as getObs

import sys
import os
import argparse

class CalibrationFramework():
    def __init__(self, simulation_name, outputDim, numAgents, numTimeStep, experiment, dynParamList, hetParamList,
                 dynIters, hetIters, numTotalIters):
        # Arguments for the Algorithm
        parser = argparse.ArgumentParser()

        # Simulation Model Hyperparameters
        parser.add_argument("--modelName", type=str, default=str(simulation_name), help="Simulation model")
        parser.add_argument("--numAgents", type=int, default=int(numAgents), help="number of agents")
        parser.add_argument("--numGridX", type=int, default=int(10), help="number of grid in X coordinate")
        parser.add_argument("--numGridY", type=int, default=int(10), help="number of grid in Y coordinate")
        parser.add_argument("--numTimeStep", type=int, default=int(numTimeStep), help="number of simulation time step")

        # Experimental Design Hyperparameters
        parser.add_argument("--experiment", type=str, default=str(experiment), help="number of simulation time step")
        parser.add_argument("--calibrationIterations", type=int, default=int(numTotalIters),
                            help="number of calibration iterations")
        parser.add_argument("--dynIters", type=int, default=int(dynIters),
                            help="number of consecutive dynamic calibration")
        parser.add_argument("--hetIters", type=int, default=int(hetIters),
                            help="number of consecutive heterogeneous calibration")
        parser.add_argument("--numCandidate", type=int, default=int(3), help="number of candidate hypotheses (I)")
        parser.add_argument("--numReplication", type=int, default=int(5), help="number of simulation replications (J)")
        parser.add_argument("--numThread", type=int, default=int(15), help="number of threads in parallel simulation")

        # Calibration Target Parameters
        parser.add_argument("--dynParamList", type=list, default=dynParamList, help="Calibration dynamic parameter lists")
        parser.add_argument("--hetParamList", type=list, default=hetParamList, help="Calibration heterogeneous parameter lists")

        # Simulation Output Dimensions on interest
        parser.add_argument("--outputDim", type=list, default=outputDim,
                            help="validation-level output dimension to fit with real-world observation")
        if simulation_name == 'WealthDistributionABM':
            parser.add_argument("--numOutputDim", type=int, default=int(len(outputDim)),
                                help="number of validation-level output dimension")
        elif simulation_name == 'RealEstateMarketABM':
            parser.add_argument("--numOutputDim", type=int, default=int(2 * len(outputDim)),
                                help="number of validation-level output dimension")
        parser.add_argument("--dimAgentLevelStates", type=int, default=int(12),
                            help="dimension of agent-level states used in clustering")

        # Dynamic Calibration Hyperparameters
        parser.add_argument("--HMMClusters", type=int, default=int(3),
                            help="number of temporal clusters in HMMM")
        if experiment == 'random':
            parser.add_argument("--dynamicUpdate", type=str, default='randomSearch',
                                help="dynamic parameter update method")
        elif experiment == 'dynamic':
            #parser.add_argument("--dynamicUpdate", type=str, default='samplingByTime',
            #                    help="dynamic parameter update method")
            parser.add_argument("--dynamicUpdate", type=str, default='samplingByRegime',
                                help="dynamic parameter update method")
            #parser.add_argument("--dynamicUpdate", type=str, default='ModeSelection',
            # help="dynamic parameter update method")
        elif experiment == 'heterogeneous':
            parser.add_argument("--dynamicUpdate", type=str, default='noDynamicUpdate',
                                help="dynamic parameter update method")
        elif experiment == 'framework':
            parser.add_argument("--dynamicUpdate", type=str, default='ModeSelection',
                                help="dynamic parameter update method")
        else:
            print("check experiment again")
            sys.exit()

        # Heterogeneous Calibration Hyperparameters
        parser.add_argument("--dimLatent", type=int, default=int(100),
                            help="number of threads in parallel simulation")
        parser.add_argument("--epochVAE", type=int, default=int(2000),
                            help="epochs to train VAE")
        parser.add_argument("--learningRateVAE", type=float, default=float(0.001),
                            help="learning rate of VAE")
        parser.add_argument("--clusteringAlgorithm", type=str, default='GMM',
                            help="clustering algorithm")
        parser.add_argument("--numberOfClusters", type=int, default=int(8),
                            help="number of clusters (K^{k})")
        parser.add_argument("--randomIterations", type=int, default=int(3),
                            help="random sampling for the very first of calibration")
        parser.add_argument("--randomRatio", type=float, default=float(0.15),
                            help="random sampling ratio")
        parser.add_argument("--fullExplorationRatio", type=float, default=float(0.2),
                            help="full exploration ratio")
        parser.add_argument("--fullExploitationRatio", type=float, default=float(0.05),
                            help="full exploitation ratio")

        # Working Directory
        dir = os.path.abspath(os.path.join('.', os.pardir)) + '/FirstArticleExperimentalResults/'\
              + str(experiment) + '/'
        if not os.path.exists(dir):
            os.makedirs(dir)
        experiment_duplication = len(os.listdir(dir))
        dir = dir + 'Experiments_' + str(experiment_duplication) + '/'
        parser.add_argument("--dir", type=str, default=dir, help="directory path")
        self.hyperParams = parser.parse_args()

    def setup(self):
        self.initParams = initializingParameters(self.hyperParams)
        self.dicParams = self.initParams.initializeParameters()
        self.trueObservation = getObs.getValidation(self.hyperParams, self.dicParams)
        self.agentCluster = agentCluster(self.dicParams, self.hyperParams)
        self.agentClusters, _ = self.agentCluster.agentClustering(self.hyperParams.clusteringAlgorithm,
                                                             self.hyperParams.numberOfClusters)
        self.simulator = simulation(self.hyperParams, self.agentClusters)
        self.dicParams = self.initParams.initializeHeterogeneousParameters(self.dicParams, self.agentClusters)
        self.optimizer = optimizer(self.hyperParams, self.trueObservation)
        self.findOptimalParameter = findOptimalParameter()

    def calibrate(self):
        self.setup()
        for itr in range(self.hyperParams.calibrationIterations):
            print("----------------------------------------------------")
            print("------------------------ Calibration Iteration " + str(itr) + " --------------------------")
            print("----------------------------------------------------")
            resultAverage, resultCov = self.simulator.runParallelSimulation(itr, self.dicParams)
            self.dicParams = self.optimizer.getNewParams(self.dicParams, resultAverage, resultCov, itr)
        return self.findOptimalParameter.findOptimalParameter()

if __name__ == '__main__':
    # Simulation Model for Experiment
    print("Wealth Distribution ABM -> 1")
    print("Real Estate Market ABM -> 2")
    simulation_name = input("Which agent-based model do you want to use : ")
    simulation_name = int(simulation_name)
    # Ask Basic Setting
    print("Random Search -> enter 1")
    print("Dynamic Calibration -> enter 2")
    print("Heterogeneous Calibration -> enter 3")
    print("Calibration framework -> enter 4")
    experiment = input("Which experiment do you want : ")
    experiment = int(experiment)
    print("List all the calibration parameters")
    done = False
    # dynamic calibration consecutive iterations
    dynIters = 0
    # heterogeneous calibration consecutive iterations
    hetIters = 0
    # Number of total iterations for calibration
    numTotalIters = input("Input the number of total calibration iterations : ")
    numTotalIters = int(numTotalIters)

    # The list of calibration dynamic parameters: dynParamList
    # The list of calibration heterogeneous parameters: hetParamList
    if experiment == 1:
        experiment = 'random'
        dynParamList = [0,1,2]
        hetParamList = [0,1]
    if experiment == 2:
        dynIters = input("Dynamic calibration consecutive iteration numbers : ")
        dynIters = int(dynIters)
        experiment = 'dynamic'
        dynParamList = []
        while not done:
            param = input("input which dynamic parameter to calibrate (e.g. if you want to calibrate the first"
                          " and the second dynamic parameters, first input 0 and input 1 consecutively,"
                          " and put 'done') : ")
            try:
                dynParamList.append(int(param))
            except:
                print("you have input 'param' as " + str(param))
                done = True
        if dynParamList == []:
            dynParamList = [0,1,2]
        hetParamList = []
    elif experiment == 3:
        hetIters = input("Heterogeneous calibration consecutive iteration numbers : ")
        hetIters = int(hetIters)
        experiment = 'heterogeneous'
        dynParamList = []
        hetParamList = []
        while not done:
            print("if you want to calibrate all 2 heterogeneous parameters, then put 'done'")
            param = input("input which heterogeneous parameter to calibrate (e.g. if you want to calibrate the first"
                          " and the second heterogeneous parameters, first input 0 and input 1 consecutively,"
                          " and put 'done') : ")
            try:
                hetParamList.append(int(param))
            except:
                print("you have input 'param' as " + str(param))
                done = True
        if hetParamList == []:
            hetParamList = [0,1]
    elif experiment == 4:
        dynIters = input("Dynamic calibration consecutive iteration numbers : ")
        dynIters = int(dynIters)
        hetIters = input("Heterogeneous calibration consecutive iteration numbers : ")
        hetIters = int(hetIters)
        experiment = 'framework'
        dynParamList = [0,1,2]
        hetParamList = [0,1]
    if simulation_name == 1:
        numAgents = 100
        numTimeStep = 50
        simulation_name = 'WealthDistributionABM'
        outputDim = [0,1,2,3]
    elif simulation_name == 2:
        numAgents = 10000
        numTimeStep = 24
        simulation_name = 'RealEstateMarketABM'
        outputDim = [2,3,8,9]

    calibration = CalibrationFramework(simulation_name, outputDim, numAgents, numTimeStep, experiment, dynParamList,
                                       hetParamList, dynIters, hetIters,
                                       numTotalIters)
    calibratedParameter = calibration.calibrate()