from SimulationModels.RealEstateMarketABM.SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from SimulationModels.RealEstateMarketABM.Message.endListMessage import endListMessage
from SimulationModels.RealEstateMarketABM.Message.houseInfoMessage import houseInfoMessage
from SimulationModels.RealEstateMarketABM.Message.houseClassMessage import houseClassMessage
from SimulationModels.RealEstateMarketABM.Message.decisionInfoMessage import decisionInfoMessage
from SimulationModels.RealEstateMarketABM.Message.endBuyMessage import endBuyMessage
from SimulationModels.RealEstateMarketABM.Message.endUpdateMessage import endUpdateMessage
from SimulationModels.RealEstateMarketABM.House import House
import time

import random
import math
import numpy as np
import sys

class HouseholdAgent(DEVSAtomicModel):

    def __init__(self, upperModel, strID, numID, rawDataLine, objConfiguration, lstHouseholdAgent):
        super().__init__(strID)
        self.strID = strID
        self.objConfiguration = objConfiguration
        self.lstHouseholdAgent = lstHouseholdAgent

        self.upperModel = upperModel

        # Household property - Householder
        self.numID = numID
        self.age = int(rawDataLine[2])
        self.education = int(rawDataLine[3])
        self.marriage = int(rawDataLine[4])
        self.member = int(rawDataLine[6])
        if rawDataLine[5] == "1" or rawDataLine[5] == "2" or rawDataLine[5] == "3":
            self.jobOffice = 1
            self.jobService = 0
            self.jobWork = 0
        elif rawDataLine[5] == "4"  or rawDataLine[5] == "5" or rawDataLine[5] == "A":
            self.jobOffice = 0
            self.jobService = 1
            self.jobWork = 0
        elif rawDataLine[5] == "6" or rawDataLine[5] == "7" or rawDataLine[5] == "8" or rawDataLine[5] == "9":
            self.jobOffice = 0
            self.jobService = 0
            self.jobWork = 1
        else:
            self.jobOffice = 0
            self.jobService = 0
            self.jobWork = 0

        # Household property - Living
        if rawDataLine[20] == "A0401":
            self.region = 1
        elif rawDataLine[20] == "A0402":
            self.region = 0

        if rawDataLine[9] == "1":
            livingHouse = House(upperModel)
            livingHouse.makeHouse(numID, rawDataLine, self.objConfiguration)
            self.livingHouse = livingHouse
            self.ownHouse = [livingHouse]
        elif rawDataLine[9] == "2" or rawDataLine[9] == "3" or rawDataLine[9] == "4":
            livingHouse = House(upperModel)
            livingHouse.makeHouse(numID, rawDataLine, self.objConfiguration)
            self.livingHouse = livingHouse
            self.ownHouse = []
        elif rawDataLine[9] == "5":
            self.livingHouse = None
            self.ownHouse = []

        # Household property - Wealth & Income
        self.savings = int(rawDataLine[10])
        self.incomeWork = int(rawDataLine[17]) + int(rawDataLine[18]) + int(rawDataLine[19])/12.0
        if rawDataLine[21] == "A1901":
            self.consumptionRate = self.upperModel.consumptionRate1
        elif rawDataLine[21] == "A1902":
            self.consumptionRate = self.upperModel.consumptionRate2
        elif rawDataLine[21] == "A1903":
            self.consumptionRate = self.upperModel.consumptionRate3
        elif rawDataLine[21] == "A1904":
            self.consumptionRate = self.upperModel.consumptionRate4
        elif rawDataLine[21] == "A1905":
            self.consumptionRate = self.upperModel.consumptionRate5
        self.creditLoan = int(rawDataLine[16])
        self.creditRepayment = self.creditLoan*float(self.upperModel.creditLoanInterestRate[self.objConfiguration.getConfiguration("time")])\
                               *pow(1+float(self.upperModel.creditLoanInterestRate[self.objConfiguration.getConfiguration("time")]), self.upperModel.creditLoanMaturity)\
                               /(pow(1+float(self.upperModel.creditLoanInterestRate[self.objConfiguration.getConfiguration("time")]), self.upperModel.creditLoanMaturity)-1)

        # Household property - mortgage except living house
        self.houseOtherValue = int(rawDataLine[13])
        self.houseOtherMort = int(rawDataLine[14])

        self.setStateValue("state", 0)  # HH state: 0 = wait, 1 = list, 2 = buy, 3 = update
        try:
            agentCluster = self.upperModel.agentClusters[numID]
        except:
            agentCluster = 0
        try:
            self.wtp = float(self.upperModel.wtp[agentCluster])  # willingness to pay
            self.saleProb = float(self.upperModel.saleProb[agentCluster])
        except:
            self.wtp = float(self.upperModel.wtp)
            self.saleProb = float(self.upperModel.saleProb)

    def funcExternalTransition(self, strPort, objEvent):
        # about List process
        if strPort == "startList":
            self.setStateValue("state", 1)

        # about Buy process
        elif strPort == "startBuy":

            # Buy process 1: participate decision

            if self.livingHouse is None:
                #print(self.strID + " has no living house!!!")
                self.saleParticipation = True
                self.rentParticipation = True
            elif random.random() < float(self.upperModel.participateRate[self.objConfiguration.getConfiguration("time")]):
                if self.region == 1:
                    if random.random() < 0.5:
                        if self.livingHouse.owner == self.numID:
                            self.saleParticipation = True
                            self.rentParticipation = True
                        else:
                            self.saleParticipation = True
                            self.rentParticipation = False
                    else:
                        self.saleParticipation = False
                        self.rentParticipation = False
                else:
                    if self.livingHouse.owner == self.numID:
                        self.saleParticipation = True
                        self.rentParticipation = True
                    else:
                        self.saleParticipation = True
                        self.rentParticipation = False
            else:
                self.saleParticipation = False
                self.rentParticipation = False

            if self.saleParticipation == True or self.rentParticipation == True:
                self.setStateValue("state", 2)
            else:
                self.setStateValue("state", 24)

        elif strPort == "sendHouseInfo":

            # Buy process 5: select buy type (sale or rent)

            if self.rentParticipation == True:
                if random.random() <= self.saleProb:
                    self.rentParticipation = False
                else:
                    self.saleParticipation = False

            # Buy process 6: House select decision
            self.buyDecision = False
            lstHouses = objEvent.lstHouses
            if self.saleParticipation == True:
                for i in range(0, len(lstHouses)):
                    selectHouse = lstHouses[i]

                    taxAcquisition = selectHouse.calcAcquisitionTax()
                    amountDTI = self.calcDTIAmount(float(self.upperModel.DTI[self.objConfiguration.getConfiguration("time")]),\
                                                   float(self.upperModel.mortLoanInterestRate[self.objConfiguration.getConfiguration("time")]))
                    amountLTV = selectHouse.marketPriceSale*float(self.upperModel.LTV[self.objConfiguration.getConfiguration("time")])
                    affordableBudget = (min(amountDTI,amountLTV) + self.savings)*self.wtp
                    if affordableBudget >= selectHouse.marketPriceSale + taxAcquisition:
                        self.buyDecision = True
                        self.decideHouse = selectHouse
                        break

            elif self.rentParticipation == True:
                affordableRentDeposit = self.savings*self.wtp
                affordableRentFee = max((self.incomeWork - self.calcIncomeTax() + self.calcIncomeRent()) * (1 - self.consumptionRate) - self.calcPropertyTax() - self.calcMortRepaymentSum(), 0)

                for i in range(0, len(lstHouses)):
                    selectHouse = lstHouses[i]
                    if affordableRentDeposit + affordableRentFee/(float(self.upperModel.gamma[self.objConfiguration.getConfiguration("time")])/12)\
                            >= selectHouse.marketPriceRent:
                        self.buyDecision = True
                        self.decideHouse = selectHouse
                        break

            if self.buyDecision == True:
                self.setStateValue("state", 22)
            else:
                self.saleParticipation = False
                self.rentParticipation = False
                self.setStateValue("state", 24)

        elif strPort == "sendContractInfoBuy":
            self.dealingHouse = objEvent.dealingHouse
            self.dealingType = objEvent.dealingType
            if self.dealingType == "fail":
                self.saleParticipation = False
                self.rentParticipation = False
            self.setStateValue("state", 24)

        elif strPort == "sendContractInfoSell":
            dealingHouse = objEvent.dealingHouse
            dealingType = objEvent.dealingType

            if dealingType == "sale":
                self.savings = self.savings + dealingHouse.marketPriceSale - dealingHouse.mortLoan - dealingHouse.calcGainTax()
                if dealingHouse.resident == self.numID:
                    self.ownHouse.pop(self.ownHouse.index(dealingHouse))
                    self.livingHouse = None
                    dealingHouse.resident = -1
                else:
                    self.ownHouse.pop(self.ownHouse.index(dealingHouse))

            elif dealingType == "rent":
                if dealingHouse.resident == self.numID:
                    self.savings += dealingHouse.marketPriceRent
                    self.livingHouse = None
                    dealingHouse.resident = -1
                elif dealingHouse.resident is not None:
                    prevResident = self.lstHouseholdAgent[dealingHouse.resident]
                    prevResident.livingHouse = None
                    prevResident.savings += dealingHouse.rentDeposit
                    self.savings += dealingHouse.marketPriceRent - dealingHouse.rentDeposit
                    dealingHouse.resident = -1

            self.continueTimeAdvance()

        # about Update process
        elif strPort == "startUpdate":
            self.setStateValue("state", 3)

    def funcOutput(self):
        # about List process
        if self.getStateValue("state") == 1:

            # list process 1: Identify the number of vacant houses household agent have
            emptyHouseList = []
            for i in range (0, len(self.ownHouse)):
                if self.ownHouse[i].resident == -1:
                    emptyHouseList.append(self.ownHouse[i])

            # list process 2: Determine whether you are moving to a vacant house
            if self.livingHouse is None and len(emptyHouseList) > 0:
                selectIndex = random.randint(0, len(emptyHouseList) - 1)
                selectHouse = emptyHouseList[selectIndex]
                selectHouse.resident = self.numID
                selectHouse.contractPeriod = math.inf
                selectHouse.rentDeposit = 0
                selectHouse.rentFee = 0
                self.livingHouse = selectHouse
                emptyHouseList.pop(selectIndex)

            elif self.livingHouse is not None and self.livingHouse.owner == self.numID and len(emptyHouseList) > 0:
                if random.random() <= self.upperModel.moveProbability:
                    selectIndex = random.randint(0, len(emptyHouseList) - 1)
                    selectHouse = emptyHouseList[selectIndex]
                    selectHouse.resident = self.numID
                    selectHouse.contractPeriod = math.inf
                    selectHouse.rentDeposit = 0
                    selectHouse.rentFee = 0

                    livingHouse = self.livingHouse

                    livingHouse.resident = -1
                    livingHouse.contractPeriod = math.inf
                    livingHouse.rentDeposit = 0
                    livingHouse.rentFee = 0

                    self.livingHouse = selectHouse
                    emptyHouseList.pop(selectIndex)
                    emptyHouseList.append(livingHouse)


            # list process 3: if household agents have no empty house and saving is positive, end list process
            if len(emptyHouseList) == 0 and self.savings >= 0:
                objEvent1 = endListMessage(self.strID)
                self.addOutputEvent("endList", objEvent1)

            # list process 4: if household agents saving account is negative, list one random house
            elif len(emptyHouseList) == 0 and self.savings < 0:
                if len(self.ownHouse) > 0:
                    selectIndex = random.randint(0, len(self.ownHouse) - 1)
                    selectHouse = self.ownHouse[selectIndex]
                    emptyHouseList.append(selectHouse)
                    objEvent1 = endListMessage(self.strID)
                    self.addOutputEvent("endList", objEvent1)
                    objEvent2 = houseInfoMessage(emptyHouseList)  # one random house info should be added to message
                    self.addOutputEvent("requestList", objEvent2)
                else:
                    objEvent1 = endListMessage(self.strID)
                    self.addOutputEvent("endList", objEvent1)

            else:
                # list process 5: send a vacant house list to the realtor agent
                objEvent1 = endListMessage(self.strID)
                self.addOutputEvent("endList", objEvent1)
                objEvent2 = houseInfoMessage(emptyHouseList)  # vacant houses info should be added to message
                self.addOutputEvent("requestList", objEvent2)

        # about Buy process
        elif self.getStateValue("state") == 2:

            # Buy process 2: living region decision
            if self.region == 1:
                if random.random() < float(self.upperModel.capitalMoveRate[self.objConfiguration.getConfiguration("time")]):
                    selectRegion = 0
                else:
                    selectRegion = 1
            else:
                if random.random() < float(self.upperModel.nonCapitalMoveRate[self.objConfiguration.getConfiguration("time")]):
                    selectRegion = 1
                else:
                    selectRegion = 0

            # Buy process 3: House type decision
            selectType = int(np.argwhere(np.random.multinomial(1,\
                                                               [float(self.upperModel.houseTypeRatio1[self.objConfiguration.getConfiguration("time")]), \
                                                                float(self.upperModel.houseTypeRatio2[
                                                                          self.objConfiguration.getConfiguration(
                                                                              "time")]), \
                                                                float(self.upperModel.houseTypeRatio3[
                                                                          self.objConfiguration.getConfiguration(
                                                                              "time")])]) == 1)) + 1

            # Buy process 4: price upper & lower limit decision
            amountDTI = self.calcDTIAmount(float(self.upperModel.DTI[self.objConfiguration.getConfiguration("time")]),\
                                           float(self.upperModel.mortLoanInterestRate[self.objConfiguration.getConfiguration("time")]))

            selectUpper = self.savings + amountDTI
            selectLower = self.savings * self.wtp

            objEvent = houseClassMessage(self.numID, [selectRegion, selectType, selectUpper, selectLower])
            self.addOutputEvent("requestHouseInfo", objEvent)

        elif self.getStateValue("state") == 22:
            if self.saleParticipation == True:
                objEvent = decisionInfoMessage(self.numID, self.decideHouse, "sale")
            else:
                objEvent = decisionInfoMessage(self.numID, self.decideHouse, "rent")
            self.addOutputEvent("sendDecisionInfo", objEvent)

        elif self.getStateValue("state") == 24:

            if self.saleParticipation == True or self.rentParticipation == True:
                # Buy process 7: Buyer attribute and House attribute update
                if self.dealingType == "sale":
                    dealingPrice = self.dealingHouse.marketPriceSale + self.dealingHouse.calcAcquisitionTax()
                    if dealingPrice <= self.savings * self.wtp:
                        self.dealingHouse.owner = self.numID
                        self.dealingHouse.holdingPeriod = 0
                        self.dealingHouse.purchasePrice = self.dealingHouse.marketPriceSale
                        self.dealingHouse.mortLoan = 0
                        self.dealingHouse.mortRepayment = 0
                        self.dealingHouse.unsoldPeriod = 0
                        self.savings -= dealingPrice
                        self.ownHouse.append(self.dealingHouse)
                    else:
                        self.dealingHouse.owner = self.numID
                        self.dealingHouse.holdingPeriod = 0
                        self.dealingHouse.purchasePrice = self.dealingHouse.marketPriceSale
                        self.dealingHouse.mortLoan = dealingPrice - self.savings * self.wtp
                        self.dealingHouse.mortRepayment = self.dealingHouse.mortLoan*float(self.upperModel.mortLoanInterestRate[self.objConfiguration.getConfiguration("time")])\
                                                          *pow(1+float(self.upperModel.mortLoanInterestRate[self.objConfiguration.getConfiguration("time")]),self.upperModel.mortLoanMaturity)\
                                                          /(pow(1+float(self.upperModel.mortLoanInterestRate[self.objConfiguration.getConfiguration("time")]),self.upperModel.mortLoanMaturity)-1)
                        self.dealingHouse.unsoldPeriod = 0
                        self.savings = self.savings * (1 - self.wtp)
                        self.ownHouse.append(self.dealingHouse)


                elif self.dealingType == "rent":
                    self.dealingHouse.resident = self.numID
                    self.dealingHouse.contractPeriod = 24
                    self.dealingHouse.rentDeposit = min(self.dealingHouse.marketPriceRent, self.savings*self.wtp)
                    self.dealingHouse.rentFee = max(self.dealingHouse.marketPriceRent - self.dealingHouse.rentDeposit, 0)\
                                                *(float(self.upperModel.gamma[self.objConfiguration.getConfiguration("time")])/12)
                    self.savings -= self.dealingHouse.rentDeposit
                    if self.livingHouse is None:
                        self.livingHouse = self.dealingHouse
                    else:
                        self.livingHouse.resident = -1
                        self.livingHouse.contractPeriod = math.inf
                        self.livingHouse.rentDeposit = 0
                        self.livingHouse.rentFee = 0
                        self.livingHouse = self.dealingHouse

                #print("dealing perform success!!!!!")
            objEvent = endBuyMessage(self.strID)
            self.addOutputEvent("endBuy", objEvent)

        # about Update process
        if self.getStateValue("state") == 31:
            objEvent = endUpdateMessage(self.strID)
            self.addOutputEvent("endUpdate", objEvent)

    def funcInternalTransition(self):
        # about List process
        if self.getStateValue("state") == 1:
            self.setStateValue("state", 0)

        # about Buy process
        elif self.getStateValue("state") == 2:
            self.setStateValue("state", 21)
        elif self.getStateValue("state") == 22:
            self.setStateValue("state", 23)
        elif self.getStateValue("state") == 24:
            self.setStateValue("state", 0)

        # about Update process
        elif self.getStateValue("state") == 3:
            # update process 1: savings update related with income
            self.savings = self.savings*(1+float(self.upperModel.interestRate[self.objConfiguration.getConfiguration("time")]))\
                           + (self.incomeWork - self.calcIncomeTax() + self.calcIncomeRent())*(1-self.consumptionRate)
            self.incomeWork = self.incomeWork * (1 + float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")]))

            # update process 2: saving update related with rent (resident)
            if self.livingHouse is not None:
                self.savings -= self.livingHouse.rentFee
                self.livingHouse.contractPeriod -= 1
                if self.livingHouse.contractPeriod == 0:
                    self.savings += self.livingHouse.rentDeposit
                    self.livingHouse = None

            # update process 3: savings update related with loan
            if self.creditLoan <= self.creditRepayment:
                self.savings -= self.creditLoan
                self.creditLoan = 0
                self.creditRepayment = 0
            else:
                self.savings -= self.creditRepayment
                self.creditLoan = self.creditLoan*(1+float(self.upperModel.creditLoanInterestRate[self.objConfiguration.getConfiguration("time")])/12) - self.creditRepayment

            for i in range (0, len(self.ownHouse)):
                selectHouse = self.ownHouse[i]
                if selectHouse.mortLoan <= selectHouse.mortRepayment:
                    self.savings -= selectHouse.mortLoan
                    selectHouse.mortLoan = 0
                    selectHouse.mortRepayment = 0
                else:
                    self.savings -= selectHouse.mortRepayment
                    selectHouse.mortLoan = selectHouse.mortLoan*(1 + float(self.upperModel.mortLoanInterestRate[self.objConfiguration.getConfiguration("time")]) / 12) - selectHouse.mortRepayment

            # update process 4: savings update related with tax
            self.savings -= self.calcPropertyTax()

            self.setStateValue("state", 31)

        elif self.getStateValue("state") == 31:
            # update process 5: saving update related with rent (owner)
            for i in range (0, len(self.ownHouse)):
                selectHouse = self.ownHouse[i]
                if selectHouse.contractPeriod == 0:
                    self.savings -= selectHouse.rentDeposit
                    #print("!!! rent contract expired")
                    selectHouse.resident = -1
                    selectHouse.contractPeriod = math.inf
                    selectHouse.rentDeposit = 0
                    selectHouse.rentFee = 0

                # update process 6: house price update
                if self.upperModel.typePriority[selectHouse.type-1] is None or self.upperModel.typePriority[selectHouse.type-1] < self.upperModel.priorityThreshold:
                    selectHouse.marketPriceSale = int(selectHouse.marketPriceSale*(1+float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")])))
                    selectHouse.marketPriceRent = int(selectHouse.marketPriceRent*(1+float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")])))
                else:
                    if self.region == 0:
                        selectHouse.marketPriceSale = int(selectHouse.marketPriceSale*(1+float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")])\
                                                                                       + 2 * float(self.upperModel.mp_ir[self.objConfiguration.getConfiguration("time")])))
                        selectHouse.marketPriceRent = int(selectHouse.marketPriceRent*(1+float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")])\
                                                                                       +2 * float(self.upperModel.mp_ir[self.objConfiguration.getConfiguration("time")])))
                    else:
                        selectHouse.marketPriceSale = int(selectHouse.marketPriceSale * (1 + float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")]) \
                                                                                         + float(self.upperModel.mp_ir[self.objConfiguration.getConfiguration("time")])))
                        selectHouse.marketPriceRent = int(selectHouse.marketPriceRent * (1 + float(self.upperModel.inflationRate[self.objConfiguration.getConfiguration("time")]) \
                                                                                         + float(self.upperModel.mp_ir[self.objConfiguration.getConfiguration("time")])))
            self.setStateValue("state", 0)

    def funcTimeAdvance(self):
        if self.getStateValue("state") == 0:
            return math.inf

        # about List process
        elif self.getStateValue("state") == 1:
            return 1
            #return random.random()

        # about buy process
        elif self.getStateValue("state") == 2:
            return 1
        elif self.getStateValue("state") == 21: # wait HouseInfoMessage
            return math.inf
        elif self.getStateValue("state") == 22: # make buy decision
            return 1
        elif self.getStateValue("state") == 23: # wait contract decision
            return math.inf
        elif self.getStateValue("state") == 24: # end buy process
            return 1 # to make the seller agent's update performs before the buyer agent's update

        # about Update process
        elif self.getStateValue("state") == 3:
            return 1
            #return random.random()
        elif self.getStateValue("state") == 31:
            return 1

    def funcSelect(self):
        pass

    def calcIncomeRent(self):
        incomeRent = 0
        for i in range (0, len(self.ownHouse)):
            incomeRent += self.ownHouse[i].rentFee

        return incomeRent

    def calcMortRepaymentSum(self):
        mortRepaymentSum = 0
        for i in range (0, len(self.ownHouse)):
            mortRepaymentSum += self.ownHouse[i].mortRepayment

        return mortRepaymentSum

    def calcMortLoanSum(self):
        mortLoanSum = 0
        for i in range (0, len(self.ownHouse)):
            mortLoanSum += self.ownHouse[i].mortLoan

        return mortLoanSum

    # DTI calculation function (old)
    def calcDTIAmount(self, DTI, interestRate):

        n = self.objConfiguration.getConfiguration("mortLoanMaturity")

        incomeWork = self.incomeWork
        creditRepayment = self.creditRepayment

        incomeRent = 0
        mortRepayment = 0
        for i in range (0, len(self.ownHouse)):
            incomeRent += self.ownHouse[i].rentFee
            mortRepayment += self.ownHouse[i].mortRepayment

        amountDTI = (DTI*(incomeWork+incomeRent)-(creditRepayment+mortRepayment))*(pow(1+interestRate, n)-1)/(interestRate*pow(1+interestRate, n))
        return amountDTI

    def calcIncomeTax(self):
        taxIncomeRate1 = 0.06
        taxIncomeRate2 = 0.15
        taxIncomeRate3 = 0.24
        taxIncomeRate4 = 0.35
        taxIncomeRate5 = 0.38

        taxBase = self.incomeWork * 12

        if taxBase <= 12000:
            incomeTax = self.incomeWork*taxIncomeRate1
        elif taxBase > 12000 and taxBase <= 46000:
            incomeTax = self.incomeWork*taxIncomeRate2 - 1080/12
        elif taxBase > 46000 and taxBase <= 88000:
            incomeTax = self.incomeWork*taxIncomeRate3 - 5220/12
        elif taxBase > 88000 and taxBase <= 300000:
            incomeTax = self.incomeWork*taxIncomeRate4 - 14900/12
        elif taxBase > 300000:
            incomeTax = self.incomeWork*taxIncomeRate5 - 194000/12

        return incomeTax

    def calcPropertyTax(self):
        taxPropertyRate1 = 0.005
        taxPropertyRate2 = 0.0075
        taxPropertyRate3 = 0.01
        taxPropertyRate4 = 0.015
        taxPropertyRate5 = 0.02

        mortValue = 0
        for i in range(0, len(self.ownHouse)):
            mortValue += self.ownHouse[i].marketPriceSale
        taxBase = max(mortValue - 600000, 0)*0.8

        if taxBase <= 600000:
            propertyTax = (taxBase * taxPropertyRate1)/12
        elif taxBase > 600000 and taxBase <= 1200000:
            propertyTax = (taxBase * taxPropertyRate2 - 1500)/12
        elif taxBase > 1200000 and taxBase <= 5000000:
            propertyTax = (taxBase * taxPropertyRate3 - 4500)/12
        elif mortValue > 5000000 and mortValue <= 9400000:
            propertyTax = (taxBase * taxPropertyRate4 - 29500)/12
        elif mortValue > 9400000:
            propertyTax = (taxBase * taxPropertyRate5 - 76500)/12

        return propertyTax