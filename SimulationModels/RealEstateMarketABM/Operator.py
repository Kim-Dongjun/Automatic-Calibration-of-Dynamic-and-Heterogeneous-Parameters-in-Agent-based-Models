from SimulationModels.RealEstateMarketABM.SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from SimulationModels.RealEstateMarketABM.Message.startListMessage import startListMessage
from SimulationModels.RealEstateMarketABM.Message.startBuyMessage import startBuyMessage
from SimulationModels.RealEstateMarketABM.Message.startUpdateMessage import startUpdateMessage
from SimulationModels.RealEstateMarketABM.SimulationEngine.Utility.Configurator import Configurator
import os
import math

class Operator(DEVSAtomicModel):

    def __init__(self, objConfiguration, lstHouseholdAgent, lstHouse):
        super().__init__("Operator")
        self.setStateValue("operate", True)
        self.setStateValue("time", 0)   # simulation time 0 ~ T
        self.setStateValue("state", 0)  # simulation state: 0 = wait, 1 = list, 2 = buy, 3 = update
        #self.setStateValue("numEnd", 0)  # end signal counting for each state
        self.numEnd = 0
        self.objConfiguration = objConfiguration
        self.lstHouseholdAgent = lstHouseholdAgent
        self.lstHouse = lstHouse
        self.numAgentHousehold = len(lstHouseholdAgent)
        self.simTime = objConfiguration.getConfiguration("simTime")

        if objConfiguration.getConfiguration("microResults") == True:
            if not os.path.exists(objConfiguration.getConfiguration("running_folder")+"MicroResults"):
                os.makedirs(objConfiguration.getConfiguration("running_folder")+"MicroResults")
            self.objLogHouseHold = open(objConfiguration.getConfiguration("running_folder")+"MicroResults/MicroLog_"+str(objConfiguration.getConfiguration("simulationNumber"))+".csv", 'w')
            #print("Look Here, the simulation number is ", str(objConfiguration.getConfiguration("simulationNumber")))
            self.objLogHouseHold.write('Time,numID,Region,Savings,IncomeWork,Loan,HouseType,LivingType,NumberOfHouses\n')

        #self.objLogHouse = open('HouseLog.csv', 'w')
        #self.objLogHouse.write('time,numID,region,type,size,owner,marketPriceSale,marketPriceRent,holdingPeriod,resident,contractPeriod,rentDeposit,rentFee\n')

    def funcExternalTransition(self, strPort, objEvent):
        if strPort == "endList":
            #print("오퍼레이터 메세지 받는중")
            #print(str(objEvent))
            #self.setStateValue("numEnd", self.getStateValue("numEnd") + 1)
            self.numEnd += 1
        elif strPort == "endBuy":
            #print(str(objEvent))
            #self.setStateValue("numEnd", self.getStateValue("numEnd") + 1)
            self.numEnd += 1
        elif strPort == "endUpdate":
            #print(str(objEvent))
            #self.setStateValue("numEnd", self.getStateValue("numEnd") + 1)
            self.numEnd += 1
    def funcOutput(self):
        if self.getStateValue("time") == 0:     # simulation start (start list process)
            objEvent = startListMessage(self.getStateValue("time")+1)
            self.addOutputEvent("startList", objEvent)
            #print(str(objEvent))
        #elif self.getStateValue("state") == 1 and self.getStateValue("numEnd") == self.numAgentHousehold + 1:   # start buy process
        elif self.getStateValue("state") == 1 and self.numEnd == self.numAgentHousehold + 1:  # start buy process
            objEvent = startBuyMessage(self.getStateValue("time"))
            self.addOutputEvent("startBuy", objEvent)
            #print(str(objEvent))
        #elif self.getStateValue("state") == 2 and self.getStateValue("numEnd") == self.numAgentHousehold:       # start update process
        elif self.getStateValue("state") == 2 and self.numEnd == self.numAgentHousehold:  # start update process
            objEvent = startUpdateMessage(self.getStateValue("time"))
            self.addOutputEvent("startUpdate", objEvent)
            #print(str(objEvent))
        #elif self.getStateValue("state") == 3 and self.getStateValue("numEnd") == self.numAgentHousehold + 2:   # start list process
        elif self.getStateValue("state") == 3 and self.numEnd == self.numAgentHousehold + 2:  # start list process
            objEvent = startListMessage(self.getStateValue("time")+1)
            self.addOutputEvent("startList", objEvent)
            #print(str(objEvent))

    def funcInternalTransition(self):
        if self.getStateValue("time") == 0:     # simulation start (start list process)
            if self.objConfiguration.getConfiguration("microResults") == True:
                for agent in range(self.objConfiguration.getConfiguration("numAgentHousehold")):
                    #print("currentThread : ", self.objConfiguration.getConfiguration("simulationNumber"))
                    selectHousehold = self.lstHouseholdAgent[agent]
                    if selectHousehold.livingHouse != None and selectHousehold.livingHouse.owner == selectHousehold.numID:
                        self.objLogHouseHold.write(str(self.objConfiguration.getConfiguration("time")) + "," + \
                                                   str(selectHousehold.numID) + "," + \
                                                   str(selectHousehold.region) + "," + \
                                                    str(selectHousehold.savings) + "," + \
                                                   str(int(selectHousehold.incomeWork)) + "," + \
                                                    str(selectHousehold.calcMortLoanSum()) + "," + \
                                                    str(selectHousehold.livingHouse.type) + "," + \
                                                    str(1) + "," + \
                                                   str(len(selectHousehold.ownHouse)) + "\n")
                    elif selectHousehold.livingHouse != None and selectHousehold.livingHouse.owner != selectHousehold.numID:
                        self.objLogHouseHold.write(str(self.objConfiguration.getConfiguration("time")) + "," + \
                                                   str(selectHousehold.numID) + "," + \
                                                   str(selectHousehold.region) + "," + \
                                                   str(selectHousehold.savings) + "," + \
                                                   str(int(selectHousehold.incomeWork)) + "," + \
                                                   str(selectHousehold.calcMortLoanSum()) + "," + \
                                                   str(selectHousehold.livingHouse.type) + "," + \
                                                   str(2) + "," + \
                                                   str(len(selectHousehold.ownHouse)) + "\n")
                    else:
                        self.objLogHouseHold.write(str(self.objConfiguration.getConfiguration("time")) + "," + \
                                                   str(selectHousehold.numID) + "," + \
                                                   str(selectHousehold.region) + "," + \
                                                   str(selectHousehold.savings) + "," + \
                                                   str(int(selectHousehold.incomeWork)) + "," + \
                                                   str(selectHousehold.calcMortLoanSum()) + "," + \
                                                   str(4) + "," + \
                                                   str(3) + "," + \
                                                   str(len(selectHousehold.ownHouse)) + "\n")
            houseMarketSalePrices = []
            houseMarketRentPrices = []
            houseRegions = []
            houseTypes = []
            for house in self.lstHouse:
                houseMarketSalePrices.append(house.marketPriceSale)
                houseMarketRentPrices.append(house.marketPriceRent)
                houseRegions.append(house.region)
                houseTypes.append(house.type)
            self.objConfiguration.getConfiguration("HouseMarketSalePrices").append(houseMarketSalePrices)
            self.objConfiguration.getConfiguration("HouseMarketRentPrices").append(houseMarketRentPrices)
            self.objConfiguration.getConfiguration("HouseRegions").append(houseRegions)
            self.objConfiguration.getConfiguration("HouseTypes").append(houseTypes)
            
            self.setStateValue("time", 1)
            self.setStateValue("state", 1)
        #elif self.getStateValue("state") == 1 and self.getStateValue("numEnd") == self.numAgentHousehold + 1:   # start buy process
        elif self.getStateValue("state") == 1 and self.numEnd == self.numAgentHousehold + 1:  # start buy process
            self.setStateValue("state", 2)
            #self.setStateValue("numEnd", 0)
            self.numEnd = 0
        #elif self.getStateValue("state") == 2 and self.getStateValue("numEnd") == self.numAgentHousehold:       # start update process
        elif self.getStateValue("state") == 2 and self.numEnd == self.numAgentHousehold:  # start update process
            if self.getStateValue("time") != self.simTime:
                self.setStateValue("state", 3)
                #self.setStateValue("numEnd", 0)
                self.numEnd = 0
            else:
                self.setStateValue("operate", False)
        #elif self.getStateValue("state") == 3 and self.getStateValue("numEnd") == self.numAgentHousehold + 2:   # start list process
        elif self.getStateValue("state") == 3 and self.numEnd == self.numAgentHousehold + 2:  # start list process
            self.setStateValue("time", self.getStateValue("time") + 1)
            self.setStateValue("state", 1)
            #self.setStateValue("numEnd", 0)
            self.numEnd = 0
            self.objConfiguration.addConfiguration("time", self.objConfiguration.getConfiguration("time") + 1)

            # write log of Households and Houses
            if self.objConfiguration.getConfiguration("microResults") == True:
                for agent in range(self.objConfiguration.getConfiguration("numAgentHousehold")):
                    selectHousehold = self.lstHouseholdAgent[agent]
                    if selectHousehold.livingHouse != None and selectHousehold.livingHouse.owner == selectHousehold.numID:
                        self.objLogHouseHold.write(str(self.objConfiguration.getConfiguration("time")) + "," + \
                                                   str(selectHousehold.numID) + "," + \
                                                   str(selectHousehold.region) + "," + \
                                                    str(selectHousehold.savings) + "," + \
                                                   str(int(selectHousehold.incomeWork)) + "," + \
                                                    str(selectHousehold.calcMortLoanSum()) + "," + \
                                                    str(selectHousehold.livingHouse.type) + "," + \
                                                    str(1) + "," + \
                                                   str(len(selectHousehold.ownHouse)) + "\n")
                    elif selectHousehold.livingHouse != None and selectHousehold.livingHouse.owner != selectHousehold.numID:
                        self.objLogHouseHold.write(str(self.objConfiguration.getConfiguration("time")) + "," + \
                                                   str(selectHousehold.numID) + "," + \
                                                   str(selectHousehold.region) + "," + \
                                                   str(selectHousehold.savings) + "," + \
                                                   str(int(selectHousehold.incomeWork)) + "," + \
                                                   str(selectHousehold.calcMortLoanSum()) + "," + \
                                                   str(selectHousehold.livingHouse.type) + "," + \
                                                   str(2) + "," + \
                                                   str(len(selectHousehold.ownHouse)) + "\n")
                    else:
                        self.objLogHouseHold.write(str(self.objConfiguration.getConfiguration("time")) + "," + \
                                                   str(selectHousehold.numID) + "," + \
                                                   str(selectHousehold.region) + "," + \
                                                   str(selectHousehold.savings) + "," + \
                                                   str(int(selectHousehold.incomeWork)) + "," + \
                                                   str(selectHousehold.calcMortLoanSum()) + "," + \
                                                   str(4) + "," + \
                                                   str(3) + "," + \
                                                   str(len(selectHousehold.ownHouse)) + "\n")
            houseMarketSalePrices = []
            houseMarketRentPrices = []
            houseRegions = []
            houseTypes = []
            for house in self.lstHouse:
                houseMarketSalePrices.append(house.marketPriceSale)
                houseMarketRentPrices.append(house.marketPriceRent)
                houseRegions.append(house.region)
                houseTypes.append(house.type)
            self.objConfiguration.getConfiguration("HouseMarketSalePrices").append(houseMarketSalePrices)
            self.objConfiguration.getConfiguration("HouseMarketRentPrices").append(houseMarketRentPrices)
            self.objConfiguration.getConfiguration("HouseRegions").append(houseRegions)
            self.objConfiguration.getConfiguration("HouseTypes").append(houseTypes)

    def funcTimeAdvance(self):
        if self.getStateValue("operate"):
            if self.getStateValue("time") == 0:     # simulation start (start list process)
                return 1
            #elif self.getStateValue("state") == 1 and self.getStateValue("numEnd") == self.numAgentHousehold + 1:   # start buy process
            elif self.getStateValue("state") == 1 and self.numEnd == self.numAgentHousehold + 1:  # start buy process
                return 1
            #elif self.getStateValue("state") == 2 and self.getStateValue("numEnd") == self.numAgentHousehold:       # start update process
            elif self.getStateValue("state") == 2 and self.numEnd == self.numAgentHousehold:  # start update process
                return 1
            #elif self.getStateValue("state") == 3 and self.getStateValue("numEnd") == self.numAgentHousehold + 2:   # start list process
            elif self.getStateValue("state") == 3 and self.numEnd == self.numAgentHousehold + 2:  # start list process
                return 1
            else:
                return math.inf
        else:
            return math.inf

    def funcSelect(self):
        pass