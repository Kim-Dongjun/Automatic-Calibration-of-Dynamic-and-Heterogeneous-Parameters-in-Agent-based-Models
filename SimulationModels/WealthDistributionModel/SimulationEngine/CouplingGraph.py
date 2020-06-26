#-*- coding:utf-8 -*-

from SimulationModels.WealthDistributionModel.SimulationEngine.Utility.Logger import Logger
from SimulationModels.WealthDistributionModel.SimulationEngine.MRDEVS.MRDEVSAtomicModel import DEVSAtomicModel, MRDEVSAtomicModel

class CouplingGraph:

    def __init__(self,engine):
        self.engine = engine
        self.edges = []
        self.nodes = []
        self.adjacentNodes = {}
        self.nodesWithID = {}

    def addNode(self,node):
        if (str(node) in self.nodesWithID) == False:
            self.nodes.append(node)
            self.nodesWithID[str(node)] = node
            self.adjacentNodes[str(node)] = []

    def addEdge(self,edge):
        srcNode = edge.getSrcNode()
        tarNode = edge.getTarNode()
        self.addNode(srcNode)
        self.addNode(tarNode)
        self.edges.append(edge)
        self.adjacentNodes[str(srcNode)].append(str(tarNode))
        #print("!!! Adjacent !!!", self.adjacentNodes)

    def removeEdge(self,edge):
        srcNode = edge.getSrcNode()
        tarNode = edge.getTarNode()
        if str(tarNode) in self.adjacentNodes[str(srcNode)]:
            self.adjacentNodes[str(srcNode)].remove(str(tarNode))
        toRemove = -1
        for edge in self.edges:
            if edge.getSrcNode() == srcNode and edge.getTarNode() == tarNode:
                toRemove = edge
                break
        if toRemove != -1:
            self.edges.remove(toRemove)

    def getTerminalNodesInPath(self,srcNode,event):
        adjacentNodes = self.adjacentNodes[str(srcNode)]
        ret = []
        if len(adjacentNodes) == 0:
            return [srcNode]
        for nodeID in adjacentNodes:
            #print("3")
            if nodeID in self.nodesWithID:
                #print("3")
                node = self.nodesWithID[nodeID]
                if node.getDynamicDEVSCoupledModel() == True: # Adjacent Node 중에 Event의 Target Node가 어느 노드인지 체크!
                    #print("3")
                    node.getModel().funcStateTransition(node.getPort(),event.getMessage())
                ret = ret + self.getTerminalNodesInPath(node,event)
        return ret

    def broadcastEvent(self,event, currentTime):
        if event.getResolutionChange() == False:
            #self.printOut()
            srcModel = event.getSenderModel()
            srcPort = event.getSenderPort()
            #print("srcModel : ", srcModel.getModelID())
            #print("srcPort : ", srcPort)
            #for i in self.nodesWithID.keys():
            #    print("nodesWithID : ", i, self.nodesWithID[i])
            srcNode = self.nodesWithID[srcModel.getModelID()+"("+srcPort+")"]
            #print("a")
            tarNodes = self.getTerminalNodesInPath(srcNode,event)
            if srcNode in tarNodes:
                #print("srcNode Model's ID : ", srcNode.getModel().getModelID())
                tarNodes.remove(srcNode)
            self.engine.logger.log(Logger.MESSAGE, str(event.getMessage()) + "," + srcModel.getModelID() + "(" + srcPort + "), # Target Model : "+str(len(tarNodes)))
            for tarNode in tarNodes:
                tarModel = tarNode.getModel()
                #print("target Model's ID : ", tarModel.getModelID())
                self.engine.logger.log(Logger.MESSAGE,str(event.getMessage())+","+srcModel.getModelID()+"("+srcPort+")"+"-->"+tarModel.getModelID()+"("+tarNode.getPort()+")")
                if isinstance(tarModel,DEVSAtomicModel):
                    #print("event Message : ", event.getMessage())
                    # 원래 버전
                    # tarModel.funcExternalTransition(tarNode.getPort(),event.getMessage(), currentTime)
                    # 교수님께서 고치신 부분
                    tarModel.receiveExternalEvent(tarNode.getPort(),event.getMessage(),self.engine.getTime())
                    #print("     !!! 이벤트 발생 시 교수님께서 고친 부분은 다음과 같습니다.")
                    #print("     !!! 현재 보고 있는 child model : ", tarModel.getModelID())
                    #print("     !!! 현재 보고 있는 child model의 Time : ", tarModel.time)
                    #print("     !!! 현재 시뮬레이션 엔진의 currentTime : ", self.engine.getTime())
                    if tarModel.checkContinue() == False:
                        tarModel.execTimeAdvance()
                    if isinstance(tarModel,MRDEVSAtomicModel):
                        tarModel.funcResolutionTransition()

        if event.getResolutionChange() == True:
            currentModel = event.getSenderModel()
            parentModel = currentModel.getContainerModel()
            if parentModel == None:
                return
            oldState = parentModel.getResolutionState()
            if oldState == None:
                return
            oldStructure = parentModel.getResolutionStructureInfo(oldState)
            parentModel.funcResolutionTransition(event,oldStructure.getActivatedModels())
            if oldState != parentModel.getResolutionState():
                currentState = parentModel.getResolutionState()
                currentStructure = parentModel.getResolutionStructureInfo(currentState)
                parentModel.funcStateTranslation(currentState,oldStructure.getActivatedModels(),currentStructure.getActivatedModels())
                for models in currentStructure.getActivatedModels():
                    models.setActivate(True)

    def printOut(self):
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        self.engine.logger.log(Logger.STRUCTURE,"Coupling Nodes")
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        for node in self.nodes:
            self.engine.logger.log(Logger.STRUCTURE,node.getModelID()+"("+node.getPort()+")"+",DynamicCoupling : "+str(node.getDynamicDEVSCoupledModel()))
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        self.engine.logger.log(Logger.STRUCTURE,"Coupling Edges")
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        for edge in self.edges:
            output = edge.getSrcNode().getModelID()+"("+edge.getSrcNode().getPort()+")"
            output = output + "-->" + edge.getTarNode().getModelID() + "(" + edge.getTarNode().getPort() + ")"
            self.engine.logger.log(Logger.STRUCTURE,output)
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        self.engine.logger.log(Logger.STRUCTURE,"Coupling Adjacent Nodes")
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")
        for key in self.adjacentNodes:
            self.engine.logger.log(Logger.STRUCTURE,key + " : " +str(self.adjacentNodes[key]))
        self.engine.logger.log(Logger.STRUCTURE,"---------------------------------")

class CouplingEdge:

    def __init__(self,srcNode,tarNode):
        self.srcNode = srcNode
        self.tarNode = tarNode

    def getSrcNode(self):
        return self.srcNode

    def getTarNode(self):
        return self.tarNode

    def __str__(self):
        return str(self.srcNode)+"-->"+str(self.tarNode)

class CouplingNode:

    def __init__(self,model,modelID,port,blnDynamicDEVSCoupledModel=False,blnMRDEVSCoupledModel=False):
        self.modelID = modelID
        self.port = port
        self.model = model
        self.blnDynamicDEVSCoupledModel = blnDynamicDEVSCoupledModel
        self.blnMRDEVSCoupledModel = blnMRDEVSCoupledModel

    def equal(self,node):
        if self.modelID == node.modelID and self.port == node.port:
            return True
        return False

    def getPort(self):
        return self.port

    def getModelID(self):
        return self.modelID

    def getModel(self):
        return self.model

    def getMRDEVSCoupledModel(self):
        return self.blnMRDEVSCoupledModel

    def getDynamicDEVSCoupledModel(self):
        return self.blnDynamicDEVSCoupledModel

    def __str__(self):
        return self.modelID+"("+self.port+")"

if __name__ == "__main__":
    pass

