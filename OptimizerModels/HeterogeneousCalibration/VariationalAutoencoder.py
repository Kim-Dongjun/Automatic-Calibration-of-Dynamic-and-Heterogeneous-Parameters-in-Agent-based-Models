import time
import os
import numpy as np
import tensorflow as tf
import sys
import matplotlib.pyplot as plt
from tensorflow.examples.tutorials.mnist import input_data


class VariationalAutoEncoder:

    network_architecture = []
    transfer_fct = 0

    x = []
    x_reconstr_mean = []
    z = []
    z_mean = []
    z_sigma = []

    sess = 0
    cost = 0
    optimizer = 0

    total_cost_list = []
    reconstr_cost_list = []
    latent_cost_list = []


    def __init__(self, network_architecture, transfer_fct=tf.nn.softplus):
        tf.reset_default_graph()
        self.network_architecture = network_architecture
        self.transfer_fct = transfer_fct

        self.x = tf.placeholder(tf.float32, [None, network_architecture["n_input"]])

    def _create_network(self, batch_size):
        network_weights = self._initialize_weights(**self.network_architecture)

        self.z_mean, self.z_sigma = self._recognition_network(network_weights["weights_recog"],
                                                                     network_weights["biases_recog"])

        n_z = self.network_architecture["n_z"]
        eps = tf.random_normal((batch_size, n_z), 0, 1, dtype=tf.float32)

        self.z = tf.add(self.z_mean, tf.multiply(self.z_sigma, eps))

        self.x_reconstr_mean = self._generator_network(network_weights["weights_gener"],
                                                       network_weights["biases_gener"])

    def _initialize_weights(self, n_hidden_recog_1, n_hidden_recog_2, n_hidden_gener_1, n_hidden_gener_2, n_input, n_z):

        all_weights = dict()

        all_weights['weights_recog'] = {
            'h1': tf.Variable(self.xavier_init(n_input, n_hidden_recog_1), name='weights_recog_h1'), \
            'h2': tf.Variable(self.xavier_init(n_hidden_recog_1, n_hidden_recog_2), name='weights_recog_h2'), \
            'out_mean': tf.Variable(self.xavier_init(n_hidden_recog_2, n_z), name='weights_recog_out_mean'), \
            'out_log_sigma': tf.Variable(self.xavier_init(n_hidden_recog_2, n_z), name='weight_recog_out_log_sigma')}

        all_weights['biases_recog'] = {
            'b1': tf.Variable(tf.zeros([n_hidden_recog_1], dtype=tf.float32), name='biases_recog_b1'), \
            'b2': tf.Variable(tf.zeros([n_hidden_recog_2], dtype=tf.float32), name='biases_recog_b2'), \
            'out_mean': tf.Variable(tf.zeros([n_z], dtype=tf.float32), name='biases_recog_out_mean'), \
            'out_log_sigma': tf.Variable(tf.zeros([n_z], dtype=tf.float32), name='biases_recog_out_log_sigma')}

        all_weights['weights_gener'] = {
            'h1': tf.Variable(self.xavier_init(n_z, n_hidden_gener_1), name='weights_gener_h1'), \
            'h2': tf.Variable(self.xavier_init(n_hidden_gener_1, n_hidden_gener_2), name='weights_gener_h2'), \
            'out_mean': tf.Variable(self.xavier_init(n_hidden_gener_2, n_input), name='weights_gener_out_mean')}

        all_weights['biases_gener'] = {
            'b1': tf.Variable(tf.zeros([n_hidden_gener_1], dtype=tf.float32), name='biases_gener_b1'), \
            'b2': tf.Variable(tf.zeros([n_hidden_gener_2], dtype=tf.float32), name='biases_gener_b2'), \
            'out_mean': tf.Variable(tf.zeros([n_input], dtype=tf.float32), name='biases_gener_out_mean')}
        return all_weights

    def _recognition_network(self, weights, biases):
        #layer_1 = tf.nn.dropout(self.transfer_fct(tf.add(tf.matmul(self.x, weights['h1']), biases['b1'])))
        #layer_2 = tf.nn.dropout(self.transfer_fct(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])))
        layer_1 = self.transfer_fct(tf.add(tf.matmul(self.x, weights['h1']), biases['b1']))
        layer_2 = self.transfer_fct(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2']))
        z_mean = tf.add(tf.matmul(layer_2, weights['out_mean']), biases['out_mean'])
        z_sigma = 1e-6 + tf.nn.softplus(tf.add(tf.matmul(layer_2, weights['out_log_sigma']), biases['out_log_sigma']))

        return (z_mean, z_sigma)

    def _generator_network(self, weights, biases):
        #layer_1 = tf.nn.dropout(self.transfer_fct(tf.add(tf.matmul(self.z, weights['h1']), biases['b1'])))
        #layer_2 = tf.nn.dropout(self.transfer_fct(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])))
        layer_1 = self.transfer_fct(tf.add(tf.matmul(self.z, weights['h1']), biases['b1']))
        layer_2 = self.transfer_fct(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2']))
        x_reconstr_mean = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['out_mean']), biases['out_mean']))

        return x_reconstr_mean

    def _create_loss_optimizer(self, learning_rate):
        self.reconstr_loss = -tf.reduce_sum(self.x*tf.log(1e-10+self.x_reconstr_mean)+(1-self.x)*tf.log(1e-10+1-self.x_reconstr_mean),1)
        #self.reconstr_loss = tf.reduce_sum(
        #    tf.nn.sigmoid_cross_entropy_with_logits(logits=self.x_reconstr_mean, labels=self.x), reduction_indices=1)
        self.latent_loss = -0.5 * tf.reduce_sum(
            1 + 2*tf.log(self.z_sigma) - tf.square(self.z_mean) - tf.pow(self.z_sigma,2), 1)

        self.reconstr_loss = tf.reduce_mean(self.reconstr_loss)
        self.latent_loss = tf.reduce_mean(self.latent_loss)
        self.cost = tf.reduce_mean(self.reconstr_loss + self.latent_loss)
        # self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(self.cost)

        #optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        #optimizer = tf.train.AdagradOptimizer(learning_rate=learning_rate)
        #optimizer = tf.train.AdadeltaOptimizer(learning_rate=learning_rate)
        optimizer = tf.train.MomentumOptimizer(learning_rate=learning_rate, momentum = 0.9)
        #optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
        gvs = optimizer.compute_gradients(self.cost)

        for grad, var in gvs:
            if grad == None:
                print(var)
        capped_gvs = [(tf.clip_by_value(grad, 1e-8, 1-1e-8), var) for grad, var in gvs]
        self.optimizer = optimizer.apply_gradients(capped_gvs)

    def partial_fit(self, x):
        opt, cost, reconstr_loss_, latent_loss_ = self.sess.run((self.optimizer, self.cost, self.reconstr_loss, self.latent_loss), feed_dict={self.x: x})
        return cost, reconstr_loss_, latent_loss_

    def transform(self, x):
        return self.sess.run(self.z_mean, feed_dict={self.x: x})

    def generate(self, z_mu=None):
        if z_mu is None:
            z_mu = np.random.normal(size=self.network_architecture["n_z"])
        return self.sess.run(self.x_reconstr_mean, feed_dict={self.z: z_mu})

    def reconstruct(self, x):
        return self.sess.run(self.x_reconstr_mean, feed_dict={self.x: x})

    def xavier_init(self, fan_in, fan_out, constant=1):
        low = -constant * np.sqrt(6.0 / (fan_in + fan_out))
        high = constant * np.sqrt(6.0 / (fan_in + fan_out))

        return tf.random_uniform((fan_in, fan_out), minval=low, maxval=high, dtype=tf.float32)

    def train(self, trainX, batch_size=100, training_epochs=10, learning_rate=0.001):
        self._create_network(batch_size)
        self._create_loss_optimizer(learning_rate)

        init = tf.global_variables_initializer()
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
        #self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        self.sess = tf.Session(config = config)
        self.sess.run(init)

        self.total_cost_list = []
        self.reconstr_cost_list = []
        self.latent_cost_list = []
        startTime = time.time()
        for epoch in range(training_epochs):
            avg_cost = 0.
            avg_reconstr_loss = 0.
            avg_latent_loss = 0.
            total_batch = int(len(trainX) / batch_size)
            if epoch % 500 == 499:
                print("epoch number : ", epoch + 1, "/", training_epochs)
            for i in range(total_batch):
                batch = []
                for j in range(batch_size):
                    batch.append(trainX[i * batch_size + j])
                cost, reconstr_loss_, latent_loss_ = self.partial_fit(batch)
                #print('Cost : ' + str(cost))
                avg_cost += cost / len(batch) * batch_size
                avg_reconstr_loss += reconstr_loss_ / len(batch) * batch_size
                avg_latent_loss += latent_loss_ / len(batch) * batch_size
                #print('Batch Shape : ' + str(len(batch)) + " x " + str(len(batch[0])))
            #print("Epoch : ", '%04d' % (epoch + 1), " Cost = ", "{:.9f}".format(avg_cost))
            #print("Elapsed Time : " + str((time.time() - startTime)))  # - startTime.microsecond) / 1e6))
            self.total_cost_list.append(avg_cost)
            self.reconstr_cost_list.append(avg_reconstr_loss)
            self.latent_cost_list.append(avg_latent_loss)
        #return

    def plot_total_loss(self, strFileName):
        training_epochs = len(self.total_cost_list)
        t = np.arange(0, training_epochs, 1)
        # avg_cost plot
        s = self.total_cost_list
        #print(t)
        #print(s)
        #print(self.reconstr_cost_list[0])
        plt.plot(t, s)
        plt.xlabel('epoch')
        plt.ylabel('average total cost')
        plt.title('average total cost')
        plt.grid(True)
        plt.savefig(strFileName)
        plt.close()

    def plot_reconstr_loss(self, strFileName):
        training_epochs = len(self.total_cost_list)
        t = np.arange(0, training_epochs, 1)
        # avg_cost plot
        s = self.reconstr_cost_list
        #print(t)
        #print(s)
        plt.plot(t, s)
        plt.xlabel('epoch')
        plt.ylabel('average reconstruct cost')
        plt.title('average reconstruct cost')
        plt.grid(True)
        plt.savefig(strFileName)
        plt.close()

    def plot_latent_loss(self, strFileName):
        training_epochs = len(self.total_cost_list)
        t = np.arange(0, training_epochs, 1)
        # avg_cost plot
        s = self.latent_cost_list
        #print(t)
        #print(s)
        plt.plot(t, s)
        plt.xlabel('epoch')
        plt.ylabel('average latent cost')
        plt.title('average latent cost')
        plt.grid(True)
        plt.savefig(strFileName)
        plt.close()

        '''u = []
        for i in range(len(s)):
            u.append(s[i][len(s[0])-1])
        plt.plot(t,u)
        plt.xlabel('epoch')
        plt.ylabel('average latent cost')
        plt.title('average latent cost')
        plt.grid(True)
        plt.savefig(strFileName)
        plt.close()'''

    def plot_sum(self, strFileName):
        training_epochs = len(self.total_cost_list)
        t = np.arange(0, training_epochs, 1)
        s1 = self.reconstr_cost_list
        s2 = self.latent_cost_list
        s = []
        for i in range(len(u)):
            s.append(s1[i] + s2[i])
        #print(s)
        plt.plot(t, s)
        plt.xlabel('epoch')
        plt.ylabel('average SUM cost')
        plt.title('average SUM cost')
        plt.grid(True)
        plt.savefig(strFileName)
        plt.close()

    def plotReconstruct(self, testData, strFileName):
        idxLastSlash = strFileName.rfind("/")
        if os.path.exists(strFileName[0:idxLastSlash]) == False:
            os.makedirs(strFileName[0:idxLastSlash])

        x_reconstruct = self.reconstruct(testData)
        plt.figure(figsize=(8, 12))
        for i in range(5):
            plt.subplot(5, 2, 2 * i + 1)
            plt.imshow(testData[i].reshape(28, 28), vmin=0, vmax=1, cmap="gray")
            plt.title("Test Input")
            plt.colorbar()

            plt.subplot(5, 2, 2 * i + 2)
            plt.imshow(x_reconstruct[i].reshape(28, 28), vmin=0, vmax=1, cmap="gray")
            plt.title("Reconstruction")
            plt.colorbar()

        plt.tight_layout()
        plt.savefig(strFileName, bbox_inches='tight')
        plt.show()
        plt.close()

    def plotScatter2D(self, testDataFeature, testDataClass, strFileName):
        idxLastSlash = strFileName.rfind("/")
        if os.path.exists(strFileName[0:idxLastSlash]) == False:
            os.makedirs(strFileName[0:idxLastSlash])

        z_mu = self.transform(testDataFeature)
        plt.figure(figsize=(8, 6))
        plt.scatter(z_mu[:, 0], z_mu[:, 1], c=np.argmax(testDataClass, 1))
        plt.colorbar()
        plt.grid()

        plt.tight_layout()
        plt.savefig(strFileName, bbox_inches='tight')
        plt.close()

    def plotManifold2D(self, intNumX1, intNumX2, maxX1, minX1, maxX2, minX2, batch_size, strFileName):
        x1s = np.linspace(minX1, maxX1, intNumX1)
        x2s = np.linspace(minX2, maxX2, intNumX2)
        canvas = np.empty((28 * intNumX2, 28 * intNumX1))
        for i, yi in enumerate(x1s):
            for j, xi in enumerate(x2s):
                z_mu = np.array([[xi, yi]] * batch_size)
                x_mean = self.generate(z_mu)
                canvas[(intNumX1 - i - 1) * 28:(intNumX1 - i) * 28, j * 28:(j + 1) * 28] = x_mean[0].reshape(28, 28)
        plt.figure(figsize=(8, 6))
        xi, yi = np.meshgrid(x1s, x2s)
        plt.imshow(canvas, origin='upper', cmap='gray')
        plt.tight_layout()
        plt.savefig(strFileName, bbox_inches='tight')
        plt.close()


