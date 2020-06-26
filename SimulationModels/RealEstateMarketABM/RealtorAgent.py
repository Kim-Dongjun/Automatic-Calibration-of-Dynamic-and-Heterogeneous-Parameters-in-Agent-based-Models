from SimulationModels.RealEstateMarketABM.SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from SimulationModels.RealEstateMarketABM.Message.houseInfoMessage import houseInfoMessage
from SimulationModels.RealEstateMarketABM.Message.contractInfoMessage import contractInfoMessage
from SimulationModels.RealEstateMarketABM.Message.endUpdateMessage import endUpdateMessage

import random
import math
import numpy as np
import sys

class RealtorAgent(DEVSAtomicModel):

    def __init__(self, upperModel, strID, objConfiguration):
        self.strID = strID
        super().__init__(strID)

        self.upperModel = upperModel

        self.setStateValue("state", 0)  # Realtor state: 0 = idle

        self.enrollHouseList = []
        self.nowCustomerBuyList = []
        self.lstHousesClassList = []
        self.dealingHouseList = []
        self.dealingTypeList = []

        self.listTypeCount = np.zeros(3, dtype=float)
        self.sellTypeCount = np.zeros(3, dtype=float)

        self.objConfiguration = objConfiguration

        self.objLogFile = open(self.upperModel.running_folder + "iteration_" + str(self.upperModel.itrCalibration)
                               + "/" + "TransactionNumber_candidate_"
                               + str(self.objConfiguration.getConfiguration("currentCandidate"))
                                + "_replication_" + str(self.objConfiguration.getConfiguration("currentReplication"))
                               + ".csv", "w")
        self.objLogFile.write('time,buyerID,sellerID,houseID,houseRegion,houseType,houseSize,salePrice,rentPrice,'
                              'transactionType\n')
        #self.objLogFile.flush()

    def funcExternalTransition(self, strPort, objEvent):
        # about List process
        if strPort == "requestList":
            self.continueTimeAdvance()
            for i in range (0, len(objEvent.lstHouses)):
                self.enrollHouseList.append(objEvent.lstHouses[i])
                self.listTypeCount[objEvent.lstHouses[i].type-1] += 1

        # about Buy process
        elif strPort == "requestHouseInfo":
            if self.getStateValue("state") == 0:
                self.setStateValue("state", 21)     # Realtor state: 21 = finding House Info
                self.nowCustomerBuyList.append(objEvent.sender)
                self.lstHousesClassList.append(objEvent.lstHousesClass)
            elif self.getStateValue("state") == 21:
                self.nowCustomerBuyList.append(objEvent.sender)
                self.lstHousesClassList.append(objEvent.lstHousesClass)
                self.continueTimeAdvance()

        elif strPort == "sendDecisionInfo":
            if self.getStateValue("state") == 0:
                self.setStateValue("state", 22)     # Realtor state: 22 = dealing contract
                self.nowCustomerBuyList.append(objEvent.sender)
                self.dealingHouseList.append(objEvent.decision)
                self.dealingTypeList.append(objEvent.dealingType)
            elif self.getStateValue("state") == 22:
                self.nowCustomerBuyList.append(objEvent.sender)
                self.dealingHouseList.append(objEvent.decision)
                self.dealingTypeList.append(objEvent.dealingType)
                self.continueTimeAdvance()

        # about Update process
        elif strPort == "startUpdate":
            self.setStateValue("state", 3)

            alpha = 0.3
            typePriority = self.upperModel.typePriority
            for i in range (len(self.listTypeCount)):
                if self.listTypeCount[i] != 0:
                    nowPriority = self.sellTypeCount[i]/self.listTypeCount[i]
                else:
                    nowPriority = 1

                if typePriority[i] is None:
                    typePriority[i] = nowPriority
                else:
                    typePriority[i] = (1-alpha)*typePriority[i]+alpha*nowPriority

            self.objConfiguration.addConfiguration("typePriority", typePriority)
            #print(typePriority)
            self.listTypeCount = np.zeros(3, dtype=float)
            self.sellTypeCount = np.zeros(3, dtype=float)

    def funcOutput(self):
        # about Buy process
        if self.getStateValue("state") == 21:
            for i in range (len(self.nowCustomerBuyList)):

                nowCustomerBuy = self.nowCustomerBuyList[i]
                lstHousesClass = self.lstHousesClassList[i]

                selectRegion = lstHousesClass[0]
                selectType = lstHousesClass[1]
                selectUpper = lstHousesClass[2]
                selectLower = lstHousesClass[3]

                proposeHouseList = []
                for i in range (0,len(self.enrollHouseList)):
                    selectHouse = self.enrollHouseList[i]
                    if selectHouse.region == selectRegion and selectHouse.type == selectType:
                        if selectHouse.marketPriceSale >= selectLower and selectHouse.marketPriceSale <= selectUpper and selectHouse.owner != nowCustomerBuy:
                            proposeHouseList.append(selectHouse)

                Z = 5
                sampledHouseList = random.sample(proposeHouseList, min(len(proposeHouseList),Z))

                objEvent = houseInfoMessage(sampledHouseList)
                self.addOutputEvent("sendHouseInfo_"+str(nowCustomerBuy), objEvent)

            self.nowCustomerBuyList = []
            self.lstHousesClassList = []

        elif self.getStateValue("state") == 22:
            for i in range (len(self.nowCustomerBuyList)):
                nowCustomerBuy = self.nowCustomerBuyList[i]
                dealingHouse = self.dealingHouseList[i]
                dealingType = self.dealingTypeList[i]
                nowCustomerSell = dealingHouse.owner

                if dealingHouse in self.enrollHouseList:
                    #print("enrollHouseList : ", self.enrollHouseList)
                    if nowCustomerSell == 'ES':
                        objEvent = contractInfoMessage(dealingHouse, dealingType)
                        self.addOutputEvent("sendContractInfoSell_ES", objEvent)
                        self.addOutputEvent("sendContractInfoBuy_" + str(nowCustomerBuy), objEvent)
                    else:
                        objEvent = contractInfoMessage(dealingHouse, dealingType)
                        self.addOutputEvent("sendContractInfoSell_" + str(nowCustomerSell), objEvent)
                        self.addOutputEvent("sendContractInfoBuy_" + str(nowCustomerBuy), objEvent)
                    #print("currentThread : ", self.objConfiguration.getConfiguration("simulationNumber"))
                    self.objLogFile.write(str(self.objConfiguration.getConfiguration("time") + 1) + "," + \
                                          str(nowCustomerBuy) + "," + \
                                          str(nowCustomerSell) + "," + \
                                          str(dealingHouse.numID) + "," + \
                                          str(dealingHouse.region) + "," + \
                                          str(dealingHouse.type) + "," + \
                                          str(dealingHouse.size) + "," + \
                                          str(int(dealingHouse.marketPriceSale)) + "," + \
                                          str(int(dealingHouse.marketPriceRent)) + "," + \
                                          str(dealingType) + "\n")

                    self.sellTypeCount[dealingHouse.type - 1] += 1
                    self.enrollHouseList.pop(self.enrollHouseList.index(dealingHouse))

                else:
                    objEvent = contractInfoMessage(None, "fail")
                    self.addOutputEvent("sendContractInfoBuy_" + str(nowCustomerBuy), objEvent)

            #self.objLogFile.flush()
            self.nowCustomerBuyList = []
            self.dealingHouseList = []
            self.dealingTypeList = []

        # about Update process
        elif self.getStateValue("state") == 3:
            objEvent = endUpdateMessage(self.strID)
            self.addOutputEvent("endUpdate", objEvent)

    def funcInternalTransition(self):
        # about Buy process
        if self.getStateValue("state") == 21:
            self.setStateValue("state", 0)
        elif self.getStateValue("state") == 22:
            self.setStateValue("state", 0)

        # about Update process
        elif self.getStateValue("state") == 3:

            self.setStateValue("state", 0)
            mp_dr = float(self.upperModel.mp_dr[self.objConfiguration.getConfiguration("time")])
            for i in range(0, len(self.enrollHouseList)):
                selectHouse = self.enrollHouseList[i]
                selectHouse.unsoldPeriod += 1
                if selectHouse.unsoldPeriod <= 10:
                    if selectHouse.region == 0:
                        selectHouse.marketPriceSale = int(selectHouse.marketPriceSale*(1-mp_dr))
                        selectHouse.marketPriceRent = int(selectHouse.marketPriceRent*(1-mp_dr))
                    else:
                        selectHouse.marketPriceSale = int(selectHouse.marketPriceSale * (1 - 5 * mp_dr))
                        selectHouse.marketPriceRent = int(selectHouse.marketPriceRent * (1 - 5 * mp_dr))
            self.enrollHouseList = []

    def funcTimeAdvance(self):
        if self.getStateValue("state") == 0:
            return math.inf
        elif self.getStateValue("state") == 21:
            return 1
        elif self.getStateValue("state") == 22:
            return 1
        elif self.getStateValue("state") == 3:
            return 2

    def funcSelect(self):
        pass