import numpy as np
import random
from hmmlearn import hmm
import OptimizerModels.DynamicCalibration.HMMGibbs as HMM
from scipy.optimize import fmin
from scipy.stats import beta
import sys

class CalibrationLearningModel:
    def useHMMVariant(self, numTimeStep, differences, trueResult, dir,l, itrCalibration, numberHMMClusters, numOutputDim):
        #normalized_differences = np.zeros((numOutputDim,))
        differences_np = []
        normalize = np.zeros(numTimeStep)
        trueResultNormalize = np.zeros(numTimeStep)
        for time in range(numTimeStep):
            normalize[time] = np.max(np.abs(differences[numTimeStep]))
            trueResultNormalize[time] = np.max(np.abs(trueResult[numTimeStep]))
        for time in range(numTimeStep):
            features = np.zeros((numOutputDim))
            trueResultFeature = []
            for summaryStatisticsDim in range(numOutputDim):
                features[summaryStatisticsDim] = differences[summaryStatisticsDim][time]
                trueResultFeature.append(trueResult[summaryStatisticsDim][time])
            for summaryStatisticsDim in range(numOutputDim):
                features[summaryStatisticsDim] = features[summaryStatisticsDim] / (trueResultNormalize[summaryStatisticsDim])
                trueResultFeature[summaryStatisticsDim] = trueResultFeature[summaryStatisticsDim] / trueResultNormalize[summaryStatisticsDim]
                differences_np.append(features)
        print(len(differences_np))
        print(len(differences_np[0]))
        print(len(differences_np[1]))
        sys.exit()
        hmm = HMM.HMMGibbs()
        means, covs, transition, affilitationProb, estimatedLabel_temp = hmm.inferenceSampling(numberHMMClusters, differences_np, 4, l)

        estimatedLabel = []
        for time in range(len(differences[0])):
            est_temp = [0]*3
            est_temp[estimatedLabel_temp[time]] += 1
            est_idx = np.argmax(est_temp)
            estimatedLabel.append(est_idx)
        return estimatedLabel

    def useHMM(self, numTimeStep, differences, trueResult, dir, l, itrCalibration, numberHMMClusters, numOutputDim):
        model = hmm.GaussianHMM(n_components=numberHMMClusters, covariance_type="full")
        #print(differences)
        model.fit(differences)
        predictedRegime = model.predict(differences)
        return predictedRegime

    def inferenceBetaDistributionParam(self, provedPoints, provedLikelihoods):

        sumLiklihood = 0.0
        for i in range(len(provedLikelihoods)):
            sumLiklihood = sumLiklihood + provedLikelihoods[i]

        data = []
        numSample = 1000
        for i in range(numSample):
            r = random.uniform(0.0,sumLiklihood)
            select = 0
            sum = 0.0
            for j in range(len(provedPoints)):
                if sum <= r and sum+provedLikelihoods[j] >= r:
                    select = j
                    break
                else:
                    sum = sum + provedLikelihoods[j]
            if provedPoints[select] == 0.0:
                data.append(provedPoints[select]+0.001)
            elif provedPoints[select] == 1.0:
                data.append(provedPoints[select] - 0.001)
            else:
                data.append(provedPoints[select])

        refinedData = []
        for itr in range(len(data)):
            data[itr] = data[itr] + np.random.normal(0.0,0.1,1)[0]
            if data[itr] < 0.0:
                pass
            elif data[itr] > 1.0:
                pass
            else:
                refinedData.append(data[itr])

        result = fmin(betaNLL, [1, 1], args=(data,), disp=0)
        alpha, beta = result
        return alpha,beta

def betaNLL(param,*args):
    """
    Negative log likelihood function for beta
    <param>: list for parameters to be fitted.
    <args>: 1-element array containing the sample data.

    Return <nll>: negative log-likelihood to be minimized.
    """

    a, b = param
    data = args[0]
    pdf = beta.pdf(data,a,b,loc=0,scale=1)
    lg = np.log(pdf)
    mask = np.isfinite(lg)
    nll = -lg[mask].sum()
    return nll