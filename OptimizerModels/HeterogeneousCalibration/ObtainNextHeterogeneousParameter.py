import OptimizerModels.HeterogeneousCalibration.fitnessCalculator as fitnessCalculator


import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from sklearn.gaussian_process.kernels import Matern, DotProduct
from sklearn.gaussian_process import GaussianProcessRegressor
import sys

class HeterogeneousCalibration():

    def __init__(self, hyperParameters, validationObservation):
        self.hyperParameters = hyperParameters
        self.trueResult = validationObservation
        self.heterogeneousParameters = []
        self.heterogeneousFitnesses = []
        self.dataAcquisitionFunction = []

    def iterateCalibration(self, itrCalibration, heterogeneousParameter, resultAverage):
        if itrCalibration % (self.hyperParameters.dynIters + self.hyperParameters.hetIters) >= self.hyperParameters.dynIters:
            print("Updating Heterogeneous Parameters...")
            fitness = np.array(fitnessCalculator.fitnessCalculator(resultAverage, self.trueResult)).reshape(-1)
            hetParam = []
            for idx in self.hyperParameters.hetParamList:
                hetParam.append(heterogeneousParameter[idx])
            hetParam = np.array(hetParam).reshape(-1)
            self.heterogeneousParameters.append(hetParam)
            self.heterogeneousFitnesses.append(fitness)
            kernel1 = Matern(nu=0.5)
            kernel2 = DotProduct()
            kernel = kernel1 + kernel2
            gp = GaussianProcessRegressor(kernel=kernel, alpha=0.001, n_restarts_optimizer=10)
            gp.fit(self.heterogeneousParameters, self.heterogeneousFitnesses)
            if itrCalibration < self.hyperParameters.randomIterations:
                nextHeterogeneousParameter = np.random.random(len(self.heterogeneousParameters[0])).tolist()
            elif itrCalibration >= self.hyperParameters.randomIterations:
                rand = np.random.random()
                if rand < self.hyperParameters.fullExplorationRatio:
                    #print("predictive variance")
                    nextHeterogeneousParameter = self.propose_location(self.predictive_variance, self.heterogeneousParameters,
                                                                     self.heterogeneousFitnesses, gp,
                                                                     np.array([[0.0, 1.0]] * len(self.heterogeneousParameters[0])), 100)
                if rand >= self.hyperParameters.fullExplorationRatio and rand < self.hyperParameters.fullExplorationRatio + self.hyperParameters.fullExploitationRatio:
                    #print("predictive mean")
                    nextHeterogeneousParameter = self.propose_location(self.predictive_mean, self.heterogeneousParameters,
                                                                     self.heterogeneousFitnesses, gp,
                                                                     np.array([[0.0, 1.0]] * len(self.heterogeneousParameters[0])), 100)
                if rand >= self.hyperParameters.fullExplorationRatio + self.hyperParameters.fullExploitationRatio and \
                        (rand < self.hyperParameters.fullExplorationRatio + self.hyperParameters.fullExploitationRatio + self.hyperParameters.randomRatio):
                    #print("random")
                    nextHeterogeneousParameter = np.random.random(len(self.heterogeneousParameters[0])).tolist()
                if rand >= self.hyperParameters.fullExplorationRatio + self.hyperParameters.fullExploitationRatio + self.hyperParameters.randomRatio:
                    #print("weighted expected improvement")
                    nextHeterogeneousParameter = self.propose_location(self.expected_improvement, self.heterogeneousParameters, self.heterogeneousFitnesses, gp,
                                            np.array([[0.0, 1.0]]*len(self.heterogeneousParameters[0])), 100)

            heterogeneousParameter = np.array(nextHeterogeneousParameter).reshape(len(self.hyperParameters.hetParamList),-1)

        else:
            print("Heterogeneous parameter fix!!!")
        return heterogeneousParameter

    def propose_location(self, acquisition, X_sample, Y_sample, gp, bounds, n_restarts):
        ''' Proposes the next sampling point by optimizing the acquisition function.
        Args: acquisition: Acquisition function. X_sample: Sample locations (n x d).
        Y_sample: Sample values (n x 1).
        gpr: A GaussianProcessRegressor fitted to samples.
        Returns: Location of the acquisition function maximum. '''

        dim = len(X_sample[0])
        min_val = 1
        min_x = None

        def min_obj(X):
            # Minimization objective is the negative acquisition function
            return -acquisition(X.reshape(-1, dim), X_sample, Y_sample, gp)

        # Find the best optimum by starting from n_restart different random points.
        for x0 in np.random.uniform(bounds[:, 0], bounds[:, 1], size=(n_restarts, dim)):
            res = minimize(min_obj, x0=x0, bounds=bounds, method='L-BFGS-B')
            if res.fun < min_val:
                min_val = res.fun[0]
                min_x = res.x
        self.dataAcquisitionFunction.append('EI')

        return min_x

    def expected_improvement(self, X, X_sample, Y_sample, gp, xi=0.01):
        ''' Computes the EI at points X based on existing samples X_sample and Y_sample using a Gaussian process surrogate model. Args: X: Points at which EI shall be computed (m x d). X_sample: Sample locations (n x d). Y_sample: Sample values (n x 1). gpr: A GaussianProcessRegressor fitted to samples. xi: Exploitation-exploration trade-off parameter. Returns: Expected improvements at points X. '''
        #print("X가 문제 : ", X)
        mu, sigma = gp.predict(X, return_std=True)
        mu_sample = gp.predict(X_sample)
        w = 0.5 * pow(0.99, len(Y_sample))
        #sigma = sigma.reshape(-1, len(X_sample[0]))
        sigma = sigma.reshape(-1)

        # Needed for noise-based model,
        # otherwise use np.max(Y_sample).
        # See also section 2.4 in [...]
        mu_sample_opt = np.max(mu_sample)

        with np.errstate(divide='warn'):
            imp = mu - mu_sample_opt - xi
            Z = imp / sigma
            ei = (1-w) * imp * norm.cdf(Z) + w * sigma * norm.pdf(Z)
            ei[sigma == 0.0] = 0.0
        return ei

    def predictive_variance(self, X, X_sample, Y_sample, gp, xi=0.01):
        mu, sigma = gp.predict(X, return_std=True)
        sigma = sigma.reshape(-1)
        return sigma

    def predictive_mean(self, X, X_sample, Y_sample, gp, xi=0.01):
        mu, sigma = gp.predict(X, return_std=True)
        return -mu