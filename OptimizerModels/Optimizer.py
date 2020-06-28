from OptimizerModels.DynamicCalibration.ObtainNextDynamicParameter import DynamicCalibration
from OptimizerModels.HeterogeneousCalibration.ObtainNextHeterogeneousParameter import HeterogeneousCalibration
from plots.plots import plotsCalibrationFramework as plts

class optimizer():
    def __init__(self, hyperParameters, trueObservation):
        self.hyperParameters = hyperParameters
        self.validationObservation = trueObservation
        self.dynCal = DynamicCalibration(self.hyperParameters, self.validationObservation)
        self.hetCal = HeterogeneousCalibration(self.hyperParameters, self.validationObservation)
        self.dic = {}
        self.plts = plts(self.hyperParameters)

    def getNewParams(self, dicParams, resultAverage, resultCov, itrCalibration):
        print("optimizing parameters...")
        self.plts.plotTrajectory(itrCalibration, resultAverage, resultCov, self.validationObservation)
        self.plts.plotDynamicParameters(itrCalibration, dicParams)
        dynParam = self.dynCal.iterateCalibration(itrCalibration, dicParams['dynamicParameter'], resultAverage, resultCov)
        hetParam = self.hetCal.iterateCalibration(itrCalibration, dicParams['heterogeneousParameter'], resultAverage)
        dicParams['dynamicParameter'] = dynParam
        dicParams['heterogeneousParameter'] = hetParam
        return dicParams