from SimulationModels.WealthDistributionModel.SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from SimulationModels.WealthDistributionModel.HouseHoldAgent import HouseHoldAgent
from SimulationModels.WealthDistributionModel.GridAgent import GridAgent
from SimulationModels.WealthDistributionModel.SimulationMessage import AgentMovement,GridInfo,DustPropagation
import os
import sys
import random
import csv
import numpy as np

class WealthDistribution(DEVSCoupledModel):

    def __init__(self,objConfiguration, dynamicParameter, heterogeneousParameter, directory=''):
        super().__init__("WealthDistribution")

        intNumAgentHouseHold = objConfiguration.getConfiguration("numAgentHouseHold")
        intNumGridX = objConfiguration.getConfiguration("numGridX")
        intNumGridY = objConfiguration.getConfiguration("numGridY")
        candidate = objConfiguration.getConfiguration("candidate")

        self.dir = directory
        self.lstGridID = []

        # Create Grid Agent
        self.lstGridAgent = []
        for i in range(intNumGridX):
            self.lstGridAgent.append([])
            self.lstGridID.append([])
            for j in range(intNumGridY):
                strGridID = "GridAgent_" + str(i) + "," + str(j)
                self.lstGridID[i].append(strGridID)
                objGrid = GridAgent('GridAgent_' + str(i) + ',' + str(j),i,j,random.randint(2,15))
                self.addModel(objGrid)  # Simulation Engine registered
                self.lstGridAgent[i].append(objGrid)

        # Create Household Agent
        self.lstHouseHoldAgent = []
        for i in range(intNumAgentHouseHold):
            dicGridInfo = {}
            for j in range(intNumGridX):
                for k in range(intNumGridY):
                    #print("-----------------------------------")
                    #print(self.lstGridID[j][k])
                    dicGridInfo[self.lstGridID[j][k]] = GridInfo(self.lstGridID[j][k], j, k, self.lstGridAgent[j][k].getStateValue("GridWealth"), len(self.lstGridAgent[j][k].getStateValue("Agent List")), 0)
                    #dicGridInfo[self.lstGridID[j][k]] = self.lstGridAgent[j][k]
            objAgent = HouseHoldAgent(objConfiguration, 'HouseHoldAgent_'+str(i),'GridAgent_',random.randint(0,intNumGridX-1),
                                      random.randint(0,intNumGridY-1),intNumGridX,intNumGridY,1,random.randint(10,20),
                                      1,1,1,100, 0, 0, dicGridInfo, candidate, dynamicParameter, heterogeneousParameter)
            self.addModel(objAgent) # Simulation Engine registered
            self.lstHouseHoldAgent.append(objAgent)

        #for i in range(intNumAgentHouseHold):
        #    print(self.lstHouseHoldAgent[i].getStateValue("ID"),self.lstHouseHoldAgent[i].getStateValue("GridX"),self.lstHouseHoldAgent[i].getStateValue("GridY"))

        for i in range(intNumAgentHouseHold):
            for j in range(intNumGridX):
                for k in range(intNumGridY):
                    # addCoupling은 initial node -> target node로 coupling 관계를 정의
                    # Define Node(Grid) that agent is currently in
                    self.addInternalCoupling(self.lstHouseHoldAgent[i], "leave_grid_GridAgent_"+str(j)+','+str(k), \
                                             self.lstGridAgent[j][k], "leave_grid")
                    self.addInternalCoupling(self.lstHouseHoldAgent[i], "enter_grid_GridAgent_" + str(j) + ',' + str(k), \
                                             self.lstGridAgent[j][k], "enter_grid")
                    self.addInternalCoupling(self.lstGridAgent[j][k], "send_grid_info_"+self.lstHouseHoldAgent[i].getStateValue("ID"), \
                                             self.lstHouseHoldAgent[i], "send_grid_info_"+self.lstHouseHoldAgent[i].getStateValue("ID"))

