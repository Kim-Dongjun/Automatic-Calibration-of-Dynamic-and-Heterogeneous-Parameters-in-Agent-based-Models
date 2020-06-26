import math
import random

class House:

    def __init__(self, upperModel):
        self.upperModel = upperModel

    def makeHouse(self, numID, rawDataLine, objConfiguration):

        self.objConfiguration = objConfiguration
        jeonseExRate = float(self.upperModel.jeonseExchangeRate[self.objConfiguration.getConfiguration("time")])  # jeonse exchange rate
        mortLoanInterestRate = float(self.objConfiguration.getConfiguration("mortLoanInterestRate")[self.objConfiguration.getConfiguration("time")])
        n_mort = self.objConfiguration.getConfiguration("mortLoanMaturity")
        pricePerSize1 = float(self.upperModel.houseTypePrice1[self.objConfiguration.getConfiguration("time")])
        pricePerSize2 = float(self.upperModel.houseTypePrice2[self.objConfiguration.getConfiguration("time")])
        pricePerSize3 = float(self.upperModel.houseTypePrice3[self.objConfiguration.getConfiguration("time")])
        pricePerSize = [pricePerSize1*10, pricePerSize2*10, pricePerSize3*10]
        gamma = float(self.upperModel.gamma[self.objConfiguration.getConfiguration("time")])   # deposit rental fee exchange rate

        # owner household
        if rawDataLine[9] == "1":

            # House property - Object info
            self.numID = numID
            if rawDataLine[20] == "A0401":
                self.region = 1
            elif rawDataLine[20] == "A0402":
                self.region = 0
            self.type = int(rawDataLine[7])
            self.size = int(rawDataLine[8])

            # House property - Owner info
            self.owner = numID
            self.marketPriceSale = int(rawDataLine[12])
            self.marketPriceRent = self.marketPriceSale * jeonseExRate
            self.holdingPeriod = 0
            self.purchasePrice = self.marketPriceSale
            self.mortLoan = int(rawDataLine[15])
            self.mortRepayment = self.mortLoan*mortLoanInterestRate*pow(1+mortLoanInterestRate,n_mort)/(pow(1+mortLoanInterestRate,n_mort)-1)
            self.unsoldPeriod = 0

            # House property - Resident info
            self.resident = numID
            self.contractPeriod = math.inf
            self.rentDeposit = 0
            self.rentFee = 0

        # resident household
        elif rawDataLine[9] == "2" or "3" or "4":

            # House property - Object info
            self.numID = numID
            if rawDataLine[20] == "A0401":
                self.region = 1
            elif rawDataLine[20] == "A0402":
                self.region = 0
            self.type = int(rawDataLine[7])
            self.size = int(rawDataLine[8])

            # House property - Owner info
            self.owner = -1
            self.marketPriceSale = self.size*pricePerSize[self.type-1]  # type index start from 1
            self.marketPriceRent = self.marketPriceSale * jeonseExRate
            self.holdingPeriod = 0
            self.purchasePrice = self.marketPriceSale
            self.mortLoan = 0
            self.mortRepayment = 0
            self.unsoldPeriod = 0

            # House property - Resident info
            self.resident = numID
            self.contractPeriod = random.randrange(1, 25)
            self.rentDeposit = int(rawDataLine[11])
            self.rentFee = max(self.marketPriceRent-self.rentDeposit, 0) * gamma/12

    def makeEmptyHouse(self, numID, rawDataLine, objConfiguration):

        self.objConfiguration = objConfiguration
        jeonseExRate = float(self.upperModel.jeonseExchangeRate[self.objConfiguration.getConfiguration("time")])  # jeonse exchange rate
        pricePerSize1 = float(self.upperModel.houseTypePrice1[self.objConfiguration.getConfiguration("time")])
        pricePerSize2 = float(self.upperModel.houseTypePrice2[self.objConfiguration.getConfiguration("time")])
        pricePerSize3 = float(self.upperModel.houseTypePrice3[self.objConfiguration.getConfiguration("time")])
        pricePerSize = [pricePerSize1, pricePerSize2, pricePerSize3]

        # owner household
        if rawDataLine[9] == "1":

            # House property - Object info
            self.numID = numID
            if rawDataLine[20] == "A0401":
                self.region = 1
            elif rawDataLine[20] == "A0402":
                self.region = 0
            self.type = int(rawDataLine[7])
            self.size = int(rawDataLine[8])

            # House property - Owner info
            self.owner = -1
            self.marketPriceSale = int(rawDataLine[12])
            self.marketPriceRent = self.marketPriceSale * jeonseExRate
            self.holdingPeriod = 0
            self.purchasePrice = self.marketPriceSale
            self.mortLoan = 0
            self.mortRepayment = 0
            self.unsoldPeriod = 0

            # House property - Resident info
            self.resident = -1
            self.contractPeriod = math.inf
            self.rentDeposit = 0
            self.rentFee = 0

        # resident household
        elif rawDataLine[9] == "2" or "3" or "4":

            # House property - Object info
            self.numID = numID
            if rawDataLine[20] == "A0401":
                self.region = 1
            elif rawDataLine[20] == "A0402":
                self.region = 0
            self.type = int(rawDataLine[7])
            self.size = int(rawDataLine[8])

            # House property - Owner info
            self.owner = -1
            self.marketPriceSale = self.size * pricePerSize[self.type - 1]  # type index start from 1
            self.marketPriceRent = self.marketPriceSale * jeonseExRate
            self.holdingPeriod = 0
            self.purchasePrice = self.marketPriceSale
            self.mortLoan = 0
            self.mortRepayment = 0
            self.unsoldPeriod = 0

            # House property - Resident info
            self.resident = -1
            self.contractPeriod = math.inf
            self.rentDeposit = 0
            self.rentFee = 0

    def calcAcquisitionTax(self):
        taxAcquisitionRate1 = 0.01
        taxAcquisitionRate2 = 0.02
        taxAcquisitionRate3 = 0.03

        if self.marketPriceSale <= 60000:
            taxAcquisition = self.marketPriceSale * taxAcquisitionRate1
        elif self.marketPriceSale > 60000 and self.marketPriceSale <= 90000:
            taxAcquisition = self.marketPriceSale * taxAcquisitionRate2
        else:
            taxAcquisition = self.marketPriceSale * taxAcquisitionRate3

        return taxAcquisition

    def calcGainTax(self):
        taxGainRate1 = 0.06
        taxGainRate2 = 0.15
        taxGainRate3 = 0.24
        taxGainRate4 = 0.35
        taxGainRate5 = 0.38

        taxBase = self.marketPriceSale - self.purchasePrice

        if taxBase <= 12000:
            gainTax = taxBase * taxGainRate1
        elif taxBase > 12000 and taxBase <= 46000:
            gainTax = taxBase * taxGainRate2 - 1080
        elif taxBase > 46000 and taxBase <= 88000:
            gainTax = taxBase * taxGainRate3 - 5220
        elif taxBase > 88000 and taxBase <= 300000:
            gainTax = taxBase * taxGainRate4 - 14900
        elif taxBase > 300000:
            gainTax = taxBase * taxGainRate5 - 194000
        return gainTax