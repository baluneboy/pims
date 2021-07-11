#!/usr/bin/env python

import numpy as np


class NeuralNetwork:

    def __init__(self, layer_sizes):
        weight_shapes = [(a, b) for a, b in zip(layer_sizes[1:], layer_sizes[:-1])]
        self.weights = [np.random.standard_normal(s) / s[1] ** 0.5 for s in weight_shapes]
        self.biases = [np.zeros((s, 1)) for s in layer_sizes[1:]]

    def predict(self, a):
        for w, b in zip(self.weights, self.biases):
            a = self.activation(np.matmul(w, a) + b)
        return a

    @staticmethod
    def activation(x):
        return 1 / (1 + np.exp(-x))


np.load('mnist.npz')
with np.load('mnist.npz') as data:
    training_images = data['training_images']
    print(training_images.shape)

lay_sizes = (3, 5, 10)
xi = np.ones((lay_sizes[0], 1))

net = NeuralNetwork(lay_sizes)
prediction = net.predict(xi)
print(prediction)


# https://machinelearningmastery.com/implement-backpropagation-algorithm-scratch-python/
