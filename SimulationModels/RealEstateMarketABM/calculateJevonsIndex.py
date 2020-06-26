import numpy as np
import csv
import sys

def calculateSimpleJevonsIndex(running_folder, currentCandidate, currentReplication, numReplication, marketSalePrices, marketRentPrices, regions, houseTypes):
    numTime = len(marketSalePrices)
    numHouses = len(marketSalePrices[0])
    Jevons = [[100.],[100.]]
    for time in range(1,numTime):
        tempCapital = 0
        numCapital = 0
        tempNonCapital = 0
        numNonCapital = 0
        for house in range(numHouses):
            if regions[time][house] == 0:
                tempCapital += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                numCapital += 1
            else:
                tempNonCapital += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                numNonCapital += 1
        tempCapital *= 1./numCapital
        tempNonCapital *= 1./numNonCapital
        Jevons[0].append(100 * np.exp(tempCapital))
        Jevons[1].append(100 * np.exp(tempNonCapital))
        
    file = open(running_folder + "/JevonsIndex_" + str(currentCandidate * numReplication + currentReplication) + ".csv", 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(Jevons[0])
    writer.writerow(Jevons[1])
    file.close()


def calculateJevonsIndex(running_folder, currentCandidate, currentReplication, numReplication, marketSalePrices,
                         marketRentPrices, regions, houseTypes):
    numTime = len(marketSalePrices)
    numHouses = len(marketSalePrices[0])
    Jevons = [['Capital Detached Sale', 100.], ['Capital Detached Rent', 100.], ['Capital Apartment Sales', 100.], \
              ['Capital Apartment Rent', 100.], ['Capital Multiplex Sale', 100.], ['Capital Multiplex Rent', 100.], \
              ['NonCapital Detached Sale', 100.], ['NonCapital Detached Rent', 100.], ['NonCapital Apartment Sales', 100.], \
              ['NonCapital Apartment Rent', 100.], ['NonCapital Multiplex Sale', 100.], ['NonCapital Multiplex Rent', 100.]] 
    for time in range(1, numTime):
        tempCapitalAptSale = 0
        tempCapitalAptRent = 0
        tempCapitalDetSale = 0
        tempCapitalDetRent = 0
        tempCapitalMulSale = 0
        tempCapitalMulRent = 0
        numCapitalApt = 0
        numCapitalDet = 0
        numCapitalMul = 0
        tempNonCapitalAptSale = 0
        tempNonCapitalAptRent = 0
        tempNonCapitalDetSale = 0
        tempNonCapitalDetRent = 0
        tempNonCapitalMulSale = 0
        tempNonCapitalMulRent = 0
        numNonCapitalApt = 0
        numNonCapitalDet = 0
        numNonCapitalMul = 0
        tempCapital = 0
        tempNonCapital = 0
        numNonCapital = 0
        for house in range(numHouses):
            if regions[time][house] == 0:
                if houseTypes[time][house] == 1:
                    tempCapitalDetSale += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                    tempCapitalDetRent += np.log(marketRentPrices[time][house]) - np.log(marketRentPrices[0][house])
                    numCapitalDet += 1
                elif houseTypes[time][house] == 2:
                    tempCapitalAptSale += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                    tempCapitalAptRent += np.log(marketRentPrices[time][house]) - np.log(marketRentPrices[0][house])
                    numCapitalApt += 1
                elif houseTypes[time][house] == 3:
                    tempCapitalMulSale += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                    tempCapitalMulRent += np.log(marketRentPrices[time][house]) - np.log(marketRentPrices[0][house])
                    numCapitalMul += 1
            else:
                if houseTypes[time][house] == 1:
                    tempNonCapitalDetSale += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                    tempNonCapitalDetRent += np.log(marketRentPrices[time][house]) - np.log(marketRentPrices[0][house])
                    numNonCapitalDet += 1
                elif houseTypes[time][house] == 2:
                    tempNonCapitalAptSale += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                    tempNonCapitalAptRent += np.log(marketRentPrices[time][house]) - np.log(marketRentPrices[0][house])
                    numNonCapitalApt += 1
                elif houseTypes[time][house] == 3:
                    tempNonCapitalMulSale += np.log(marketSalePrices[time][house]) - np.log(marketSalePrices[0][house])
                    tempNonCapitalMulRent += np.log(marketRentPrices[time][house]) - np.log(marketRentPrices[0][house])
                    numNonCapitalMul += 1
        tempCapitalDetSale *= 1. / numCapitalDet
        tempCapitalDetRent *= 1. / numCapitalDet
        tempCapitalAptSale *= 1. / numCapitalApt
        tempCapitalAptRent *= 1. / numCapitalApt
        tempCapitalMulSale *= 1. / numCapitalMul
        tempCapitalMulRent *= 1. / numCapitalMul
        tempNonCapitalDetSale *= 1. / numNonCapitalDet
        tempNonCapitalDetRent *= 1. / numNonCapitalDet
        tempNonCapitalAptSale *= 1. / numNonCapitalApt
        tempNonCapitalAptRent *= 1. / numNonCapitalApt
        tempNonCapitalMulSale *= 1. / numNonCapitalMul
        tempNonCapitalMulRent *= 1. / numNonCapitalMul
        Jevons[0].append(100 * np.exp(tempCapitalDetSale))
        Jevons[1].append(100 * np.exp(tempCapitalDetRent))
        Jevons[2].append(100 * np.exp(tempCapitalAptSale))
        Jevons[3].append(100 * np.exp(tempCapitalAptRent))
        Jevons[4].append(100 * np.exp(tempCapitalMulSale))
        Jevons[5].append(100 * np.exp(tempCapitalMulRent))
        Jevons[6].append(100 * np.exp(tempNonCapitalDetSale))
        Jevons[7].append(100 * np.exp(tempNonCapitalDetRent))
        Jevons[8].append(100 * np.exp(tempNonCapitalAptSale))
        Jevons[9].append(100 * np.exp(tempNonCapitalAptRent))
        Jevons[10].append(100 * np.exp(tempNonCapitalMulSale))
        Jevons[11].append(100 * np.exp(tempNonCapitalMulRent))

    file = open(running_folder + "/PriceIndex_candidate_" + str(currentCandidate) + "_replication_" +
                str(currentReplication) + ".csv",
                'w', newline='')
    writer = csv.writer(file)
    for i in range(len(Jevons)):
        writer.writerow(Jevons[i])
    #file.flush()
    #writer.writerow(Jevons[0])
    #writer.writerow(Jevons[1])
    file.close()