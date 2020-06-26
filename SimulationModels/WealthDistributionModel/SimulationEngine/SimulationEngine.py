#-*- coding:utf-8 -*-

import sys
import csv
import numpy as np

#sys.path.insert(0,'../SimulationEngine')
from SimulationModels.WealthDistributionModel.SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from SimulationModels.WealthDistributionModel.SimulationEngine.CouplingGraph import *
from SimulationModels.WealthDistributionModel.SimulationEngine.Utility.Logger import Logger
from SimulationModels.WealthDistributionModel.SimulationEngine.Visualzer.Visualizer import Visualizer
from SimulationModels.WealthDistributionModel.SimulationEngine.Utility.Event import *

class SimulationEngine: # 엔진 자체는 최상위 모델로써, 시뮬레이션의 전체 시간을 관리하는 객체임
# 시간진행 관리, 모델 실행 및 메시지 전송을 계층적 협업을 통해 수행
    def __init__(self):
        self.models = []
        self.queueEvent = []
        self.visualNodes = []
        self.visualEdges = []

    def setOutmostModel(self,model):
        self.model = model
        self.models.append(model)
        self.couplingGraph = CouplingGraph(self)

        modelBFS = [model]
        #print("modelBFS : ", modelBFS)
        while len(modelBFS) != 0:
            currentModel = modelBFS.pop(0)
            #print("currentModel : ", currentModel)
            #print(isinstance(currentModel,DEVSCoupledModel))
            if isinstance(currentModel,DEVSCoupledModel) == True:
                children = currentModel.getModels()
                for childModelID in children:
                    children[childModelID].setSimulationEngine(self)
                    modelBFS.append(children[childModelID])
                    self.models.append(children[childModelID])

                # EIC, EOC, IC 등을 불러오는 것
                nodes = currentModel.getCouplingNodes()
                edges = currentModel.getCouplingEdges()
                #for i in nodes.keys():
                #    print("!!! IC NODES !!! " + str(i)) # 여기선 IC의 반쪽만 나옴 ex. models.out
                #for i in range(len(edges)):
                #    print("!!! IC !!! " + str(edges[i])) # 여기선 IC가 나옴 ex. (models.out,models.in)
                for nodeID in nodes:
                    self.couplingGraph.addNode(nodes[nodeID])
                for edge in edges:
                    self.couplingGraph.addEdge(edge)

    def addEvent(self,event):
        self.queueEvent.append(event)

    def run(self,maxTime = -1,ta=-1,visualizer=False,logFileName=-1,logGeneral=False,logActivateState=False,logActivateMessage=False,logActivateTA=False,logStructure=False, directory = '', itrCalibration=0):
        self.itrCalibration = itrCalibration
        self.dir = directory
        self.maxTime = maxTime
        self.ta = ta
        self.logger = Logger(self,logFileName,logGeneral,logActivateState,logActivateMessage,logActivateTA,logStructure)

        self.runInitialize()
        if visualizer == True:
            self.runWithVisualizer()
        else:
            Low, Middle, High, Gini = self.runWithoutVisualizer()
        return Low, Middle, High, Gini

    def runWithVisualizer(self):
        self.minTA = 0
        if self.maxTime <= 0:
            self.maxTime = 10000
        self.visualizer = Visualizer(self,self.maxTime)

    def runWithoutVisualizer(self):
        self.minTA = 0
        flag = 0
        LOW = []
        MIDDLE = []
        HIGH = []
        GINI = []
        while ( self.maxTime == -1 and self.minTA < sys.float_info.max ) or self.currentTime < self.maxTime: # currentTime: 최상위에서 시뮬레이션의 전체 시간을 관리함
            #print("----------------runWithoutVisualizer의 while문이 시작합니다.")
            self.runSingleStep()
            if self.currentTime == flag:
                for model in self.models:
                    model.getCurrentTime()
                    # 동준's recommendation! 시간이 없어서 ad-hoc으로 만들었습니다.
                    # model.setCurrentTime(self.currentTime)
                low, middle, high, gini = self.model.writeLogfileHeterogeneous(self.currentTime, self.dir, self.itrCalibration)

                LOW.append(low)
                MIDDLE.append(middle)
                HIGH.append(high)
                GINI.append(gini)
                flag += 1
            #print("----------------runWithoutVisualizer의 while문이 끝났습니다. 끝난 후의 currentTime과 minTA는 다음과 같습니다.")
            #print("currentTime: " + str(self.currentTime))
            #print("minTA : ", self.minTA)
            #self.model.queryMinTimeAdvance()

        return LOW, MIDDLE, HIGH, GINI

    def runInitialize(self):
        self.currentTime = 0
        #print("초기화중입니다..")
        #for i in range(len(self.models)):
        #    print("I am submodels in Engine : ", self.models[i])
        for model in self.models:
            model.setLogger(self.logger)
            if isinstance(model,DEVSAtomicModel) == True:
                model.setTime(self.currentTime)
                model.execTimeAdvance()
        #print("초기화 끝")
    def runSingleStep(self):
        self.logger.log(Logger.GENERAL, "-------------------------------------------")
        self.logger.log(Logger.GENERAL, "Simulation Time : " + str(self.currentTime))
        #print("-----------------Simulation Time : " + str(self.currentTime))
        self.logger.log(Logger.GENERAL, "-------------------------------------------")

        self.visualNodes = []
        self.visualEdges = []
        for model in self.models:
            self.logger.log(Logger.STATE, model.getModelID() + " : " + str(model.getStates()))
            for visualNode in model.getVisualNodes():
                self.visualNodes.append(visualNode)
            for visualEdge in model.getVisualEdges():
                self.visualEdges.append(visualEdge)
        #for i in range(len(self.queueEvent)):
        #    print("Queue : " + str(self.queueEvent[i]))
        for event in self.queueEvent:
            self.logger.log(Logger.MESSAGE,
                            event.getSenderModel().getModelID() + "(" + event.getSenderPort() + ")" + ":" + str(
                                event.getMessage()))

        if len(self.queueEvent) == 0:
            #print("발생한 이벤트가 없습니다.")
            self.minTA = self.model.queryMinTimeAdvance() # 모든 submodel들의 시간 체크! 어떤 submodel이
            #print("!!! minTA: " + str(self.minTA))
            if self.minTA == sys.float_info.max:
                self.logger.log(Logger.GENERAL, "Terminate by finding the minimum time advance as infinite\n")
                #print("Every agent did not move!!!!")
                sys.exit()
                #self.minTA = 1
            if self.ta != -1:
                self.minTA = self.ta
            self.currentTime = self.currentTime + self.minTA
            #print("currentTime 업데이트 완료!")
            #print("minTA : ",self.minTA)
            # self.queueEvent를 생성(명세서에 적힌 addOutputEvent를 통해)
            self.model.performTimeAdvance(self.currentTime) # currentTime인 시간을 가지고 있는 submodel들을 전부 실행

            #for i in range(len(self.queueEvent)):
            #    print("Queue : " + str(self.queueEvent[i]))
            #print("which agent? ", self.model.ID)
            #print("--------------------")

        else:
            #print("대기하고 있는 이벤트가 있어서 처리하는 중입니다.")
            while len(self.queueEvent) != 0:
                idxToPop = 0
                for itr in range(len(self.queueEvent)):
                    if isinstance(self.queueEvent[idxToPop],ResolutionEvent) == True:
                        if isinstance(self.queueEvent[itr],RecursionError) == False:
                            idxToPop = itr
                event = self.queueEvent.pop(idxToPop)
                #print(event)
                self.couplingGraph.broadcastEvent(event, self.currentTime)
        #print("!!! minTA: " + str(self.minTA))

    def getTime(self):
        return self.currentTime

    def getVisualNodes(self):
        return self.visualNodes

    def getVisualEdges(self):
        return self.visualEdges

    def getCouplingGraph(self):
        return self.couplingGraph

if __name__ == "__main__":
    pass