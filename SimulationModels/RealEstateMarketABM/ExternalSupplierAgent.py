from SimulationModels.RealEstateMarketABM.SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from SimulationModels.RealEstateMarketABM.Message.endListMessage import endListMessage
from SimulationModels.RealEstateMarketABM.Message.houseInfoMessage import houseInfoMessage
from SimulationModels.RealEstateMarketABM.Message.endUpdateMessage import endUpdateMessage
from SimulationModels.RealEstateMarketABM.House import House

import random
import math
import numpy as np
import csv

class ExternalSupplierAgent(DEVSAtomicModel):

    def __init__(self, upperModel, strID, lstHouseTotal, objConfiguration):
        super().__init__(strID)
        self.strID = strID
        self.ownHouse = []

        self.upperModel = upperModel
        self.setStateValue("state", 0)  # simulation state: 0 = wait, 1 = list, 2 = buy, 3 = update
        self.lstHouseTotal = lstHouseTotal
        self.objConfiguration = objConfiguration

        #self.rawData = self.readFile('InputData/Household_rawdata_2015_1.csv')
        #weightVector = [float(x) for x in self.importColumnData(self.rawData, -1)]  # import weight value of households
        #self.normalizedWeightVector = [x / sum(weightVector) for x in weightVector]

    def funcExternalTransition(self, strPort, objEvent):
        # about List process
        if strPort == "startList":
            self.setStateValue("state", 1)

        # about Buy process
        elif strPort == "sendContractInfoSell":
            dealingHouse = objEvent.dealingHouse
            dealingType = objEvent.dealingType

            if dealingType == "sale":
                self.ownHouse.pop(self.ownHouse.index(dealingHouse))

            self.continueTimeAdvance()

        # about Update process
        elif strPort == "startUpdate":
            self.setStateValue("state", 3)

    def funcOutput(self):
        # about List process
        if self.getStateValue("state") == 1:

            # list process 1: Identify the number of vacant houses household agent have
            emptyHouseList = []
            for i in range(0, len(self.ownHouse)):
                if self.ownHouse[i].resident == -1:
                    emptyHouseList.append(self.ownHouse[i])

            # list process 2: send a vacant house list to the realtor agent
            if len(emptyHouseList) == 0:
                objEvent1 = endListMessage(self.strID)
                self.addOutputEvent("endList", objEvent1)
            else:
                objEvent1 = endListMessage(self.strID)
                self.addOutputEvent("endList", objEvent1)
                objEvent2 = houseInfoMessage(emptyHouseList)  # List houses info should be added to message
                self.addOutputEvent("requestList", objEvent2)

        # about Update process
        elif self.getStateValue("state") == 3:
            objEvent = endUpdateMessage(self.strID)
            self.addOutputEvent("endUpdate", objEvent)



    def funcInternalTransition(self):
        # about List process
        if self.getStateValue("state") == 1:
            self.setStateValue("state", 0)

        # about Update process
        elif self.getStateValue("state") == 3:

            for i in range (0, len(self.ownHouse)):
                selectHouse = self.ownHouse[i]
                if selectHouse.contractPeriod == 0:
                    selectHouse.resident = -1
                    selectHouse.contractPeriod = math.inf
                    selectHouse.rentDeposit = 0
                    selectHouse.rentFee = 0

                # update process 6: house price update
                inflationRate = float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")])
                mp_ir = float(self.upperModel.mp_ir[self.objConfiguration.getConfiguration("time")])
                if self.upperModel.typePriority[selectHouse.type-1] is None or self.upperModel.typePriority[selectHouse.type-1] < self.upperModel.priorityThreshold:
                    selectHouse.marketPriceSale = int(selectHouse.marketPriceSale*(1+inflationRate))
                    selectHouse.marketPriceRent = int(selectHouse.marketPriceRent*(1+inflationRate))
                else:
                    #print("House price is increasing at time ", str(self.objConfiguration.getConfiguration("time")))
                    selectHouse.marketPriceSale = int(selectHouse.marketPriceSale*(1+inflationRate\
                                                                                   +mp_ir))
                    selectHouse.marketPriceRent = int(selectHouse.marketPriceRent*(1+inflationRate\
                                                                                   +mp_ir))

            # House generation (capital)
            capitalMonthlyHouseSupply = 0.002
            capitalMonthlyHouseSupplyNum = int(
            capitalMonthlyHouseSupply * self.objConfiguration.getConfiguration("numAgentHousehold") / 2)
            cnt = 0
            while capitalMonthlyHouseSupplyNum != cnt:
                selectNum = int(np.argwhere(np.random.multinomial(1, self.upperModel.normalizedWeightVector) == 1))
                if self.upperModel.rawData[selectNum][20] == "A0401":
                    genHouse = House(self.upperModel)
                    genHouse.makeEmptyHouse(len(self.lstHouseTotal), self.upperModel.rawData[selectNum],
                                            self.objConfiguration)
                    genHouse.owner = 'ES'
                    self.ownHouse.append(genHouse)
                    self.lstHouseTotal.append(genHouse)
                    cnt += 1

            # House generation (nonCapital)
            nonCapitalMonthlyHouseSupply = 0.002
            nonCapitalMonthlyHouseSupplyNum = int(
            nonCapitalMonthlyHouseSupply * self.objConfiguration.getConfiguration("numAgentHousehold") / 2)
            cnt = 0
            while nonCapitalMonthlyHouseSupplyNum != cnt:
                selectNum = int(np.argwhere(np.random.multinomial(1, self.upperModel.normalizedWeightVector) == 1))
                if self.upperModel.rawData[selectNum][20] == "A0402":
                    genHouse = House(self.upperModel)
                    genHouse.makeEmptyHouse(len(self.lstHouseTotal), self.upperModel.rawData[selectNum],
                                            self.objConfiguration)
                    genHouse.owner = 'ES'
                    self.ownHouse.append(genHouse)
                    self.lstHouseTotal.append(genHouse)
                    cnt += 1

            self.setStateValue("state", 0)

    def funcTimeAdvance(self):
        if self.getStateValue("state") == 0:
            return math.inf
        elif self.getStateValue("state") == 1:
            return 1
            #return random.random()
        elif self.getStateValue("state") == 3:
            return 2

    def readFile(self, filename):
        rawData = []
        f = open('InputData/Household_rawdata_2015_1.csv')
        lines = csv.reader(f)
        temp = 0
        for line in lines:
            if temp == 0:
                temp += 1
            else:
                rawData.append(line)
                temp += 1
        rawData = np.array(rawData)
        return rawData

    def importColumnData(self, rawData, columnIndex):
        column = []
        [n,m] = rawData.shape
        for i in range (0, n):
            line = rawData[i]
            column.append(line[columnIndex])
        return column