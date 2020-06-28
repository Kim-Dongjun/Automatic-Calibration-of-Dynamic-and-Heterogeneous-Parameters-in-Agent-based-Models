import SimulationModels.RealEstateMarketABM.postProcessSimulationResult as RealEstateMarketModelPost
import SimulationModels.WealthDistributionModel.postProcessSimulationResult as WealthDistributionModelPost
import OptimizerModels.DynamicCalibration.DynamicParameterDistributionLearning as LearningModels
from OptimizerModels.findOptimalParameter import findOptimalParameter
from plots.plots import plotsCalibrationFramework as plts

from scipy.stats import multivariate_normal
from scipy.stats import norm
from scipy.stats import beta
from scipy.optimize import fmin
import numpy as np
import math
import sys

class DynamicCalibration():

    def __init__(self, hyperParameters, validationObservation):
        self.hyperParameters = hyperParameters
        self.trueResult = validationObservation
        self.numCopy = 5
        self.rateExperimentExploration = 1
        if self.hyperParameters.modelName == 'RealEstateMarketABM':
            self.post = RealEstateMarketModelPost.postProcess(hyperParameters)
        elif self.hyperParameters.modelName == 'WealthDistributionABM':
            self.post = WealthDistributionModelPost.postProcess(hyperParameters)
        self.plts = plts(self.hyperParameters)

    def iterateCalibration(self, itrCalibration, currentParameters, simResult, simResultCov):
        if itrCalibration % (self.hyperParameters.dynIters + self.hyperParameters.hetIters) < self.hyperParameters.dynIters:
            print("Updating dynamic parameters...")
            differences = self.post.getDifferences(simResult, self.trueResult)
            regimePerCandidate = self.obtainRegime(differences, itrCalibration)
            mergedRegime, numMergedRegimes, mergedRegimesSet = self.mergingRegime(regimePerCandidate)

            weights = np.zeros((self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))
            for candidate in range(self.hyperParameters.numCandidate):
                for time in range(self.hyperParameters.numTimeStep):
                    for ss in range(len(self.trueResult[time])):
                        if simResult[candidate][time][ss] == 0.:
                            weights[candidate][time] += np.log(
                                norm.pdf(self.trueResult[time][ss], simResult[candidate][time][ss],
                                         simResultCov[candidate][time][ss][ss] + 0.01))
                            #print("weights 1 : ", candidate, time, ss, self.trueResult[time][ss], simResult[candidate][time][ss], np.log(
                            #    norm.pdf(self.trueResult[time][ss], simResult[candidate][time][ss],
                            #             simResultCov[candidate][time][ss][ss] + 0.01)))
                        else:
                            weights[candidate][time] += np.log(norm.pdf(self.trueResult[time][ss], simResult[candidate][time][ss], simResultCov[candidate][time][ss][ss] + 0.01 * simResult[candidate][time][ss]))
                            #print("weights 2 : ", candidate, time, ss, self.trueResult[time][ss], simResult[candidate][time][ss], np.log(norm.pdf(self.trueResult[time][ss], simResult[candidate][time][ss], simResultCov[candidate][time][ss][ss] + 0.01 * simResult[candidate][time][ss])))
            for m in range(numMergedRegimes):
                for l in range(currentParameters.shape[0]):
                    alpha_, beta_ = self.mleBeta(currentParameters, weights, mergedRegimesSet, m, l)
                    currentParameters = self.generateNextDynamicParameter(alpha_, beta_, currentParameters,
                                                                       mergedRegimesSet, m, l)
            return currentParameters
        else:
            return currentParameters

    def generateNextDynamicParameter(self, alpha_, beta_, currentParameters, mergedRegimesSet, m, l):
        if self.hyperParameters.dynamicUpdate == 'samplingByTime':
            samples = beta.rvs(alpha_, beta_, size=self.hyperParameters.numCandidate * len(mergedRegimesSet[m])).tolist()
        elif self.hyperParameters.dynamicUpdate == 'samplingByRegime':
            samples = beta.rvs(alpha_, beta_, size=self.hyperParameters.numCandidate).tolist()
        elif self.hyperParameters.dynamicUpdate == 'ModeSelection':
            samples = []
            mean = (alpha_ + beta_) / alpha_
            std = np.sqrt((alpha_ * beta_) / (pow(alpha_ + beta_,2) * (alpha_ + beta_ + 1.)))
            for candidate in range(self.hyperParameters.numCandidate):
                samples.append(mean + (candidate - (self.hyperParameters.numCandidate - 1.)/2.) * std)
        for candidate in range(self.hyperParameters.numCandidate):
            if self.hyperParameters.dynamicUpdate == 'samplingByTime':
                for time in mergedRegimesSet[m]:
                    rand = np.random.choice(len(samples))
                    currentParameters[l][candidate][time] = samples[rand]
                    del samples[rand]
            else:
                rand = np.random.choice(len(samples))
                for time in mergedRegimesSet[m]:
                    currentParameters[l][candidate][time] = samples[rand]
                del samples[rand]
        return currentParameters

    def mleBeta(self, currentParameters, weights, mergedRegimesSet, m, l):
        parameters = []
        weights_ = []
        for time in mergedRegimesSet[m]:
            for candidate in range(self.hyperParameters.numCandidate):
                parameters.append(currentParameters[l][candidate][time])
                weights_.append(weights[candidate][time])
        numSamples = 100
        samples = []
        weights_ = weights_ / np.sum(weights_)
        if not np.isnan(np.sum(weights_)):
            for n in range(numSamples):
                choice = np.random.choice(parameters, 1, p=weights_)
                samples.append(choice[0]+0.01*(np.random.random()-0.5))
            samples = np.clip(samples, 0.001, 0.999)
            #alpha_, beta_, mean, std = beta.fit(samples)
            result = fmin(self.betaNLL, [1, 1], args=(samples,), disp=False)
            alpha_, beta_ = result
            return alpha_, beta_
        else:
            return 1, 1

    def betaNLL(self, param, *args):
        '''Negative log likelihood function for beta
        <param>: list for parameters to be fitted.
        <args>: 1-element array containing the sample data.

        Return <nll>: negative log-likelihood to be minimized.
        '''

        a, b = param
        data = args[0]
        pdf = beta.pdf(data, a, b, loc=0, scale=1)
        lg = np.log(pdf)
        # -----Replace -inf with 0s------
        lg = np.where(lg == -np.inf, 0, lg)
        nll = -1 * np.sum(lg)
        return nll

    def mergingRegime(self, regimePerCandidate):
        mergedRegime = np.zeros(self.hyperParameters.numTimeStep)
        regimePerCandidate_tp = np.transpose(regimePerCandidate)
        regimesType = {}
        for time in range(self.hyperParameters.numTimeStep):
            if str(regimePerCandidate_tp[time]) in regimesType.keys():
                regimesType[str(regimePerCandidate_tp[time])].append(time)
            else:
                regimesType[str(regimePerCandidate_tp[time])] = [time]
        typeIndicator = {}
        typeNumber = 0
        for type in regimesType.keys():
            typeIndicator[type] = typeNumber
            typeNumber += 1
        mergedRegimesSet = {}
        for type in regimesType.keys():
            mergedRegimesSet[typeIndicator[type]] = regimesType[type]
        for key in regimesType.keys():
            for time in regimesType[key]:
                mergedRegime[time] = typeIndicator[key]
        return mergedRegime, typeNumber, mergedRegimesSet

    def obtainRegime(self, differences, itrCalibration):
        regimePerCandidate = np.zeros((self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))
        for candidate in range(self.hyperParameters.numCandidate):
            regimePerCandidate[candidate] = LearningModels.CalibrationLearningModel().useHMM(self.hyperParameters.numTimeStep,
                                                                                           self.normalize(differences[candidate]), self.trueResult, self.hyperParameters.dir, candidate,
                                                                                            itrCalibration, self.hyperParameters.HMMClusters, self.hyperParameters.numOutputDim)
        return regimePerCandidate

    def normalize(self, vector):
        return vector / np.sum(vector,0)

    def calculateNormalPDF(self, X, mean, std):
        if std == 0.:
            return 1.
        std = 10. * std
        ret = 1.0 / math.sqrt(2 * math.pi * std * std + sys.float_info.epsilon)
        ret = ret * math.exp(-(X - mean) * (X - mean) / (2 * std * std + sys.float_info.epsilon))
        return ret

    def meaninglessLikelihoodCheck(self, likelihoodTranspose, timeindexes):
        number = 0
        for time in range(len(timeindexes)):
            #print("Check "+str(timeindexes[time]))
            if self.sameCheck(likelihoodTranspose[timeindexes[time]]) or math.isnan(likelihoodTranspose[timeindexes[time]][0]) \
                    or math.isnan(likelihoodTranspose[timeindexes[time]][1]) or math.isnan(likelihoodTranspose[timeindexes[time]][2]):
                #print("Time : "+str(timeindexes[time])+" Same !!!!")
                number += 1
        if number > len(timeindexes) / 2.:
            return True
        else:
            return False

    def sameCheck(self, list):
        for i in range(len(list)):
            for j in range(i):
                if abs(list[i]-list[j]) > 0.01:
                    return False
        return True

    def meaninglessSimulationResultCheck(self, differences, timeindexes):
        number = 0
        for cand in range(self.hyperParameters.numCandidate):
            count = 0
            for time in range(len(timeindexes)):
                temp = 0
                for j in range(self.hyperParameters.numOutputDim):
                    if self.resultCheck(differences, timeindexes[time], cand, j):
                        temp += 1
                if temp > self.hyperParameters.numOutputDim / 2.:
                    count += 1
            if count > len(timeindexes) / 2.:
                number += 1
        if number == self.hyperParameters.numCandidate:
            return True
        else:
            return False

    def resultCheck(self, differences, time, cand, j):
        # Shape(self.simResult) = numCandidate * 4 * numTimeStep # Shape(self.trueResult) = 4 * numTimeStep
        if abs(self.trueResult[j][time] - differences[cand][j][time]) / max(self.trueResult[j][time], differences[cand][j][time]) > 0.5:
            return True
        else:
            return False