#-*- coding:utf-8 -*-

import random
import sys

from SimulationModels.WealthDistributionModel.SimulationEngine.ClassicDEVS.DEVSAtomicModel import DEVSAtomicModel
from SimulationModels.WealthDistributionModel.SimulationMessage import AgentMovement,GridInfo,DustPropagation
from SimulationModels.WealthDistributionModel.Message.HouseInfoMessage import HouseInfoMessage
import random

class GridAgent(DEVSAtomicModel):

    def __init__(self, strID,x,y,gridWealth):
        super().__init__(strID)
        #print("Model ID : ", self.getModelID())
        self.setStateValue("ID", strID)
        #self.setStateValue("lstGive",[])
        self.setStateValue("GridX", x)
        self.setStateValue("GridY", y)
        self.setStateValue("GridWealth", gridWealth)
        self.setStateValue("Sent Grid Info",False)
        self.setStateValue("Received Request Grid Info",False)
        self.setStateValue("Agent List", [])
        self.setStateValue("Wealth Level", None)
        self.setStateValue("Initialized", False)
        self.setStateValue("Wealth", None)


    def funcExternalTransition(self, strPort, objEvent, currentTime):
        #print("Ext:"+self.getModelID()+":"+strPort+":"+str(len(self.getStateValue("Agent List"))))
        #print(self.getModelID()+":"+str(self.getStateValue("Agent List")))

        if strPort == "leave_grid":
            if self.getModelID() == objEvent.strFromGridID:
                #print("!!! Agent Leave Grid")
                lstAgents = self.getStateValue("Agent List")
                strAgentID = objEvent.strMoveAgentID
                if strAgentID in lstAgents:
                    lstAgents.remove(strAgentID)
                    self.setStateValue("Agent List", lstAgents)
                self.setStateValue("Send Grid Info", False)
                self.setStateValue("Received Request Grid Info",True)
                #print("     그리드에 있던 에이전트가 이동한다고 이벤트가 왔습니다.")

        if strPort == "enter_grid":
            #print("To Grid : ", objEvent.strToGridID)
            if self.getModelID() == objEvent.strToGridID:
                #print("!!! Agent Enter Grid")
                lstAgents = self.getStateValue("Agent List")
                strAgentID = objEvent.strMoveAgentID
                if strAgentID not in lstAgents:
                    lstAgents.append(strAgentID)
                    self.setStateValue("Agent List",lstAgents)
                self.setStateValue("Send Grid Info",False)
                self.setStateValue("Received Request Grid Info", True)
                #print("     그리드에 새로운 에이전트가 편입한다고 이벤트가 왔습니다.")
                #print(self.getStateValue("Agent List"))

        lstAgents = self.getStateValue("Agent List")
        #dblDustLevel = self.getStateValue("Wealth Level")
        #self.setStateValue("Wealth Level",dblDustLevel)

    def funcOutput(self):
        if len(self.getStateValue("Agent List")) != 0:
            #print("Out:" + self.getModelID() + ":" + str(len(self.getStateValue("Agent List"))))
            pass
        if self.getStateValue("Received Request Grid Info") == True:
            #print("Out2:" + self.getModelID() + ":" + str(len(self.getStateValue("Agent List"))))
            self.setStateValue("Sent Grid Info", True)
            self.setStateValue("Received Request Grid Info", False)
            lstAgents = self.getStateValue("Agent List")
            for i in range(len(lstAgents)):
                #print("Out : " + self.getModelID() + ":" + lstAgents[i] + ", Pass Time : "+str(self.getStateValue("Traffic Pass Time")))
                objGridInfo = GridInfo(self.getModelID(), \
                                       self.getStateValue("GridX"), \
                                       self.getStateValue("GridY"), \
                                       self.getStateValue("GridWealth"), \
                                       len(lstAgents), \
                                       None)
                self.addOutputEvent("send_grid_info_"+lstAgents[i], objGridInfo)
                #print("     그리드 정보를 넘겨주는 이벤트를 송출합니다.")

    def funcInternalTransition(self):
        #print("Int:"+self.getModelID())
        self.setStateValue("Received Request Grid Info",False)
        if self.getStateValue("Initialized") == False:
            lstAgents = self.getStateValue("Agent List")
            #dblWealthLevel = self.getStateValue("Wealth Level")
            self.setStateValue("Initialized", True)


    def funcTimeAdvance(self):
        #print("!!! TA : "+self.getStateValue("ID"))

        if  self.getStateValue("Initialized") == False:
            #print("Grid Time : Initialized")
            #print("!!! TA 1")
            return 0
        elif self.getStateValue("Received Request Grid Info") == True:
            #print("Grid Time : Received Request Grid Info True")
            #print("!!! TA 2")
            return 0
        elif self.getStateValue("Received Request Grid Info") == False:
            #print("Grid Time : Received Request Grid Info False")
            return sys.float_info.max
        elif self.getStateValue("Sent Grid Info") == True:
            #print("Grid Time : Sent Grid Info True")
            return sys.float_info.max

    def funcSelect(self):
        pass

    def __str__(self):
        return "I am Grid Agent!"