if __name__ == "__main__":

    network_architecture = dict(n_hidden_recog_1=500, \
                                n_hidden_recog_2=500, \
                                n_hidden_gener_1=500, \
                                n_hidden_gener_2=500, \
                                n_input=784, \
                                n_z=20)

    #np.random.seed(0)
    #tf.set_random_seed(0)

    mnist = input_data.read_data_sets('MNIST_DATA', one_hot=True)
    n_samples = mnist.train.num_examples

    #iterations = [1, 5]
    iterations = [1]
    testX = mnist.test.next_batch(5000)[0]
    trainX = []
    for i in range(n_samples):
        tempTuple = mnist.train.next_batch(1)[0]
        trainX.append(tempTuple[0])

    '''for i in range(len(iterations)):
        vae = VariationalAutoEncoder(network_architecture)
        # vae.train(trainX,batch_size=5000,training_epochs=iterations[i],learning_rate=0.001)
        vae.train(trainX, batch_size=5000, training_epochs=30, learning_rate=0.001)
        vae.plotReconstruct(testX, './log/VAE-Reconstruct-iteration-' + str(iterations[i]) + '.png')
        vae.plot_total_loss('./log/VAE-Total-cost-iteration-' + str(iterations[i]) + '.png')
        vae.plot_reconstr_loss('./log/VAE-Reconstruct-cost-iteration-' + str(iterations[i]) + '.png')
        vae.plot_latent_loss('./log/VAE-Latent-cost-iteration-' + str(iterations[i]) + '.png')
        # vae.plot_sum('./log/VAE-SUM-cost-iteration-'+str(iterations[i])+'.png')'''

    network_architecture2D = dict(n_hidden_recog_1=500, \
                                  n_hidden_recog_2=500, \
                                  n_hidden_gener_1=500, \
                                  n_hidden_gener_2=500, \
                                  n_input=784, \
                                  n_z=2)

    testX, testY = mnist.test.next_batch(1000)

    print("I am trainX:",trainX[0])
    for i in range(len(iterations)):
        tf.reset_default_graph()
        vae2D = VariationalAutoEncoder(network_architecture2D)
        # vae2D.train(trainX,batch_size=5000,training_epochs=iterations[i],learning_rate=0.001)
        vae2D.train(trainX, batch_size=5000, training_epochs=30, learning_rate=0.001)
        vae2D.plotScatter2D(testX, testY, './log/VAE-2D-Scatter-iteration-' + str(iterations[i]) + '.png')
        vae2D.plotManifold2D(28, 28, -3, 3, -3, 3, 5000,
                             './log/VAE-2D-Manifold-iteration-' + str(iterations[i]) + '.png')
        vae2D.plot_total_loss('./log/VAE-2D-Total-cost-iteration-' + str(iterations[i]) + '.png')
        vae2D.plot_reconstr_loss('./log/VAE-2D-Reconstruct-cost-iteration-' + str(iterations[i]) + '.png')
        vae2D.plot_latent_loss('./log/VAE-2D-Latent-cost-iteration-' + str(iterations[i]) + '.png')
        # vae2D.plot_sum('./log/VAE-2D-SUM-cost-iteration-'+str(iterations[i])+'.png')