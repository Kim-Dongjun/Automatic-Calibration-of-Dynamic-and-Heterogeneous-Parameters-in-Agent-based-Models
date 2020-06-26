from SimulationModels.RealEstateMarketABM.SimulationEngine.SimulationEngine import SimulationEngine
from SimulationModels.RealEstateMarketABM.SimulationEngine.Utility.Configurator import Configurator
import SimulationModels.RealEstateMarketABM.calculateJevonsIndex as ji
from SimulationModels.RealEstateMarketABM.RealEstateMarketModel import HousingMarketModel
import csv
import numpy as np
from time import sleep
import time
import os
import sys

def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator

# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds.\n" %tempTimeInterval )

def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)


def Model(hyperParameters, itrCalibration, currentThread, dynamicParameter, heterogeneousParameter, agentClusters,
          microResults=False):
    #simResultRaw = []
    #simMicroResultRaw = []
    number = 0
    objConfiguration = Configurator()

    # setting static variables
    staticVariableFilename = os.path.dirname(os.path.abspath(__file__)) + '/InputData/Static_variable_rawdata_2015.csv'
    with open(staticVariableFilename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            elif line_count == 1:
                rawData = np.array(row[1])
                line_count += 1
            else:
                rawData = np.vstack([rawData, row[1]])
                line_count += 1

    objConfiguration.addConfiguration("running_folder", hyperParameters.dir)
    objConfiguration.addConfiguration("itrCalibration", int(itrCalibration))
    if not os.path.exists(hyperParameters.dir + 'iteration_' + str(itrCalibration)):
        os.makedirs(hyperParameters.dir + 'iteration_' + str(itrCalibration))
    objConfiguration.addConfiguration("microResults", microResults)
    objConfiguration.addConfiguration("numAgentHousehold", hyperParameters.numAgents)
    objConfiguration.addConfiguration("simTime", hyperParameters.numTimeStep)
    objConfiguration.addConfiguration("mortLoanMaturity", int(rawData[2]))
    objConfiguration.addConfiguration("creditLoanMaturity", int(rawData[3]))
    objConfiguration.addConfiguration("capitalHouseSupplyRatio", float(rawData[4]))
    objConfiguration.addConfiguration("nonCapitalHouseSupplyRatio", float(rawData[5]))
    # objConfiguration.addConfiguration("mp_ir", float(rawData[6]))
    # objConfiguration.addConfiguration("mp_dr", float(rawData[7]))
    objConfiguration.addConfiguration("moveProbability", float(rawData[8]))
    # objConfiguration.addConfiguration("wtp", float(rawData[9]))
    # objConfiguration.addConfiguration("saleProb", float(rawData[10]))
    # objConfiguration.addConfiguration("participateRate", float(rawData[11]))
    objConfiguration.addConfiguration("consumptionRate1", float(rawData[12]))
    objConfiguration.addConfiguration("consumptionRate2", float(rawData[13]))
    objConfiguration.addConfiguration("consumptionRate3", float(rawData[14]))
    objConfiguration.addConfiguration("consumptionRate4", float(rawData[15]))
    objConfiguration.addConfiguration("consumptionRate5", float(rawData[16]))
    objConfiguration.addConfiguration("priorityThreshold", float(rawData[17]))
    objConfiguration.addConfiguration("agentClusters", agentClusters)
    objConfiguration.addConfiguration("HouseMarketSalePrices", [])
    objConfiguration.addConfiguration("HouseMarketRentPrices", [])
    objConfiguration.addConfiguration("HouseRegions", [])
    objConfiguration.addConfiguration("HouseTypes", [])
    objConfiguration.addConfiguration("dynParamList", hyperParameters.dynParamList)
    objConfiguration.addConfiguration("hetParamList", hyperParameters.hetParamList)
    objConfiguration.addConfiguration("calibrationType", hyperParameters.experiment)
    objConfiguration.addConfiguration("typePriority", [None, None, None])

    # setting dynamic variables
    dynamicVariableFilename = os.path.dirname(os.path.abspath(__file__)) + '/InputData/Dynamic_variable_rawdata_2015.csv'
    with open(dynamicVariableFilename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            elif line_count == 1:
                rawData2 = np.array(row)
                line_count += 1
            else:
                rawData2 = np.vstack([rawData2, row])
                line_count += 1
    rawData2 = np.transpose(rawData2)
    objConfiguration.addConfiguration("interestRate", rawData2[1])
    objConfiguration.addConfiguration("inflationRate", rawData2[2])
    objConfiguration.addConfiguration("jeonseExchangeRate", rawData2[3])
    objConfiguration.addConfiguration("depositRentfeeExchangeRate", rawData2[4])
    objConfiguration.addConfiguration("creditLoanInterestRate", rawData2[5])
    objConfiguration.addConfiguration("mortLoanInterestRate", rawData2[6])
    objConfiguration.addConfiguration("fixedInterestRateSpread", rawData2[7])
    objConfiguration.addConfiguration("houseTypeRatio1", rawData2[8])
    objConfiguration.addConfiguration("houseTypeRatio2", rawData2[9])
    objConfiguration.addConfiguration("houseTypeRatio3", rawData2[10])
    objConfiguration.addConfiguration("houseTypePrice1", rawData2[11])
    objConfiguration.addConfiguration("houseTypePrice2", rawData2[12])
    objConfiguration.addConfiguration("houseTypePrice3", rawData2[13])
    objConfiguration.addConfiguration("capitalMoveRate", rawData2[14])
    objConfiguration.addConfiguration("nonCapitalMoveRate", rawData2[15])
    objConfiguration.addConfiguration("LTV", rawData2[16])
    objConfiguration.addConfiguration("DTI", rawData2[17])

    # Simulation Parameter Setting
    currentCandidate = currentThread // hyperParameters.numReplication
    currentReplication = currentThread % hyperParameters.numReplication
    objConfiguration.addConfiguration("currentCandidate", currentCandidate)
    objConfiguration.addConfiguration("currentReplication", currentReplication)

    # Simulation Parameter Values
    objConfiguration.addConfiguration("participateRate", dynamicParameter[0][currentCandidate])
    objConfiguration.addConfiguration("mp_ir", dynamicParameter[1][currentCandidate])
    objConfiguration.addConfiguration("mp_dr", dynamicParameter[2][currentCandidate])
    objConfiguration.addConfiguration("wtp", heterogeneousParameter[0])
    objConfiguration.addConfiguration("saleProb", heterogeneousParameter[1])

    if not os.path.exists(hyperParameters.dir + 'iteration_' + str(itrCalibration) +
                          '/DynamicParameter_Candidate_' + str(currentCandidate) + '.csv'):
        file = open(hyperParameters.dir + 'iteration_' + str(itrCalibration) +
                    '/DynamicParameter_Candidate_' + str(currentCandidate) + '.csv','w', newline='')
        writer = csv.writer(file)
        writer.writerow(["Market Participation Rate"]+dynamicParameter[0][currentCandidate].tolist())
        writer.writerow(["Market Price Increase Rate"]+dynamicParameter[1][currentCandidate].tolist())
        writer.writerow(["Market Price Decrease Rate"]+dynamicParameter[2][currentCandidate].tolist())
        file.close()
    if not os.path.exists(hyperParameters.dir + 'iteration_' + str(itrCalibration) +
                          '/HeterogeneousParameter_Candidate_' + str(currentCandidate) + '.csv'):
        file = open(hyperParameters.dir + 'iteration_' + str(itrCalibration) +
                    '/HeterogeneousParameter.csv', 'w', newline='')
        writer = csv.writer(file)
        writer.writerow(['Willing to Pay']+heterogeneousParameter[0].tolist())
        writer.writerow(['Purchase Rate']+heterogeneousParameter[1].tolist())
        file.close()

    objConfiguration.addConfiguration("simulationNumber", currentThread)
    objConfiguration.addConfiguration("time", 0)
    print(str(currentThread) + "-th Simulation Start!")

    objModel = HousingMarketModel(objConfiguration)
    #print("시뮬레이션 초기화")
    engine = SimulationEngine()
    engine.setOutmostModel(objModel)
    engine.run(maxTime=99999, \
               logFileName='log.txt', \
               visualizer=False, \
               logGeneral=False, \
               logActivateState=False, \
               logActivateMessage=False, \
               logActivateTA=False, \
               logStructure=False \
               )
    print(str(currentThread) + "-th Simulation End!")
    if objConfiguration.getConfiguration("microResults") == True:
        objModel.objOperator.objLogHouseHold.close()
    objModel.objHousingMarket.objRealtor.objLogFile.close()
    number += 1

    #print("--------------------------------------------")
    #print("Market Prices : ", objConfiguration.getConfiguration("HouseMarketPrices"))
    #print("--------------------------------------------")
    
    ji.calculateJevonsIndex(hyperParameters.dir + 'iteration_' + str(itrCalibration), currentCandidate,
                            currentReplication, hyperParameters.numReplication,
                            objConfiguration.getConfiguration("HouseMarketSalePrices"),
                            objConfiguration.getConfiguration("HouseMarketRentPrices"),
                            objConfiguration.getConfiguration("HouseRegions"),
                            objConfiguration.getConfiguration("HouseTypes"))

    sys.stdout.flush()
    if itrCalibration == 0:
        simMicroResultRaw = []
    else:
        simMicroResultRaw = []

    return int(rawData[0])

if __name__ == '__main__':
    tic()
    objConfiguration = Configurator()

    # setting static variables
    staticVariableFilename = 'InputData/Static_variable_rawdata_2015.csv'
    with open(staticVariableFilename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            elif line_count == 1:
                rawData = np.array(row[1])
                line_count += 1
            else:
                rawData = np.vstack([rawData, row[1]])
                line_count += 1

    objConfiguration.addConfiguration("numAgentHousehold", int(rawData[0]))
    objConfiguration.addConfiguration("simTime", int(rawData[1]))
    objConfiguration.addConfiguration("mortLoanMaturity", int(rawData[2]))
    objConfiguration.addConfiguration("creditLoanMaturity", int(rawData[3]))
    objConfiguration.addConfiguration("capitalHouseSupplyRatio", float(rawData[4]))
    objConfiguration.addConfiguration("nonCapitalHouseSupplyRatio", float(rawData[5]))
    objConfiguration.addConfiguration("moveProbability", float(rawData[8]))
    objConfiguration.addConfiguration("wtp", float(rawData[9]))
    objConfiguration.addConfiguration("saleProb", float(rawData[10]))
    objConfiguration.addConfiguration("consumptionRate1", float(rawData[12]))
    objConfiguration.addConfiguration("consumptionRate2", float(rawData[13]))
    objConfiguration.addConfiguration("consumptionRate3", float(rawData[14]))
    objConfiguration.addConfiguration("consumptionRate4", float(rawData[15]))
    objConfiguration.addConfiguration("consumptionRate5", float(rawData[16]))
    objConfiguration.addConfiguration("priorityThreshold", float(rawData[17]))

    objConfiguration.addConfiguration("participateRate", [float(rawData[11])] * int(rawData[1]))
    objConfiguration.addConfiguration("mp_ir", [float(rawData[6])] * int(rawData[1]))
    objConfiguration.addConfiguration("mp_dr", [float(rawData[7])] * int(rawData[1]))

    objConfiguration.addConfiguration("time", 0)
    objConfiguration.addConfiguration("typePriority", [None, None, None])

    # setting dynamic variables
    dynamicVariableFilename = 'InputData/Dynamic_variable_rawdata_2015.csv'
    with open(dynamicVariableFilename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            elif line_count == 1:
                rawData2 = np.array(row)
                line_count += 1
            else:
                rawData2 = np.vstack([rawData2, row])
                line_count += 1
    rawData2 = np.transpose(rawData2)
    objConfiguration.addConfiguration("interestRate", rawData2[1])
    objConfiguration.addConfiguration("inflationRate", rawData2[2])
    objConfiguration.addConfiguration("jeonseExchangeRate", rawData2[3])
    objConfiguration.addConfiguration("depositRentfeeExchangeRate", rawData2[4])
    objConfiguration.addConfiguration("creditLoanInterestRate", rawData2[5])
    objConfiguration.addConfiguration("mortLoanInterestRate", rawData2[6])
    objConfiguration.addConfiguration("fixedInterestRateSpread", rawData2[7])
    objConfiguration.addConfiguration("houseTypeRatio1", rawData2[8])
    objConfiguration.addConfiguration("houseTypeRatio2", rawData2[9])
    objConfiguration.addConfiguration("houseTypeRatio3", rawData2[10])
    objConfiguration.addConfiguration("houseTypePrice1", rawData2[11])
    objConfiguration.addConfiguration("houseTypePrice2", rawData2[12])
    objConfiguration.addConfiguration("houseTypePrice3", rawData2[13])
    objConfiguration.addConfiguration("capitalMoveRate", rawData2[14])
    objConfiguration.addConfiguration("nonCapitalMoveRate", rawData2[15])
    objConfiguration.addConfiguration("LTV", rawData2[16])
    objConfiguration.addConfiguration("DTI", rawData2[17])
    #toc()
    #tic()
    objModel = HousingMarketModel(objConfiguration)
    #toc()
    #tic()
    engine = SimulationEngine()
    engine.setOutmostModel(objModel)
    #toc()
    #tic()
    engine.run(maxTime=99999, \
               logFileName='log.txt', \
               visualizer=False, \
               logGeneral=False, \
               logActivateState=False, \
               logActivateMessage=False, \
               logActivateTA=False, \
               logStructure=False \
               )