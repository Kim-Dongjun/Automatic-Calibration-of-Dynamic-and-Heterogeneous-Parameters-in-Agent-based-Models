class AgentMovement:
    def __init__(self,strFromGridID,strToGridID,strMoveAgentID):
        self.strMessage = "Move,"+str(strFromGridID)+","+str(strToGridID)+","+str(strMoveAgentID)
        self.strFromGridID = strFromGridID
        self.strToGridID = strToGridID
        self.strMoveAgentID = strMoveAgentID
    def __str__(self):
        return self.strMessage

class GridInfo:
    def __init__(self,strGridID,dblLon,dblLat,dblGridWealth,intHoldingAgent, strTargetAgentID):
        self.strMessage = "GridInfo," + str(strGridID) + "," + str(dblLon) + "," + \
                          str(dblLat) + "," + str(dblGridWealth) + "," + str(intHoldingAgent) + "," + str(strTargetAgentID)
        self.strGridID = strGridID
        self.strRequestAgentID = strTargetAgentID
        self.dblLon = dblLon
        self.dblLat = dblLat
        self.dblGridWealth = dblGridWealth
        self.intHoldingAgent = intHoldingAgent

    def __str__(self):
        return self.strMessage

    def gridWealth(self):
        return self.dblGridWealth

    def numAgent(self):
        return self.intHoldingAgent

class DustPropagation:
    def __init__(self,dblDust):
        self.strMessage = "DustPropagation,"+str(dblDust)
        self.dblDust = dblDust
    def __str__(self):
        return self.strMessage
