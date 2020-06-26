from SimulationModels.RealEstateMarketABM.SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from SimulationModels.RealEstateMarketABM.Operator import Operator
from SimulationModels.RealEstateMarketABM.RealEstateMarket import HousingMarket



class HousingMarketModel(DEVSCoupledModel):
    def __init__(self, objConfiguration):
        super().__init__("HousingMarketModel")

        self.objHousingMarket = HousingMarket(objConfiguration)
        self.addModel(self.objHousingMarket)  # Simulation Engine registered

        self.objOperator = Operator(objConfiguration, self.objHousingMarket.lstHouseholdAgent, self.objHousingMarket.lstHouse)
        self.addModel(self.objOperator)  # Simulation Engine registered

        self.addInternalCoupling(self.objOperator, "startList", self.objHousingMarket, "startList")
        self.addInternalCoupling(self.objOperator, "startBuy", self.objHousingMarket, "startBuy")
        self.addInternalCoupling(self.objOperator, "startUpdate", self.objHousingMarket, "startUpdate")
        self.addInternalCoupling(self.objHousingMarket, "endList", self.objOperator, "endList")
        self.addInternalCoupling(self.objHousingMarket, "endBuy", self.objOperator, "endBuy")
        self.addInternalCoupling(self.objHousingMarket, "endUpdate", self.objOperator, "endUpdate")