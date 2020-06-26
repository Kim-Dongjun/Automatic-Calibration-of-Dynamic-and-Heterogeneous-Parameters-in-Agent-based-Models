#-*- coding:utf-8 -*-

import random
import sys
from SimulationModels.WealthDistributionModel.SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from SimulationModels.WealthDistributionModel.SimulationMessage import AgentMovement,GridInfo,DustPropagation
import numpy as np
import operator
import os

class HouseHoldAgent(DEVSAtomicModel):

    def __init__(self, objConfiguration, strID,strInitialGridID,x,y,maxX,maxY,vision,wealth,economicIncome,economicOutcome,
                 age,lifeExpectancy,gridWealth,gridNumAgents,dicInitialGridInfo,candidate, dynamicParameter, heterogeneousParameter):
        super().__init__(strID)

        self.objConfiguration = objConfiguration
        #print("Model ID : ", self.getModelID())
        #print("ID : ", strID)
        self.setStateValue("ID", strID)
        self.setStateValue("GridX", str(x))
        self.setStateValue("GridY", str(y))
        self.setStateValue("MaxGridX", str(maxX))
        self.setStateValue("MaxGridY", str(maxY))
        self.setStateValue("CurrentGridID", strInitialGridID+str(x)+','+str(y))
        #self.setStateValue("NextGridID", strInitialGridID+str(x)+','+str(int(y+1)%int(self.getStateValue("MaxGridY"))))
        self.setStateValue("NextGridID",None)
        self.setStateValue("Income", economicIncome)
        self.setStateValue("Outcome", economicOutcome)
        self.setStateValue("Age", age)
        self.setStateValue("Wealth", wealth)
        self.setStateValue("Life_expectancy", lifeExpectancy)
        self.setStateValue("MaxWealth", 0)
        self.setStateValue("Vision", vision)
        self.setStateValue("GridWealth", gridWealth)
        self.setStateValue("GridNumAgents", gridNumAgents)
        self.setStateValue("Received Grid Info", False)
        self.setStateValue("Request Grid Info", False)
        self.setStateValue("Ready Move", True)
        self.setStateValue("Initialized", False)
        self.setStateValue("Arrived", False)
        self.setStateValue("Grid Info Dictionary", dicInitialGridInfo)
        self.setStateValue("NextGrid Travel Time",1)
        self.setStateValue("Wealth Level", 1)
        self.setStateValue("Micro Level", 1)
        self.setStateValue("Moving Probability", 0.5)
        self.setStateValue("candidate", candidate)
        self.strInitialGridID = strInitialGridID
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.dynamicParameter = dynamicParameter
        self.heterogeneousParameter = heterogeneousParameter

    def funcExternalTransition(self, strPort, objEvent, currentTime):
        #print("!!! "+self.getStateValue("ID")+"_Ext"+","+strPort)
        #print("Port : ", strPort)
        if strPort == "send_grid_info_"+self.getStateValue("ID"):
            #print("Am I Here?")
            if self.getStateValue("Request Grid Info") == True:
                dicGridInfo = self.getStateValue("Grid Info Dictionary")
                #print("!!! update grid info : "+objEvent.strGridID)
                dicGridInfo[objEvent.strGridID] = objEvent
                self.setStateValue("GridWealth", objEvent.dblGridWealth)
                self.setStateValue("GridNumAgents", objEvent.intHoldingAgent)
                self.setStateValue("Received Grid Info",True)
                self.setStateValue("Request Grid Info", False)
                self.setStateValue("Ready Move", False)
                bull = 1.5
                bare = 0.5
                w_ = float(self.getStateValue("GridWealth")) / float(self.getStateValue("GridNumAgents"))
                self.setStateValue("Income", (self.dynamicParameter[0][int(self.getStateValue("candidate"))][currentTime]) * w_)
                self.setStateValue("Outcome", float(self.heterogeneousParameter[0][int(self.getStateValue("Micro Level"))-1]) * w_)
                self.setStateValue("Wealth", float(self.getStateValue("Wealth")) + float(self.getStateValue("Income")) - float(self.getStateValue("Outcome")))

    def funcOutput(self):
        if self.getStateValue("Ready Move") == True:
            self.setStateValue("Request Grid Info",True)
            if self.getStateValue("Initialized") == False:
                objMovement = AgentMovement(None,self.getStateValue("CurrentGridID"),self.getModelID())
                self.addOutputEvent("enter_grid_" + self.getStateValue("CurrentGridID"), objMovement)
                self.setStateValue("Initialized", True)
                return
            if self.getStateValue("NextGridID") != None:
                objMovement = AgentMovement(self.getStateValue("CurrentGridID"), self.getStateValue("NextGridID"), self.getModelID())
                self.addOutputEvent("enter_grid_" + self.getStateValue("NextGridID"), objMovement)
                self.addOutputEvent("leave_grid_" + self.getStateValue("CurrentGridID"), objMovement)
            else:
                objMovement = AgentMovement(self.getStateValue("CurrentGridID"),"None",self.getModelID())
                self.addOutputEvent("leave_grid_" + self.getStateValue("CurrentGridID"), objMovement)
                self.setStateValue("Arrived", True)

    def calculateWealthLevel(self,maxwealth, minwealth):
        list = [minwealth, (2.*minwealth + maxwealth)/3., (minwealth + 2.*maxwealth)/3., maxwealth]
        for i in range(1,len(list)):
            if self.getStateValue("Wealth") <= list[i] and self.getStateValue("Wealth") >= list[i-1]:
                self.setStateValue("Wealth Level", i)

    def funcInternalTransition(self, maxwealth, minwealth):
        if self.getStateValue("Received Grid Info") == True:
            self.setStateValue("Received Grid Info", False)
            self.setStateValue("Ready Move", True)
            self.calculateWealthLevel(maxwealth, minwealth)
            dir = {}
            up = []
            down = []
            right = []
            left = []
            for i in range(int(self.getStateValue("Vision"))):
                up.append(float(self.getStateValue("Grid Info Dictionary")[
                                    'GridAgent_' + str(int(self.getStateValue("GridX"))) + ',' + str(
                                        (int(self.getStateValue("GridY")) + (i + 1)) % int(
                                            self.getStateValue("MaxGridY")))].gridWealth())
                          /float(self.getStateValue("Grid Info Dictionary")[
                                     'GridAgent_' + str(int(self.getStateValue("GridX"))) + ',' + str(
                                         (int(self.getStateValue("GridY")) + (i + 1)) % int(
                                             self.getStateValue("MaxGridY")))].numAgent()+1)
                                 )
                down.append(float(self.getStateValue("Grid Info Dictionary")[
                                      'GridAgent_' + str(int(self.getStateValue("GridX"))) + ',' + str(
                                          (int(self.getStateValue("GridY")) - (i + 1)) % int(
                                              self.getStateValue("MaxGridY")))].gridWealth())
                            / float(self.getStateValue("Grid Info Dictionary")[
                                        'GridAgent_' + str(int(self.getStateValue("GridX"))) + ',' + str(
                                          (int(self.getStateValue("GridY")) - (i + 1)) % int(
                                              self.getStateValue("MaxGridY")))].numAgent() + 1)
                            )
                right.append(float(self.getStateValue("Grid Info Dictionary")[
                                       'GridAgent_' + str((int(self.getStateValue("GridX")) + (i + 1)) % int(
                                           self.getStateValue("MaxGridX"))) + ',' + str(
                                           int(self.getStateValue("GridY")))].gridWealth())
                / float(self.getStateValue("Grid Info Dictionary")[
                                       'GridAgent_' + str((int(self.getStateValue("GridX")) + (i + 1)) % int(
                                           self.getStateValue("MaxGridX"))) + ',' + str(
                                           int(self.getStateValue("GridY")))].numAgent()+1))
                left.append(float(self.getStateValue("Grid Info Dictionary")[
                                      'GridAgent_' + str((int(self.getStateValue("GridX")) - (i + 1)) % int(
                                          self.getStateValue("MaxGridX"))) + ',' + str(
                                          int(self.getStateValue("GridY")))].gridWealth())
                            / float(self.getStateValue("Grid Info Dictionary")[
                                      'GridAgent_' + str((int(self.getStateValue("GridX")) - (i + 1)) % int(
                                          self.getStateValue("MaxGridX"))) + ',' + str(
                                          int(self.getStateValue("GridY")))].numAgent()+1))
            dir['up'] = max(up)
            dir['down'] = max(down)
            dir['right'] = max(right)
            dir['left'] = max(left)

            direction = max(dir.items(), key=operator.itemgetter(1))[0]

            if direction == 'up':
                self.setStateValue("NextGridID", self.strInitialGridID + str(int(self.getStateValue("GridX"))) + "," + str(
                    (int(self.getStateValue("GridY"))+1)%int(self.getStateValue("MaxGridY"))))
            elif direction == 'down':
                self.setStateValue("NextGridID", self.strInitialGridID + str(int(self.getStateValue("GridX"))) + "," + str(
                    (int(self.getStateValue("GridY"))-1)%int(self.getStateValue("MaxGridY"))))
            elif direction == 'right':
                self.setStateValue("NextGridID", self.strInitialGridID + str((int(self.getStateValue("GridX"))+1)%int(self.getStateValue("MaxGridX"))) + "," + str(
                    int(self.getStateValue("GridY"))))
            elif direction == 'left':
                self.setStateValue("NextGridID", self.strInitialGridID + str((int(self.getStateValue("GridX"))-1)%int(self.getStateValue("MaxGridX"))) + "," + str(
                    int(self.getStateValue("GridY"))))

    def funcTimeAdvance(self):
        if self.getStateValue("Arrived") == True:
            sys.exit()
            return sys.float_info.max
        else:
            if self.getStateValue("Initialized") == False:
                return 0
            else:
                if self.getStateValue("Request Grid Info") == False and self.getStateValue("Received Grid Info") == True:
                    return 0
                if self.getStateValue("Request Grid Info") == True and self.getStateValue("Received Grid Info") == False:
                    return sys.float_info.max
                else:
                    return self.getStateValue("NextGrid Travel Time")

    def funcSelect(self):
        pass