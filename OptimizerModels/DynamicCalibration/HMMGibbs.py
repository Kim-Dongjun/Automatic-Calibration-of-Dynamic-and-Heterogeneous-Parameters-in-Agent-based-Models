import random
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib import gridspec


class HMMGibbs:
    def plotPoints(self, data, affilitation, means, covs, affilitationProb, dir_, itr, l):
        plt.figure(1)
        gs = gridspec.GridSpec(3, 1)
        axarr0 = plt.subplot(gs[:2, :])
        # axarr0.set_facecolor('white')
        types = []
        for i in range(len(affilitation)):
            if affilitation[i] in types:
                pass
            else:
                types.append(affilitation[i])

        for i in range(len(data)):
            if i >= 1:
                axarr0.arrow(data[i - 1][0], data[i - 1][1], data[i][0] - data[i - 1][0], data[i][1] - data[i - 1][1],
                             head_width=0.1, head_length=0.15, fc='k', ec='k', length_includes_head=True, color='cyan')

        colors = ['r', 'g', 'b', 'y', 'k']
        totalX = []
        totalY = []
        for j in range(len(types)):
            x = []
            y = []
            for i in range(len(data)):
                if affilitation[i] == types[j]:
                    x.append(data[i][0])
                    y.append(data[i][1])
                    totalX.append(data[i][0])
                    totalY.append(data[i][1])
            axarr0.plot(x, y, colors[j % len(colors)] + 'o')

        gridX = np.arange(min(totalX) - 0.1 * (max(totalX) - min(totalX)),
                          max(totalX) + 0.1 * (max(totalX) - min(totalX)), (max(totalX) - min(totalX)) / 100)
        gridY = np.arange(min(totalY) - 0.1 * (max(totalY) - min(totalY)),
                          max(totalY) + 0.1 * (max(totalY) - min(totalY)), (max(totalY) - min(totalY)) / 100)
        meshX, meshY = np.meshgrid(gridX, gridY)

        axarr1 = plt.subplot(gs[2, :])

        affilitationProbTranspose = []
        for i in range(len(types)):
            temp = []
            for j in range(len(data)):
                temp.append(affilitationProb[j][i])
            affilitationProbTranspose.append(temp)

        temp = np.zeros(len(data))
        for i in range(len(types)):
            axarr1.bar(range(len(data)), affilitationProbTranspose[i], width=1.0, bottom=temp, color=colors[i],
                       edgecolor="none")
            for j in range(len(data)):
                temp[j] = temp[j] + affilitationProbTranspose[i][j]

        plt.tight_layout()
        plt.savefig(dir_ + "/hmm" + str(itr) + "-th_iteration_Candidate_" + str(l) + ".png")

    def most_common(self, lst):
        return max(set(lst), key=lst.count)

    def plotPoints_dj2(self, data, affilitation, means, covs, affilitationProb, dir_, l, first_dimension,
                       second_dimension, numCopy, itrCalibration, figType):
        plt.clf()
        plt.close()
        real_cluster = []
        for i in range(int(len(affilitation) / numCopy)):
            temp = affilitation[i * numCopy: (i + 1) * numCopy]
            real_cluster.append(self.most_common(temp))
        colors = ['r', 'g', 'b', 'y', 'k']
        for i in range(len(real_cluster)):
            if i == 0:
                pointShape = '^'
            else:
                pointShape = 'o'
            plt.plot(data[i * numCopy][first_dimension], data[i * numCopy][second_dimension],
                     colors[real_cluster[i]] + pointShape)
            if i == 0:
                plt.text(data[i * numCopy][first_dimension], data[i * numCopy][second_dimension], 'initial point',
                         fontsize=10)
            if i > 0:
                plt.arrow(data[(i - 1) * numCopy][first_dimension], data[(i - 1) * numCopy][second_dimension], \
                          data[i * numCopy][first_dimension] - data[(i - 1) * numCopy][first_dimension], \
                          data[i * numCopy][second_dimension] - data[(i - 1) * numCopy][second_dimension], \
                          head_width=0.01,
                          head_length=0.015)  # fc = 'k', ec = 'k', length_includes_head = True, color = 'y')
        if first_dimension == 0:
            plt.xlabel('Normalized Low Proportion Difference')
        elif first_dimension == 1:
            plt.xlabel('Normalized Middle Proportion Difference')
        else:
            plt.xlabel('Normalized Gini Index Difference')
        if second_dimension == 1:
            plt.ylabel('Normalized Middle Proportion Difference')
        else:
            plt.ylabel('Normalized Gini Index Difference')
        plt.title('Regime Detection Result of Single Hypothesis')
        if figType == 2:
            plt.savefig(dir_ + str(itrCalibration) + "-th_HMM_Candidate_" + str(l) + "_dimension_" + str(
                first_dimension) + "," + str(second_dimension) + ".png")
        elif figType == 3:
            plt.savefig(dir_ + str(itrCalibration) + "-th_HMM_Candidate_" + str(l) + "_dimension_" + str(
                first_dimension) + "," + str(second_dimension) + ".png", dpi=300)
        plt.close()

    def plotPoints_dj(self, data, affilitation, means, covs, affilitationProb, dir_, l, first_dimension,
                      second_dimension, numCopy, itrCalibration):
        plt.clf()
        plt.close()
        fig, axes = plt.subplots(2, 1, figsize=(20, 10))
        axarr0 = axes[0]
        types = [0, 1, 2]
        real_cluster = []
        for i in range(int(len(affilitation) / numCopy)):
            temp = affilitation[i * numCopy: (i + 1) * numCopy]
            real_cluster.append(self.most_common(temp))
        colors = ['r', 'g', 'b', 'y', 'k']
        totalX = []
        totalY = []
        for i in range(len(real_cluster)):
            if i == 0:
                pointShape = '^'
            else:
                pointShape = 'o'
            axarr0.plot(data[i * numCopy][first_dimension], data[i * numCopy][second_dimension],
                        colors[real_cluster[i]] + pointShape)
            if i == 0:
                axarr0.text(data[i * numCopy][first_dimension], data[i * numCopy][second_dimension], 'initial point',
                            fontsize=10)
            if i > 0:
                axarr0.arrow(data[(i - 1) * numCopy][first_dimension], data[(i - 1) * numCopy][second_dimension], \
                             data[i * numCopy][first_dimension] - data[(i - 1) * numCopy][first_dimension], \
                             data[i * numCopy][second_dimension] - data[(i - 1) * numCopy][second_dimension])

        axarr1 = axes[1]

        affilitationProbTranspose = []
        for i in range(len(types)):
            temp = []
            for j in range(len(data)):
                temp.append(affilitationProb[j][i])
            affilitationProbTranspose.append(temp)

        temp = np.zeros(len(data))
        for i in range(len(types)):
            axarr1.bar(range(len(data)), affilitationProbTranspose[i], width=1.0, bottom=temp, color=colors[i],
                       edgecolor="none")
            for j in range(len(data)):
                temp[j] = temp[j] + affilitationProbTranspose[i][j]

        fig.tight_layout()
        fig.savefig(dir_ + str(itrCalibration) + "-th_HMM_Candidate_" + str(l) + "_dimension_" + str(
            first_dimension) + "," + str(second_dimension) + ".png", dpi=300)
        plt.close()

    def initialize(self, data, k):
        transition = []
        initial = []
        for i in range(k):
            temp = []
            initial.append(1.0 / float(k))
            for j in range(k):
                temp.append(1.0 / float(k))
            transition.append(temp)

        dataCluster = []
        for j in range(k):
            dataCluster.append([])

        affilitationProb = []
        estimatedLabel = []
        for i in range(len(data)):
            temp = []
            for j in range(k):
                temp.append(0.0)
            affilitationProb.append(temp)

            idx = random.randrange(0, k)
            dataCluster[idx].append(data[i])
            affilitationProb[i][idx] = 1.0
            estimatedLabel.append(idx)

        means = []
        for j in range(k):
            means.append(np.mean(dataCluster[j], axis=0))

        covs = []
        for j in range(k):
            if len(dataCluster[j]) > 1:
                covs.append(np.cov(np.array(dataCluster[j]).T))
            else:
                covs.append([[1., 0.], [0., 1.]])
        return means, covs, transition, initial, affilitationProb, estimatedLabel

    def inferenceSampling(self, k, data, itr, l):
        means, covs, transition, initial, affilitationProb, estimatedLabel = self.initialize(data, k)

        for i in range(itr):
            for j in range(len(data)):
                # Expectation
                estimatedLabel[j], affilitationProb[j] = self.sampleLabel(k, data[j], means, covs, transition, initial,
                                                                          estimatedLabel, j, len(data))

                # Maximization
                means, covs, transition, initial = self.learningParameters(data, estimatedLabel, affilitationProb, k)
        return means, covs, transition, affilitationProb, estimatedLabel

    def learningParameters(self, data, estimatedLabel, affilitationProb, k):
        initial = []
        for i in range(k):
            initial.append(0.001)
        initial[int(estimatedLabel[0])] = 1.0
        normalize = 0.0
        for i in range(k):
            normalize = normalize + initial[i]
        for i in range(k):
            initial[i] = initial[i] / normalize

        transition = []
        for i in range(k):
            temp = []
            for j in range(k):
                temp.append(0.001)
            transition.append(temp)
        for i in range(len(data) - 1):
            transition[int(estimatedLabel[i])][int(estimatedLabel[i + 1])] = transition[int(estimatedLabel[i])][
                                                                                 int(estimatedLabel[i + 1])] + 1.0

        for i in range(k):
            normalize = 0.0
            for j in range(k):
                normalize = normalize + transition[i][j]
            for j in range(k):
                transition[i][j] = transition[i][j] / normalize

        means = []
        firstindex = 0
        for j in range(k):
            temp = data[firstindex] * affilitationProb[firstindex][j]
            # normalize = 0.0
            normalize = affilitationProb[firstindex][j]
            for i in range(1, len(data)):
                temp = temp + data[i] * affilitationProb[i][j]
                normalize = normalize + affilitationProb[i][j]
            temp = temp / normalize
            means.append(temp)

        covs = []
        for j in range(k):
            temp = np.outer((data[0] - means[j]), (data[0] - means[j])) * affilitationProb[0][j]
            normalize = affilitationProb[0][j]
            for i in range(1, len(data)):
                temp = temp + np.outer((data[i] - means[j]), (data[i] - means[j])) * affilitationProb[i][j]
                normalize = normalize + affilitationProb[i][j]
            temp = temp / normalize
            # if temp[0][0] == 0:
            #    temp = np.identity(4)
            covs.append(temp)

        return means, covs, transition, initial

    def sampleLabel(self, k, instance, means, covs, transition, initial, estimatedLabel, j, length):
        loglikelihood = []
        likelihood = []
        normalize = 0
        for i in range(k):
            if length == j + 1:
                logLikelihoodNextState = 0
            else:
                logLikelihoodNextState = np.log(transition[i][int(estimatedLabel[j + 1])])
            if j == 0:
                logLikelihoodPrevState = np.log(initial[i])
            else:
                logLikelihoodPrevState = np.log(transition[int(estimatedLabel[j - 1])][i])
            # covs[i] = covs[i] + 1.0 * np.array([[1.0, 0.0], [0.0, 1.0]])

            try:
                logLikelihoodObservation = np.log(stats.multivariate_normal.pdf(instance, mean=means[i],
                                                                                cov=covs[i] + 0.001 * np.identity(
                                                                                    len(means[i]))))
            except:
                print("Error!!!!")
                print("Instance : ", instance)
                print("mean : ", means[i])
                print("cov : ", covs[i])
                print("identity : ", np.identity(len(means[i])))
                print("Error : ", stats.multivariate_normal.pdf(instance, mean=means[i],
                                                                cov=covs[i] + 0.001 * np.identity(len(means[i]))))
            # logLikelihoodObservation = np.log(stats.multivariate_normal.pdf(instance, mean = means[i], cov = covs[i])+0.0001)
            loglikelihood.append(logLikelihoodNextState + logLikelihoodPrevState + logLikelihoodObservation)
            # likelihood.append(np.exp(loglikelihood[i]) + 0.001)
            likelihood.append(np.exp(loglikelihood[i]))
            normalize = normalize + likelihood[i]

        for i in range(k):
            likelihood[i] = likelihood[i] / normalize

        sample = np.random.multinomial(1, likelihood, size=1)
        ret = -1
        for i in range(k):
            if sample[0][i] > 0.5:
                ret = i
        return ret, likelihood


