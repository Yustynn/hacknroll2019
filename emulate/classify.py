import numpy as np
import cv2
import tensorflow as tf
from model import MNIST

model = MNIST()
saver = tf.train.Saver()
sess = tf.Session()
saver.restore(sess, 'models/mnist')


def preprocess(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.bitwise_not(image)
    image = image / 255
    return image.flatten()


def classify(image):
    results = sess.run(model.out, {
        model.x: [preprocess(image)],
        model.keep_prob: 1.0
    })[0]
    return np.argmax(results)
