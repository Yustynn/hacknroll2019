import tensorflow as tf
import tensorflow.contrib.slim as slim


class MNIST:
    def __init__(self):
        self.x = tf.placeholder(tf.float32, shape=[None, 784])
        self.y = tf.placeholder(tf.int64, shape=[None])
        self.keep_prob = tf.placeholder(tf.float32)

        x_image = tf.reshape(self.x, [-1, 28, 28, 1])
        
        with tf.variable_scope('mnist') as scope:
            logits = self.network(x_image, self.keep_prob)
            self.out = tf.nn.softmax(logits)
            
        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=self.y, logits=logits)
        self.loss = tf.reduce_mean(cross_entropy)
        
        correct_prediction = tf.equal(tf.argmax(self.out, 1), self.y)
        self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        
        
    def network(self, inp, keep_prob):
        net = slim.conv2d(inp, 32, [5, 5], scope='conv1')
        net = slim.max_pool2d(net, [2, 2], scope='pool1')
        
        net = slim.conv2d(inp, 64, [5, 5], scope='conv2')
        net = slim.max_pool2d(net, [2, 2], scope='pool2')
        
        net = slim.flatten(net, scope='flat')
        
        net = slim.fully_connected(net, 1024, scope='fc1')
        net = slim.dropout(net, keep_prob, scope='drop1')
        
        net = slim.fully_connected(net, 10, activation_fn=None, scope='out')
        return net
