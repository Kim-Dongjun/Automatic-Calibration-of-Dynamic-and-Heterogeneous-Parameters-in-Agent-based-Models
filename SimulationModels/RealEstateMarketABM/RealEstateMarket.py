from SimulationModels.RealEstateMarketABM.SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from SimulationModels.RealEstateMarketABM.HouseholdAgent import HouseholdAgent
from SimulationModels.RealEstateMarketABM.RealtorAgent import RealtorAgent
from SimulationModels.RealEstateMarketABM.ExternalSupplierAgent import ExternalSupplierAgent
from SimulationModels.RealEstateMarketABM.House import House

import csv
import numpy as np
import os

import time
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

class HousingMarket(DEVSCoupledModel):
    def __init__(self, objConfiguration):

        super().__init__("HousingMarket")
        self.objConfiguration = objConfiguration

        self.numAgentHousehold = self.objConfiguration.getConfiguration("numAgentHousehold")
        filename1 = 'InputData/Household_rawdata_2015_1.csv'
        filename2 = 'InputData/Household_rawdata_2015_2.csv'

        mortLoanInterestRate = float(self.objConfiguration.getConfiguration("mortLoanInterestRate")[self.objConfiguration.getConfiguration("time")])
        n_mort = self.objConfiguration.getConfiguration("mortLoanMaturity")
        self.lstHouse = []
        self.lstHouseholdAgent = []

        # Ordinary parameters
        self.consumptionRate1 = self.objConfiguration.getConfiguration("consumptionRate1")
        self.consumptionRate2 = self.objConfiguration.getConfiguration("consumptionRate2")
        self.consumptionRate3 = self.objConfiguration.getConfiguration("consumptionRate3")
        self.consumptionRate4 = self.objConfiguration.getConfiguration("consumptionRate4")
        self.consumptionRate5 = self.objConfiguration.getConfiguration("consumptionRate5")
        self.jeonseExchangeRate = self.objConfiguration.getConfiguration("jeonseExchangeRate")
        self.houseTypePrice1 = self.objConfiguration.getConfiguration("houseTypePrice1")
        self.houseTypePrice2 = self.objConfiguration.getConfiguration("houseTypePrice2")
        self.houseTypePrice3 = self.objConfiguration.getConfiguration("houseTypePrice3")
        self.itrCalibration = self.objConfiguration.getConfiguration("itrCalibration")
        self.microResults = self.objConfiguration.getConfiguration("microResults")
        self.running_folder = self.objConfiguration.getConfiguration("running_folder")
        self.simulationNumber = self.objConfiguration.getConfiguration("simulationNumber")

        self.moveProbability = self.objConfiguration.getConfiguration("moveProbability")
        self.typePriority = self.objConfiguration.getConfiguration("typePriority")
        self.priorityThreshold = self.objConfiguration.getConfiguration("priorityThreshold")
        self.inflationRate = self.objConfiguration.getConfiguration("inflationRate")
        self.LTV = self.objConfiguration.getConfiguration("LTV")
        self.DTI = self.objConfiguration.getConfiguration("DTI")
        self.mortLoanInterestRate = self.objConfiguration.getConfiguration("mortLoanInterestRate")
        self.gamma = self.objConfiguration.getConfiguration("depositRentfeeExchangeRate")
        self.mortLoanMaturity = self.objConfiguration.getConfiguration("mortLoanMaturity")
        self.capitalMoveRate = self.objConfiguration.getConfiguration("capitalMoveRate")
        self.nonCapitalMoveRate = self.objConfiguration.getConfiguration("nonCapitalMoveRate")
        self.houseTypeRatio1 = self.objConfiguration.getConfiguration("houseTypeRatio1")
        self.houseTypeRatio2 = self.objConfiguration.getConfiguration("houseTypeRatio2")
        self.houseTypeRatio3 = self.objConfiguration.getConfiguration("houseTypeRatio3")
        self.creditLoanInterestRate = self.objConfiguration.getConfiguration("creditLoanInterestRate")
        self.interestRate = self.objConfiguration.getConfiguration("interestRate")
        self.creditLoanMaturity = self.objConfiguration.getConfiguration("creditLoanMaturity")
        self.priorityThreshold = self.objConfiguration.getConfiguration("priorityThreshold")
        self.agentClusters = self.objConfiguration.getConfiguration("agentClusters")

        # Dynamic Parameters
        self.participateRate = self.objConfiguration.getConfiguration("participateRate")
        self.mp_ir = self.objConfiguration.getConfiguration("mp_ir")
        self.mp_dr = self.objConfiguration.getConfiguration("mp_dr")

        # Heterogeneous Parameters
        self.wtp = self.objConfiguration.getConfiguration("wtp")
        self.saleProb = self.objConfiguration.getConfiguration("saleProb")

        if int(self.simulationNumber) == 0:
            print("participationRate : ", self.participateRate)
            print("mp_ir : ", self.mp_ir)
            print("mp_dr : ", self.mp_dr)
            print("wtp : ", self.wtp)
            print("saleProb : ", self.saleProb)

        self.rawData = self.readFile(filename1)
        weightVector = [float(x) for x in self.importColumnData(self.rawData, -1)]  # import weight value of households
        self.normalizedWeightVector = [x / sum(weightVector) for x in weightVector]

        self.objRealtor = RealtorAgent(self, 'Realtor', objConfiguration)
        self.addModel(self.objRealtor)  # Simulation Engine registered


        self.objExternalSupplierAgent = ExternalSupplierAgent(self, 'ExternalSupplier', self.lstHouse, objConfiguration)
        self.addModel(self.objExternalSupplierAgent)  # Simulation Engine registered

        # Household generation step 1 & 2 (except matching house owner and renter)
        #tic()
        if self.objConfiguration.getConfiguration('calibrationType') != 'dynamic':
            np.random.seed(0)
        for i in range(0, self.numAgentHousehold):
            selectNum = int(np.argwhere(np.random.multinomial(1, self.normalizedWeightVector) == 1))
            genHousehold = HouseholdAgent(self, 'HouseholdAgent_'+str(i), i, self.rawData[selectNum], objConfiguration, self.lstHouseholdAgent)
            self.lstHouseholdAgent.append(genHousehold)
            self.addModel(genHousehold)
            self.lstHouse.append(genHousehold.livingHouse)
        #print("여기 시간")
        #toc()
        #sys.exit()
        np.random.seed(int(time.time()))
        # Household generation step 3 (matching house owner and renter)
        houseOtherValueList = []
        for j in range(0, len(self.lstHouseholdAgent)):
            houseOtherValueList.append(self.lstHouseholdAgent[j].houseOtherValue)
        for i in range(0, len(self.lstHouse)):
            selectHouse = self.lstHouse[i]
            if selectHouse.owner == -1:
                houseValue = selectHouse.marketPriceSale
                resident = self.lstHouseholdAgent[selectHouse.resident]
                #houseOtherValueList = []
                #for j in range(0, len(self.lstHouseholdAgent)):
                #    houseOtherValueList.append(self.lstHouseholdAgent[j].houseOtherValue)
                owner = self.lstHouseholdAgent[houseOtherValueList.index(max(houseOtherValueList))]

                if owner != resident and owner.houseOtherValue + owner.houseOtherMort > houseValue:
                    selectHouse.owner = owner.numID
                    temp = owner.houseOtherValue - houseValue
                    if temp >= 0:
                        owner.houseOtherValue = temp
                    else:
                        owner.houseOtherValue = 0
                        owner.houseOtherMort -= -temp
                        selectHouse.mortLoan = -temp
                        selectHouse.mortRepayment = selectHouse.mortLoan * mortLoanInterestRate * pow(
                            1 + mortLoanInterestRate, n_mort) / (pow(1 + mortLoanInterestRate, n_mort) - 1)
                    houseOtherValueList[np.argmax(houseOtherValueList)] = owner.houseOtherValue
                    owner.ownHouse.append(selectHouse)
                else:
                    selectHouse.owner = 'ES'
                    self.objExternalSupplierAgent.ownHouse.append(selectHouse)


        # Household generation step 4 (noncapital house supply rate fitting)
        capitalHouseSupplyRatio = self.objConfiguration.getConfiguration("capitalHouseSupplyRatio")
        capitalCnt = 0
        for i in range(0, len(self.lstHouseholdAgent)):
            if self.lstHouseholdAgent[i].region == 1:
                capitalCnt += 1
        nonCapitalCnt = len(self.lstHouseholdAgent) - capitalCnt

        nonCapitalHouseSupplyRatio = self.objConfiguration.getConfiguration("nonCapitalHouseSupplyRatio")
        nonCapitalHouseNeed = int(nonCapitalCnt * nonCapitalHouseSupplyRatio) - nonCapitalCnt
        cnt = 0
        while nonCapitalHouseNeed != cnt:
            selectNum = int(np.argwhere(np.random.multinomial(1, self.normalizedWeightVector) == 1))
            if self.rawData[selectNum][20] == "A0402":
                genHouse = House(self)
                genHouse.makeEmptyHouse(len(self.lstHouse), self.rawData[selectNum], self.objConfiguration)
                houseValue = genHouse.marketPriceSale
                houseOtherValueList = []
                for j in range(0, len(self.lstHouseholdAgent)):
                    houseOtherValueList.append(self.lstHouseholdAgent[j].houseOtherValue)
                owner = self.lstHouseholdAgent[houseOtherValueList.index(max(houseOtherValueList))]

                if owner.houseOtherValue + owner.houseOtherMort > houseValue:
                    genHouse.owner = owner.numID
                    temp = owner.houseOtherValue - houseValue
                    if temp >= 0:
                        owner.houseOtherValue = temp
                    else:
                        owner.houseOtherValue = 0
                        owner.houseOtherMort -= -temp
                        genHouse.mortLoan = -temp
                        genHouse.mortRepayment = genHouse.mortLoan * mortLoanInterestRate * pow(
                            1 + mortLoanInterestRate, n_mort) / (pow(1 + mortLoanInterestRate, n_mort) - 1)
                    owner.ownHouse.append(genHouse)
                else:
                    genHouse.owner = 'ES'
                    self.objExternalSupplierAgent.ownHouse.append(genHouse)

                self.lstHouse.append(genHouse)
                cnt += 1

        # Household generation step 5 (capital house supply rate fitting)
        capitalHouseholdNeed = int(capitalCnt / capitalHouseSupplyRatio) - capitalCnt
        self.rawData2 = self.readFile(filename2)
        weightVector2 = [float(x) for x in
                         self.importColumnData(self.rawData2, -1)]  # import weight value of households
        normalizedWeightVector2 = [x / sum(weightVector2) for x in weightVector2]
        #print("CapitalHouseholdNeed : ", len(self.lstHouseholdAgent))
        #print("Real Capital : ", capitalHouseholdNeed)
        for i in range(0, capitalHouseholdNeed):
            selectNum = int(np.argwhere(np.random.multinomial(1, normalizedWeightVector2) == 1))
            genHousehold = HouseholdAgent(self,'HouseholdAgent_'+str(len(self.lstHouseholdAgent)), len(self.lstHouseholdAgent), self.rawData2[selectNum], objConfiguration, self.lstHouseholdAgent)
            self.lstHouseholdAgent.append(genHousehold)
            self.addModel(genHousehold)

        # add External Coupling
        for i in range(len(self.lstHouseholdAgent)):
            self.addExternalInputCoupling("startList", self.lstHouseholdAgent[i], "startList")
            self.addExternalInputCoupling("startBuy", self.lstHouseholdAgent[i], "startBuy")
            self.addExternalInputCoupling("startUpdate", self.lstHouseholdAgent[i], "startUpdate")
            self.addExternalOutputCoupling(self.lstHouseholdAgent[i],"endList", "endList")
            self.addExternalOutputCoupling(self.lstHouseholdAgent[i], "endBuy", "endBuy")
            self.addExternalOutputCoupling(self.lstHouseholdAgent[i], "endUpdate", "endUpdate")

        self.addExternalInputCoupling("startList", self.objExternalSupplierAgent, "startList")
        self.addExternalInputCoupling("startUpdate", self.objExternalSupplierAgent, "startUpdate")
        self.addExternalOutputCoupling(self.objExternalSupplierAgent, "endList", "endList")
        self.addExternalOutputCoupling(self.objExternalSupplierAgent, "endUpdate", "endUpdate")

        self.addExternalInputCoupling("startUpdate", self.objRealtor, "startUpdate")
        self.addExternalOutputCoupling(self.objRealtor, "endUpdate", "endUpdate")

        # add Internal Coupling for List process
        for i in range(len(self.lstHouseholdAgent)):
            self.addInternalCoupling(self.lstHouseholdAgent[i], "requestList", self.objRealtor, "requestList")
        self.addInternalCoupling(self.objExternalSupplierAgent, "requestList", self.objRealtor, "requestList")

        # add Internal Coupling for Buy process
        for i in range(len(self.lstHouseholdAgent)):
            self.addInternalCoupling(self.lstHouseholdAgent[i], "requestHouseInfo", self.objRealtor, "requestHouseInfo")
            self.addInternalCoupling(self.objRealtor, "sendHouseInfo_"+str(i), self.lstHouseholdAgent[i], "sendHouseInfo")
            self.addInternalCoupling(self.lstHouseholdAgent[i], "sendDecisionInfo", self.objRealtor, "sendDecisionInfo")
            self.addInternalCoupling(self.objRealtor, "sendContractInfoBuy_"+str(i), self.lstHouseholdAgent[i], "sendContractInfoBuy")
            self.addInternalCoupling(self.objRealtor, "sendContractInfoSell_"+str(i), self.lstHouseholdAgent[i], "sendContractInfoSell")
        self.addInternalCoupling(self.objRealtor, "sendContractInfoSell_ES", self.objExternalSupplierAgent, "sendContractInfoSell")


    def readFile(self, filename):
        rawData = []
        f = open(os.path.dirname(os.path.abspath(__file__)) + '/InputData/Household_rawdata_2015_1.csv')
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
