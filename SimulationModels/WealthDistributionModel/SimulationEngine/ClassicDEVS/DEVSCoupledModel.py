#-*- coding:utf-8 -*-

from SimulationModels.WealthDistributionModel.SimulationEngine.ClassicDEVS.DEVSCoupling import DEVSCoupling
from SimulationModels.WealthDistributionModel.SimulationEngine.ClassicDEVS.DEVSModel import DEVSModel
from SimulationModels.WealthDistributionModel.SimulationEngine.CouplingGraph import CouplingEdge, CouplingNode
from SimulationModels.WealthDistributionModel.SimulationEngine.Utility.Logger import Logger

import sys
import numpy as np
import csv
sys.path.insert(0,'.')
import os

class DEVSCoupledModel(DEVSModel):

    def __init__(self, ID):
        super().__init__()
        self.models = {}
        self.edges = []
        self.nodesWithID = {}
        self.setModelID(ID)

    def addModel(self,model):
        self.models[model.getModelID()] = model
        model.setContainerModel(self)

    def getCurrentTime(self):
        #for modelID in self.models:
        #    print("싱글 스텝이 끝난 후 모든 모델들의 self.time값은 다음과 같습니다 :" + str(self.models[modelID].getModelID) + " : " + str(self.models[modelID].getCurrentTime()))
        return 0
    def setCurrentTime(self,currentTime):
        #print("!!! ENGINE : setCurrentTime : "+str(self.getModelID())+": Current Time : "+str(currentTime) ) #+" : Time : "+str(self.getTime()))
        for modelID in self.models:
            self.models[modelID].setCurrentTime(currentTime)

    def queryMinTimeAdvance(self): # 모든 submodel들의 시간을 다 체크한다음 가장 작은 시간의 submodel을 실행하려고 minTA를 설정한다
        #print("모든 Model들의 TimeAdvance를 물어본 다음 가장 작은 시간으로 minTA를 설정해줍니다.")
        minTA = sys.float_info.max
        for modelID in self.models:
            model = self.models[modelID]
            ta = model.queryTimeAdvance()
            if ta < minTA:
                minTA = ta
        self.logger.log(Logger.TA,"Query MIN TA (" + self.getModelID() + ") : " + str(minTA))
        #print("모든 Model들의 TimeAdvance를 물어보았습니다. minTA는 아래와 같습니다.")
        #print("Query MIN TA Coupled (" + self.getModelID() + ") : " + str(minTA))
        return minTA

    def queryMinTime(self):
        #print("모든 Model들의 시간을 물어본 다음 가장 작은 시간으로 nextTime을 세팅해줍니다.")
        nextTime = sys.float_info.max
        for modelID in self.models:
            model = self.models[modelID]
            time = model.queryTime()
            if time < nextTime:
                nextTime = time
        self.logger.log(Logger.TA,"Query Min Time (" + self.getModelID() + ") : " + str(nextTime))
        #print("모든 Model들의 시간을 물어보았습니다. nextTime은 아래와 같습니다.")
        #print("Query Min Time (" + self.getModelID() + ") : " + str(nextTime))
        return nextTime

    def performTimeAdvance(self,currentTime):
        #print("Coupled Model의 PerformTimeAdvance를 실행합니다.")
        self.time = currentTime
        maxWealth, minwealth = self.maxWealth()
        #if currentTime == 0:
        self.getMicroLevel()
        for modelID in self.models:
            #print(modelID, "와 같은 Atomic Model의 PerformTimeAdvance를 실행합니다 : ")
            modelNextTime = self.models[modelID].queryTime()
            #print("     CurrentTime ("+str(self.models[modelID].getModelID()) + ") : "+ str(currentTime))
            #print("Atomic Model queryTime : ", modelNextTime)
            if modelNextTime <= currentTime:
                #print("modelID", modelID)
                self.models[modelID].performTimeAdvance(currentTime,maxWealth, minwealth) # submodel이 실행됨, submodel의 다음번째 시간이 계산되어 나옴
            #else:
                #print("     !!! 현재 Child Model은 그냥 넘어가겠습니다.")
                #print("     !!! 태섭이가 고친 부분 실행 시작")
                #self.models[modelID].setCurrentTime(currentTime)
                #print("     !!! 만약 currentTime과 modelTime이 일치하면 원래 코드가 맞고 일치하지 않으면 태섭이가 수정한 것이 맞습니다.")
                #print("     !!! 사실은 아직 안고치고 있습니다.")
                #print("     !!! 현재 시뮬레이션 엔진의 currentTime : ", currentTime)
                #print("     !!! 현재 보고 있는 child model의 modelNextTime   : ", modelNextTime)
                #print("     !!! 현재 보고 있는 child model의 modelTime   : ", self.models[modelID].time)
                #print("     !!! 현재 보고 있는 child model의 modelTime   : ", )
                #print("     !!! 태섭이가 고친 부분 실행 끝")

    def maxWealth(self):
        maxwealth = 0
        minwealth = 100000000
        #print("AAAAAAAAAA")
        #print(self.models)
        for model in self.models:
            #print(self.models[model])
            #print("D : ", model.getStateValue("Wealth"))
            try:
                #print("C : ",(model.getStateValue("Wealth")))
                if maxwealth < float(self.models[model].getStateValue("Wealth")):
                    #print("AAA : ", self.models[model].getStateValue("Wealth"))
                    maxwealth = float(self.models[model].getStateValue("Wealth"))
                if minwealth > float(self.models[model].getStateValue("Wealth")):
                    minwealth = float(self.models[model].getStateValue("Wealth"))
            except:
                continue
                #print("BBBB")
        #print("AA : ",maxwealth)
        return maxwealth, minwealth

    def getMicroLevel(self):
        wealth = []
        for model in self.models:
            try:
                wealth.append(float(self.models[model].getStateValue("Wealth")))
            except:
                continue
        wealth_copy = wealth
        wealth_copy.sort()
        cent = wealth_copy[len(wealth)//2]
        low = wealth_copy[len(wealth)//3]
        high = wealth_copy[(len(wealth)*2)//3]

        for model in self.models:
            try:
                if float(self.models[model].getStateValue("Wealth")) <= cent:
                    self.models[model].setStateValue('Micro Level', 1)
                else:
                    self.models[model].setStateValue('Micro Level', 2)
                if float(self.models[model].getStateValue("Wealth")) <= low:
                    self.models[model].setStateValue('Wealth Level', 1)
                elif float(self.models[model].getStateValue("Wealth")) > low and float(self.models[model].getStateValue("Wealth")) <= high:
                    self.models[model].setStateValue('Wealth Level', 2)
                else:
                    self.models[model].setStateValue('Wealth Level', 3)
            except:
                continue

    def writeLogfile(self, currentTime, dir, itrCalibration):
        agent_wealth = [currentTime]
        #agent_level = [self.currentTime]
        level = [0,0,0]
        #print(self.models)
        for model in self.models:
            #print("???")
            #try:
                #print(model.getStateValue("Wealth"))
            #print(model)
            #print("UU : ",model.getStateValue("Wealth"))
            if self.models[model].getStateValue("Wealth") != None:
                agent_wealth.append(self.models[model].getStateValue("Wealth"))
                #if model.getStateValue("Wealth Level") != None:
                #print("KK : ",int(self.models[model].getStateValue("Wealth Level")))
                level[int(self.models[model].getStateValue("Wealth Level"))-1] += 1
            #except:
            #    print("BBB")
            #    continue
        total_population = 0
        for i in range(len(level)):
            total_population += level[i]
        for i in range(len(level)):
            level[i] = level[i]/total_population * 100

        #agent_wealth.append(np.mean(agent_wealth[1:]))
        #fileLog = open(os.path.dirname(os.path.realpath(__file__)) + "/../../WealthDistributionModel/Agent_Specific_Result/Result/" + "MicroResult_Wealth.csv", "a",newline='')
        #print("dir : ", dir)
        fileLog = open(dir + "MicroResult_Wealth"+str(itrCalibration)+".csv", "a", newline='')
        writer = csv.writer(fileLog)
        writer.writerow(agent_wealth[1:] + [np.mean(agent_wealth[1:])])
        fileLog.close()

        '''fileLog = open("../WealthDistributionModel/Result/" + "MicroResult_Level.csv", "a", newline='')
        writer = csv.writer(fileLog)
        writer.writerow([str(currentTime)]+level)
        fileLog.close()'''

        agent_wealth.sort()
        agent_wealth = agent_wealth[1:]

        numerator = 0
        denominator = 0
        sum_ = sum(agent_wealth)
        len_ = len(agent_wealth)
        accrued = 0
        #for i in range(len_):
            #accrued += agent_wealth[i]
            #numerator += (len_ - i) * ((float(i + 1) / 100.) * sum_ - accrued)
            #numerator += ((float(i) / float(len_)) * sum_ - accrued)
        for i in range(len_):
            for j in range(len_):
                numerator += abs(agent_wealth[i]-agent_wealth[j])
        for i in range(len_):
            denominator += 2*len_*agent_wealth[i]
        #denominator = sum_ * (len_) / 2.
        try:
            gini = numerator / denominator
        except:
            gini = 0.0
        '''fileLog = open("../WealthDistributionModel/Result/" + "MicroResult_Gini.csv", "a", newline='')
        writer = csv.writer(fileLog)
        writer.writerow([str(currentTime)] + [gini])
        fileLog.close()'''

        '''fileLog = open("../WealthDistributionModel/Result/" + "Macro_result.csv", "a", newline='')
        writer = csv.writer(fileLog)
        writer.writerow([str(currentTime)] + level + [gini])
        fileLog.close()'''

        return level[0], level[1], level[2], gini

    def writeLogfileHeterogeneous(self, currentTime, dir, itrCalibration):
        agent_wealth = [currentTime]
        level = [0,0,0]
        population = [0,0,0]
        for model in self.models:
            if self.models[model].getStateValue("Wealth") != None:
                agent_wealth.append(self.models[model].getStateValue("Wealth"))
                level[int(self.models[model].getStateValue("Wealth Level"))-1] += float(self.models[model].getStateValue("Wealth"))
                population[int(self.models[model].getStateValue("Wealth Level"))-1] += 1
            #except:
            #    print("BBB")
            #    continue
        for i in range(len(level)):
            level[i] = level[i]/population[i]
        #print("level : ", level)
        #fileLog = open(dir + "MicroResult_Wealth"+str(itrCalibration)+".csv", "a", newline='')
        #writer = csv.writer(fileLog)
        #writer.writerow(agent_wealth[1:] + [np.mean(agent_wealth[1:])])
        #fileLog.close()

        agent_wealth.sort()
        agent_wealth = agent_wealth[1:]

        numerator = 0
        denominator = 0
        sum_ = sum(agent_wealth)
        len_ = len(agent_wealth)
        accrued = 0
        for i in range(len_):
            for j in range(len_):
                numerator += abs(agent_wealth[i]-agent_wealth[j])
        for i in range(len_):
            denominator += 2*len_*agent_wealth[i]
        #denominator = sum_ * (len_) / 2.
        try:
            gini = numerator / denominator
        except:
            gini = 0.0

        return level[0], level[1], level[2], gini

    def sum(self,list):
        summ = 0
        for i in range(len(list)):
            summ += list[i]
        return summ

    def queryTimeAdvance(self):
        return self.queryMinTimeAdvance()

    def queryTime(self):
        return self.queryMinTime()

    def getModels(self):
        return self.models

    def getCouplingNodes(self):
        return self.nodesWithID

    def getCouplingEdges(self):
        return self.edges

    def addExternalOutputCoupling(self,srcModel,srcPort,tarPort):
        self.addCoupling(srcModel, srcPort, self, tarPort)

    def addExternalInputCoupling(self, srcPort, tarModel, tarPort):
        self.addCoupling(self, srcPort, tarModel, tarPort)

    def addInternalCoupling(self, srcModel, srcPort, tarModel, tarPort):
        self.addCoupling(srcModel, srcPort, tarModel, tarPort)

    def addCoupling(self, srcModel, srcPort, tarModel, tarPort): # nodesWithID에는 EIC, EOC, IC 등이 들어갈 수 있음
        if srcModel.getModelID() + "(" + srcPort + ")" in self.nodesWithID:
            srcNode = self.nodesWithID[srcModel.getModelID() + "(" + srcPort + ")"]
        else:
            srcNode = CouplingNode(srcModel, srcModel.getModelID(), srcPort) # CouplingGraph에 있는 클래스
            self.nodesWithID[srcModel.getModelID() + "(" + srcPort + ")"] = srcNode

        if tarModel.getModelID() + "(" + tarPort + ")" in self.nodesWithID:
            tarNode = self.nodesWithID[tarModel.getModelID() + "(" + tarPort + ")"]
        else:
            tarNode = CouplingNode(tarModel, tarModel.getModelID(), tarPort)
            self.nodesWithID[tarModel.getModelID() + "(" + tarPort + ")"] = tarNode

        edge = CouplingEdge(srcNode, tarNode) # CouplingEdge의 input 하나 하나는 self.nodesWithID의 list 원소들
        self.edges.append(edge)
        if self.getSimulationEngine() != -1:
            self.getSimulationEngine().getCouplingGraph().addEdge(edge)
        #for i in self.nodesWithID.keys():
        #    print("!!! nodesWithID : " + str(i))

    def getCoupling(self):
        ret = []
        for edge in self.edges:
            ret.append(DEVSCoupling(edge.srcNode.getModel(), edge.srcNode.getPort(), edge.tarNode.getModel(),
                                    edge.tarNode.getPort()))
        return ret

if __name__ == "__main__":
    pass