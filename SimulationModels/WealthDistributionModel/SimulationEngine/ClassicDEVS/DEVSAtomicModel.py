#-*- coding:utf-8 -*-

from SimulationModels.WealthDistributionModel.SimulationEngine.ClassicDEVS.DEVSModel import DEVSModel
from SimulationModels.WealthDistributionModel.SimulationEngine.Utility.Event import Event
from SimulationModels.WealthDistributionModel.SimulationEngine.Utility.Logger import Logger

class DEVSAtomicModel(DEVSModel):

    def __init__(self,ID):
        super().__init__()
        self.blnContinue = False
        self.setModelID(ID)
        # Atomic Model에서 nextTime은 self.time + nextTimeAdvance로 계산되며, nextTime은 model의 queryTime의 output이다.
        self.time = 0

    def receiveExternalEvent(self,port,event,currentTime):
        self.blnContinue = False
        self.funcExternalTransition(port,event,currentTime)
        # 교수님 고친 부분 here
        #self.funcExternalTransition(event)
        if self.blnContinue == False:
            self.time = currentTime
            self.execTimeAdvance()
            #self.performTimeAdvance()

    def getCurrentTime(self):
        return self.time

    def setCurrentTime(self,currentTime):
        #print("!!! ENGINE : setCurrentTime : "+str(self.getModelID())+": Current Time : "+str(currentTime) ) #+" : Time : "+str(self.getTime()))
        self.time = currentTime

    def addOutputEvent(self,varOutput,varMessage):
        self.engine.addEvent(Event(self,varOutput,varMessage))
        #print("!!! Event Add : ", Event(self,varOutput,varMessage))

    def performTimeAdvance(self,currentTime,maxwealth, minwealth):
        #print("1")
        self.time = currentTime
        #print("    ", self.getModelID()," 모델 Output Function 구동중입니다..")
        self.funcOutput()
        try:
            self.funcInternalTransition(maxwealth, minwealth)
            #print("    ", self.getModelID(), " 모델 Internal Transition Function 구동중입니다..")
        except:
            self.funcInternalTransition()
            #print("    ", self.getModelID(), " 모델 Internal Transition Function 구동중입니다..")
        self.execTimeAdvance()

    def queryTimeAdvance(self):
        self.logger.log(Logger.TA,"Query MIN TA ("+self.getModelID()+") : " + str(self.nextTimeAdvance))
        #print("Query MIN TA Atomic (" + self.getModelID() + ") : " + str(self.nextTimeAdvance))
        return self.nextTimeAdvance

    def queryTime(self):
        self.logger.log(Logger.TA,"Query Time ("+self.getModelID()+") : " + str(self.nextTime))
        #print("     Query Time ("+self.getModelID()+") : "+str(self.nextTime))
        return self.nextTime

    def continueTimeAdvance(self):
        self.blnContinue = True

    def execTimeAdvance(self):
        #print("    ", self.getModelID(), " 모델 Time Advance Function 구동중입니다..")
        self.nextTimeAdvance = self.funcTimeAdvance()
        #print("     Next Time을 current Time에 nextTimeAdvance를 더하여 업데이트하는 중입니다..")
        #print("     현재 집중하고 있는 child Model Time : ", self.time)
        #print("     nextTimeAdvance : ", self.nextTimeAdvance)
        self.nextTime = self.time + self.nextTimeAdvance
        #print("     현재 모델의 nextTime은 다음과 같습니다 : ", self.nextTime)

    def checkContinue(self):
        value = self.blnContinue
        self.blnContinue = False
        return value

    def funcOutput(self):
        pass

    def funcExternalTransition(self, strPort, event):
        pass

    def funcInternalTransition(self):
        pass

    def funcTimeAdvance(self):
        pass

    def funcSelect(self):
        pass

if __name__ == "__main__":
    pass