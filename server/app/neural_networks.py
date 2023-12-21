from tensorflow.keras.models import Model
import tensorflow as tf
from tensorflow.keras import layers

class AnomalyDetector(Model):
    def __init__(self, activation):
        super(AnomalyDetector, self).__init__()
        self.encoder = tf.keras.Sequential([
            layers.Dense(128, activation = activation),
            layers.Dense(64, activation = activation),
            layers.Dense(32, activation = activation),
            layers.Dense(16, activation = activation),
            layers.Dense(8, activation = activation)
        ])

        self.decoder = tf.keras.Sequential([
            layers.Dense(16, activation = activation),
            layers.Dense(32, activation = activation),
            layers.Dense(64, activation = activation),
            layers.Dense(128, activation = activation),
            layers.Dense(1, activation = 'linear')
        ])

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
    

class AR_NN(Model):

    def __init__(self, activation_function, loss = 'mse', optimizer = 'adam'):
        super(AR_NN, self).__init__()
        self.layer1 = layers.Dense(128, activation = activation_function)
        self.layer2 = layers.Dense(256, activation = activation_function)
        self.layer3 = layers.Dense(512, activation = activation_function)
        self.layer4 = layers.Dense(1024, activation = activation_function)
        self.layer5 = layers.Dense(2048, activation = activation_function)
        self.layer6 = layers.Dense(2048, activation = activation_function)
        self.layer7 = layers.Dense(1024, activation = activation_function)
        self.layer8 = layers.Dense(512, activation = activation_function)
        self.layer9 = layers.Dense(256, activation = activation_function)
        self.output_layer = layers.Dense(1, activation = 'linear')
        self.compile(loss = loss, optimizer = optimizer)

    def call(self, X):
        return self.output_layer(self.layer9(self.layer8(self.layer7(self.layer6(self.layer5(self.layer4(self.layer3(self.layer2(self.layer1(X))))))))))