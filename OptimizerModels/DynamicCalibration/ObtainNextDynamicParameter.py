import SimulationModels.RealEstateMarketABM.postProcessSimulationResult as RealEstateMarketModelPost
import SimulationModels.WealthDistributionModel.postProcessSimulationResult as WealthDistributionModelPost
import OptimizerModels.DynamicCalibration.DynamicParameterDistributionLearning as LearningModels
from OptimizerModels.findOptimalParameter import findOptimalParameter
from plots.plots import plotsCalibrationFramework as plts

from scipy.stats import multivariate_normal
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

    def iterateCalibration2(self, itrCalibration, currentParameters, simResult, simResultCov):
        if itrCalibration % (self.hyperParameters.dynIters + self.hyperParameters.hetIters) < self.hyperParameters.dynIters:
            print("Updating dynamic parameters...")
            differences = self.post.getDifferences(simResult, self.trueResult)
            regimePerCandidate = self.obtainRegime(differences, itrCalibration)
            weights = np.zeros((self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))

            for candidate in range(self.hyperParameters.numCandidate):
                for time in range(self.hyperParameters.numTimeStep):
                    print("covariance : ", simResultCov[candidate][time])
                    weights[candidate][time] = multivariate_normal.pdf(self.trueResult[time], mean=simResult[candidate][time], cov=simResultCov[candidate][time])

    def iterateCalibration(self, itrCalibration, currentParameters, simResult, simResultCov):
        if itrCalibration % (self.hyperParameters.dynIters + self.hyperParameters.hetIters) < self.hyperParameters.dynIters:
            print("Updating dynamic parameters...")
            differences = self.post.getDifferences(simResult, self.trueResult)
            # RUN HMM VARIANT FOR REGIME DETECTION
            # REGIME IDENTIFICATION
            #regimePerCandidate = np.zeros((self.numCandidate, self.numTimeStep))
            regimePerCandidate = self.obtainRegime(differences, itrCalibration)
            logLikelihood = np.zeros((self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))
            likelihood = np.zeros((self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))
            simulationGoesWrong2 = np.zeros(self.hyperParameters.numTimeStep)
            print("regime transaction number : ", regimePerCandidate)

            for l in range(self.hyperParameters.numCandidate):
                #self.likelihood[l] = np.ones(self.numTimeStep)#[1.0] * self.numTimeStep
                for time in range(self.hyperParameters.numTimeStep):
                    for summaryStatisticsDim in range(self.hyperParameters.numOutputDim):
                        logLikelihood[l][time] = logLikelihood[l][time] + np.log(self.calculateNormalPDF(self.trueResult[summaryStatisticsDim][time], simResult[l][summaryStatisticsDim][time], simResultCov[l][summaryStatisticsDim][time]))

            for t in range(self.hyperParameters.numTimeStep):
                normalize = 0
                for l in range(self.hyperParameters.numCandidate):
                    likelihood[l][t] = np.exp(logLikelihood[l][t])
                    normalize = normalize + likelihood[l][t]
                for l in range(self.hyperParameters.numCandidate):
                    likelihood[l][t] = likelihood[l][t] / normalize
            likelihoodTranspose = np.transpose(likelihood)
            ## FIND THE CALIBRATION CANDIDATE POINTS (LINE 261)
            uniqueStateSignatures = []
            mergedRegime = []
            for t in range(self.hyperParameters.numTimeStep):
                flag = 0
                for j in range(len(uniqueStateSignatures)):
                    samecheck = 0
                    for k in range(len(uniqueStateSignatures[j])):
                        if uniqueStateSignatures[j][k] == regimePerCandidate[k][t]:
                            samecheck = samecheck + 1
                    if len(uniqueStateSignatures[j]) == samecheck:
                        flag = 1
                        mergedRegime[j].append(t)
                        break
                if flag == 0:
                    temp = []
                    for k in range(len(regimePerCandidate)):
                        temp.append(regimePerCandidate[k][t])
                    uniqueStateSignatures.append(temp)  # this is merged regime result. has shape [-1*numExps]
                    mergedRegime.append([t])  # this is merged regime.

            estNewParamLists = np.zeros((3, self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))
            for itrEstParams in self.hyperParameters.dynParamList:
                currentParameter = currentParameters[itrEstParams]
                estNextSimulationParamsAlphaBeta = [[0.0, 0.0]] * self.hyperParameters.numTimeStep
                print("merged regime transaction number : ", mergedRegime)
                for regime in range(len(mergedRegime)):
                    timeindexes = mergedRegime[regime]
                    bool = self.meaninglessLikelihoodCheck(likelihoodTranspose, timeindexes)
                    provedPoints = [0.0] * (self.hyperParameters.numCandidate * len(timeindexes))
                    provedLikelihoods = [0.0] * (self.hyperParameters.numCandidate * len(timeindexes))
                    for time in range(len(timeindexes)):
                        for candidate in range(self.hyperParameters.numCandidate):
                            provedPoints[time * self.hyperParameters.numCandidate + candidate] = currentParameter[candidate][
                                timeindexes[time]]
                            provedLikelihoods[time * self.hyperParameters.numCandidate + candidate] = likelihood[candidate][
                                timeindexes[time]]
                    alpha, beta = LearningModels.CalibrationLearningModel().inferenceBetaDistributionParam(provedPoints, provedLikelihoods)
                    for j in range(len(timeindexes)):
                        mean = alpha / (alpha + beta)
                        std = math.sqrt((alpha * beta) / (pow(alpha + beta, 2) * (alpha + beta + 1.)))
                    bool2 = self.meaninglessSimulationResultCheck(differences, timeindexes)
                    for cand in range(self.hyperParameters.numCandidate):
                        if self.hyperParameters.dynamicUpdate == 'samplingByTime':
                            for time in range(len(timeindexes)):
                                if bool or bool2:
                                    temp = np.random.uniform(0, 1, self.hyperParameters.numCandidate)
                                    simulationGoesWrong2[timeindexes[time]] = 1.0
                                    estNewParamLists[itrEstParams][cand][timeindexes[time]] = temp[cand]
                                else:
                                    estNewParamLists[itrEstParams][cand][timeindexes[time]] = np.random.beta(self.rateExperimentExploration * alpha, self.rateExperimentExploration * beta, 1)[0]
                        elif self.hyperParameters.dynamicUpdate == 'samplingByRegime':
                            tempo = np.random.beta(self.rateExperimentExploration * alpha, self.rateExperimentExploration * beta, 1)[0]
                            for time in range(len(timeindexes)):
                                if bool or bool2:
                                    temp = np.random.uniform(0, 1, self.hyperParameters.numCandidate)
                                    simulationGoesWrong2[timeindexes[time]] = 1.0
                                    estNewParamLists[itrEstParams][cand][timeindexes[time]] = temp[cand]
                                else:
                                    estNewParamLists[itrEstParams][cand][timeindexes[time]] = tempo
                        elif self.hyperParameters.dynamicUpdate == 'ModelSelection':
                            for time in range(len(timeindexes)):
                                temp = np.random.uniform(0, 1, self.hyperParameters.numCandidate)
                                if bool or bool2:
                                    simulationGoesWrong2[timeindexes[time]] = 1.0
                                    estNewParamLists[itrEstParams][cand][timeindexes[time]] = temp[cand]
                                else:
                                    estNewParamLists[itrEstParams][cand][timeindexes[time]] = mean + (
                                                cand - 1) * std
            for itrEstParams in range(len(currentParameters)):
                if itrEstParams not in self.hyperParameters.dynParamList:
                    for candidate in range(self.hyperParameters.numCandidate):
                        for time in range(self.hyperParameters.numTimeStep):
                            estNewParamLists[itrEstParams][candidate][time] = currentParameters[itrEstParams][candidate][time]
        else:
            print("Dynamic parameter fix!!!")
            #estNewParamLists = findOptimalParameter.findDynamicOptimalParameter()
            estNewParamLists = currentParameters

        self.plts.plotRegimeDetection(itrCalibration, regimePerCandidate, mergedRegime)

        return estNewParamLists

    def obtainRegime(self, differences, itrCalibration):
        regimePerCandidate = np.zeros((self.hyperParameters.numCandidate, self.hyperParameters.numTimeStep))
        for candidate in range(self.hyperParameters.numCandidate):
            #regimePerCandidate[candidate] = LearningModels.CalibrationLearningModel().useHMMVariant(self.hyperParameters.numTimeStep,
            #                                                                               differences[candidate], self.trueResult, self.hyperParameters.dir, candidate,
            #                                                                                itrCalibration, self.hyperParameters.HMMClusters, self.hyperParameters.numOutputDim)
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