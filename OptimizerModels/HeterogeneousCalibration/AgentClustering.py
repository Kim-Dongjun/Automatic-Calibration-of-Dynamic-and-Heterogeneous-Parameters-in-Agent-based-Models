from SimulationModels.simulator import simulation
import OptimizerModels.HeterogeneousCalibration.VariationalAutoencoder as VariationalAutoEncoder
import OptimizerModels.HeterogeneousCalibration.PostProcessAgentLevelData as PostProcessAgentLevelData

import numpy as np
import copy
from sklearn.neighbors import NearestNeighbors
from sklearn import mixture
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn import cluster
from sklearn import manifold
from collections import Counter

class agentCluster():
    def __init__(self, dicParams, hyperParameters):
        self.hyperParameters = hyperParameters
        # Run simulation to acquire agent-level state variables for agent clustering
        self.agentClusters = []
        self.simulator = simulation(self.hyperParameters, self.agentClusters)
        #print("dicParams : ", dicParams)
        #sys.exit()
        if self.hyperParameters.modelName == 'RealEstateMarketABM' and (self.hyperParameters.experiment == 'heterogeneous' or self.hyperParameters.experiment == 'framework'):
            self.simulator.runParallelSimulation(-1, dicParams)
            # Post-process the agent-level state variable to make it an appropriate form for latent representation learning
            self.normalizedSimMicroResult = PostProcessAgentLevelData.readMicroResult(hyperParameters)

    def agentClustering(self, clusteringAlgorithm, numberOfClusters):
        if self.hyperParameters.modelName == 'RealEstateMarketABM' and (self.hyperParameters.experiment == 'heterogeneous' or self.hyperParameters.experiment == 'framework'):
            print("Clustering Process Begins")
            # Variational AotoEncoder
            print("Learning Representation by Variational Autoencoder...")
            network_architecture = dict(n_hidden_recog_1=200, \
                                        n_hidden_recog_2=50, \
                                        n_hidden_gener_1=50, \
                                        n_hidden_gener_2=200, \
                                        n_input=int(self.hyperParameters.dimAgentLevelStates * self.hyperParameters.numTimeStep), \
                                        n_z=self.hyperParameters.dimLatent)
            vae = VariationalAutoEncoder.VariationalAutoEncoder(network_architecture)
            vae.train(self.normalizedSimMicroResult, batch_size=self.hyperParameters.numAgents, training_epochs=self.hyperParameters.epochVAE,
                      learning_rate=self.hyperParameters.learningRateVAE)  # 0.001 # when training_epoch is 200, Nan will arise. When training_epoch is 100, no problem arises why Nan arise near 110~?

            vae.plot_total_loss(self.hyperParameters.dir + '/total_loss.png')
            vae.plot_reconstr_loss(self.hyperParameters.dir + '/reconst_loss.png')
            vae.plot_latent_loss(self.hyperParameters.dir + '/latent_loss.png')
            # print("simulation result : ", normalizedSimMicroResultRaw)
            representation = np.array(vae.transform(self.normalizedSimMicroResult))
            print("Representation Learning Over")

            # Dirichlet Process Mixture Model
            if clusteringAlgorithm == 'GMM':
                print("Agent Clustering by Gaussian Mixture Model...")
                gmm = mixture.GaussianMixture(n_components=numberOfClusters, covariance_type='full').fit(representation)
                agentClusters = gmm.predict(representation)
            elif clusteringAlgorithm == 'DPMM':
                print("Agent Clustering by Dirichlet Process Mixture Model...")
                dpgmm = mixture.BayesianGaussianMixture(n_components=100,
                                                        covariance_type='diag', weight_concentration_prior=1e-3).fit(
                    representation)
                agentClusters = dpgmm.predict(representation)
            elif clusteringAlgorithm == 'MeanShift':
                print("Agent Clustering by Mean Shift Model...")
                bandwidth = estimate_bandwidth(representation)
                ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
                ms.fit(representation)
                agentClusters = ms.labels_
            elif clusteringAlgorithm == 'DBSCAN':
                print("Agent Clustering by DBSCAN Model...")
                dbscan = cluster.DBSCAN().fit(representation)
                agentClusters = dbscan.labels_

            # Count the number of clusters
            numberCluster = []
            for agent in range(len(agentClusters)):
                if agentClusters[agent] not in numberCluster:
                    numberCluster.append(agentClusters[agent])
            numberCluster = len(numberCluster)
            # numberCluster = numberOfClusters

            if clusteringAlgorithm in ['GMM', 'MeanShift', 'DBSCAN']:
                compressedRepresentation = manifold.TSNE(n_components=2).fit_transform(representation)

            elif clusteringAlgorithm == 'DPMM':
                compressedRepresentation = manifold.TSNE(n_components=2).fit_transform(representation)
                # print("compressed Representation : ", compressedRepresentation)

                # Nearest Neibhborhood Model
                numberNeighbor = 500
                nbrs = NearestNeighbors(n_neighbors=numberNeighbor, algorithm='ball_tree').fit(representation)
                distances, indices = nbrs.kneighbors(representation)
                self.list = np.zeros(100)
                numberClusters = []
                for agent in range(len(agentClusters)):
                    if agentClusters[agent] not in numberClusters:
                        self.list[agentClusters[agent]] = len(numberClusters)
                        numberClusters.append(agentClusters[agent])
                # print("numberClusters : ", numberClusters)
                # print("list : ", self.list)
                mergeTargetClusters = []
                numberOfCluster = len(numberClusters)
                # print("agent Clusters : ", agentClusters.sort())
                # print("numberCluster : ", numberCluster)
                # print("number of clusters : ", numberOfCluster)
                NumberOfGroupedAgents = np.zeros(numberOfCluster)
                for agent in range(len(agentClusters)):
                    NumberOfGroupedAgents[int(self.list[agentClusters[agent]])] += 1
                # print("NumberOfGroupedAgents : ", NumberOfGroupedAgents)
                for clust in range(numberOfCluster):
                    if NumberOfGroupedAgents[clust] < self.hyperParameters.numAgents / 100.:
                        mergeTargetClusters.append(numberClusters[clust])
                # print("merge Target Clusters : ", mergeTargetClusters)
                for agent in range(len(agentClusters)):
                    if agentClusters[agent] in mergeTargetClusters:
                        temp = []
                        for neighbor in range(numberNeighbor):
                            temp.append(agentClusters[indices[agent][neighbor]])
                        agentClusters[agent] = self.most_common(temp)

                mergedAgents = []
                for agent in range(len(agentClusters)):
                    temp = []
                    for neighbor in range(numberNeighbor):
                        temp.append(agentClusters[indices[agent][neighbor]])
                    agentClusters[agent] = self.most_common(temp)
                    tempo = copy.deepcopy(temp)
                    while True:
                        try:
                            tempo.remove(agentClusters[agent])
                        except:
                            break
                    if len(tempo) * 2 > len(temp):
                        mergedAgents.append(agent)
                for agent in mergedAgents:
                    agentClusters[agent] = 100
                numberCluster = []
                for agent in range(len(agentClusters)):
                    if agentClusters[agent] not in numberCluster:
                        numberCluster.append(agentClusters[agent])
                numberCluster = len(numberCluster)
                # print("numberCluster : ", numberCluster)
                # if figureType != 1:
                #print("2nd Clustering over")
                NumberOfGroupedAgents = np.zeros(numberOfCluster)
                for agent in range(len(agentClusters)):
                    if agentClusters[agent] != 100:
                        NumberOfGroupedAgents[int(self.list[agentClusters[agent]])] += 1
                    else:
                        NumberOfGroupedAgents[-1] += 1
                #print("NumberOfGroupedAgents : ", NumberOfGroupedAgents)
                self.list = np.zeros(101)
                numberClusters = []
                for agent in range(len(agentClusters)):
                    if agentClusters[agent] not in numberClusters:
                        self.list[agentClusters[agent]] = len(numberClusters)
                        numberClusters.append(agentClusters[agent])
                for agent in range(len(agentClusters)):
                    agentClusters[agent] = self.list[agentClusters[agent]]
            print("Clustering Process Ends")
        else:
            agentClusters = []
            numberCluster = 1
        return agentClusters, numberCluster

    def most_common(self, lst):
        data = Counter(lst)
        return max(lst, key=data.get)