if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)

    trueChange = np.concatenate((np.zeros(20), np.ones(30), np.ones(40) * 2.0, np.zeros(10), np.ones(20)), axis=0)
    trueAffilitationProb = []
    for i in range(len(trueChange)):
        temp = []
        for j in range(3):
            if trueChange[i] == j:
                temp.append(1)
            else:
                temp.append(0)
        trueAffilitationProb.append(temp)

    trueMean = [[2, 4], [-1, 3], [0, 0]]
    # trueCov = [ [[0.9,0.5],[0.5,0.9]] , [[0.4,0.6],[0.5,0.9]], [[1.0,-0.5],[-0.5,1.0]] ]
    trueCov = [[[0.45, 0.25], [0.25, 0.45]], [[0.2, 0.3], [0.25, 0.45]], [[0.5, -0.25], [-0.25, 0.5]]]

    data = []
    for i in range(len(trueChange)):
        data.append(np.random.multivariate_normal(trueMean[int(trueChange[i])], trueCov[int(trueChange[i])], 1)[0])

    print("True Chage : ", trueChange)
    print("Data : ", data)

    hmm = HMMGibbs()
    hmm.plotPoints(data, trueChange, trueMean, trueCov, trueAffilitationProb)
    hmm.inferenceSampling(3, data, 10)