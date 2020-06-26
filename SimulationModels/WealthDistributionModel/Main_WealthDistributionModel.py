#-*- coding:utf-8 -*-

from SimulationModels.WealthDistributionModel.SimulationEngine.SimulationEngine import SimulationEngine
from SimulationModels.WealthDistributionModel.SimulationEngine.Utility.Configurator import Configurator

from SimulationModels.WealthDistributionModel.WealthDistribution import WealthDistribution
import numpy as np
import random
import sys
from multiprocessing import Process
import csv
import os

def Model(hyperParameters, itrCalibration, currentThread, dynamicParameter, heterogeneousParameter, agentClusters = [], microResults = False):

    objConfiguration = Configurator()
    objConfiguration.addConfiguration("numAgentHouseHold", hyperParameters.numAgents)
    objConfiguration.addConfiguration("numGridX", hyperParameters.numGridX)
    objConfiguration.addConfiguration("numGridY", hyperParameters.numGridY)
    objConfiguration.addConfiguration("candidate", currentThread // hyperParameters.numReplication)
    objConfiguration.addConfiguration("itrCalibration", itrCalibration)
    objConfiguration.addConfiguration("simulationNumber", currentThread)
    objModel = WealthDistribution(objConfiguration, dynamicParameter, heterogeneousParameter, hyperParameters.dir)
    engine = SimulationEngine()
    engine.setOutmostModel(objModel) # every children model saved in self.models -> Make the structure of ENGINE to be same as the structure of DEVS Model
    Low1, Middle1, High1, Gini1 = engine.run(maxTime=hyperParameters.numTimeStep, \
               logFileName='log.txt', \
               visualizer=False, \
               logGeneral=False, \
               logActivateState=False, \
               logActivateMessage=False, \
               logActivateTA=False, \
               logStructure=False, \
               directory = hyperParameters.dir, \
             itrCalibration = itrCalibration, \
               ) # After Initialize, Run Single Step for maxTime

    if not os.path.exists(hyperParameters.dir + "iteration_" + str(itrCalibration)):
        os.makedirs(hyperParameters.dir + "iteration_" + str(itrCalibration))

    if not os.path.exists(
            hyperParameters.dir + "iteration_" + str(itrCalibration) + '/SimulationResult_candidate_' + str(
                    objConfiguration.getConfiguration("candidate")) + '_replication_' + str(currentThread % hyperParameters.numReplication) + '.csv'):
        writeType = 'w'
    else:
        writeType = 'a'
    file = open(hyperParameters.dir + "iteration_" + str(itrCalibration) + '/SimulationResult_candidate_' + str(
        objConfiguration.getConfiguration("candidate")) + '_replication_' + str(currentThread % hyperParameters.numReplication) + '.csv', writeType, newline='')
    writer = csv.writer(file)
    writer.writerow(Low1)
    writer.writerow(Middle1)
    writer.writerow(High1)
    writer.writerow(Gini1)
    file.flush()
    file.close()

    print(str(currentThread) + "-th Simulation End!")

if __name__ == '__main__':
    random.seed(0)
    np.random.seed(0)
    numCandidate = 1
    numReplication = 1
    numTimeStep = 20
    numAgent = 2
    numGridX = 3
    numGridY = 3
    Dynamic = False
    Agent_Specific = True
    dir = './ExampleCSV/'
    Low, Middle, High, Gini = Wealth_Model(numCandidate, numReplication, numTimeStep + 1,
                                                 numAgent, numGridX, numGridY, Dynamic,
                                                 Agent_Specific, dir)
    print(Low)