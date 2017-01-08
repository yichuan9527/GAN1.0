import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
from skimage.io import imsave
import os
import shutil

img_height = 28
img_width  = 28
img_size   = img_height*img_width

to_train   = True
to_restore = False
output_path = 'output'

max_epoch = 500

h1_size    = 150
h2_size    = 300
z_size     = 100
batch_size = 256

def build_generator(z_prior):
    w1 = tf.Variable(tf.truncated_normal([z_size, h1_size], stddev=0.1), name='g_w1', dtype=tf.float32)
    b1 = tf.Variable(tf.zeros([h1_size]), name='g_b1', dtype=tf.float32)
    h1 = tf.nn.relu(tf.matmul(z_prior, w1) + b1)
    w2 = tf.Variable(tf.truncated_normal([h1_size, h2_size], stddev=0.1), name='g_w2', dtype=tf.float32)
    b2 = tf.Variable(tf.zeros([h2_size]), name='g_b1', dtype=tf.float32)
    h2 = tf.nn.relu(tf.matmul(h1,w2) + b2)
    w3 = tf.Variable(tf.truncated_normal([h2_size, img_size], stddev=0.1), name='g_w3', dtype=tf.float32)
    b3 = tf.Variable(tf.zeros([img_size]), name='g_b3', dtype=tf.float32)
    h3 = tf.matmul(h2, w3) + b3
    x_generate = tf.nn.tanh(h3)
    g_params = [w1, b1, w2, b2, w3, b3]
    return x_generate, g_params

def build_discriminantor(x_data, x_generate, keep_prob):
    x_in = tf.concat(0, [x_data, x_generate])
    w1   = tf.Variable(tf.truncated_normal([img_size, h2_size], stddev=0.1), name='d_w1', dtype=tf.float32)
    b1   = tf.Variable(tf.zeros([h2_size]), name='d_b1', dtype=tf.float32)
    h1   = tf.nn.dropout(tf.nn.relu(tf.matmul(x_in, w1) + b1), keep_prob)

    w2   = tf.Variable(tf.truncated_normal([h2_size, h1_size], stddev=0.1), name='d_w2', dtype=tf.float32)
    b2   = tf.Variable(tf.zeros([h1_size]), name='d_b2', dtype=tf.float32)
    h2   = tf.nn.dropout(tf.nn.relu(tf.matmul(h1, w2) + b2), keep_prob)

    w3   = tf.Variable(tf.truncated_normal([h1_size, 1], stddev=0.1), name='d_w3', dtype=tf.float32)
    b3   = tf.Variable(tf.zeros([1]), name='d_b3', dtype=tf.float32)
    h3   = tf.matmul(h2, w3) + b3
    y_data = tf.nn.sigmoid(tf.slice(h3, [0,0], [batch_size, -1], name=None))
    y_generate = tf.nn.sigmoid(tf.slice(h3, [batch_size, 0], [-1, -1], name=None))
    d_params = [w1, b1, w2, b2, w3, b3]
    return y_data, y_generate, d_params

def show_result(batch_res, fname, grid_size=(8, 8), grid_pad=5):
    batch_res = 0.5 * batch_res.reshape((batch_res.shape[0], img_height, img_width)) + 0.5
    img_h, img_w = batch_res.shape[1], batch_res.shape[2]
    grid_h = img_h * grid_size[0] + grid_pad * (grid_size[0] - 1)
    grid_w = img_w * grid_size[1] + grid_pad * (grid_size[1] - 1)
    img_grid = np.zeros((grid_h, grid_w), dtype=np.uint8)
    for i,res in enumerate(batch_res):
        if i >= grid_size[0]*grid_size[1]:
            break
        img = (res) * 255
        img = img.astype(np.uint8)
        row = (i // grid_size[0]) * (img_h + grid_pad)
        col = (i % grid_size[1])* (img_w + grid_pad)
        img_grid[row:row + img_h, col:col + img_w] = img

    imsave(fname, img_grid)

def train():
    mnist =input_data.read_data_sets('MNIST_data',one_hot=True)

    x_data  = tf.placeholder(tf.float32, [batch_size, img_size], name='x_data')
    z_prior = tf.placeholder(tf.float32, [batch_size, z_size], name='z_prior')
    keep_prob = tf.placeholder(tf.float32, name='kepp_prob')
    gloab_step = tf.Variable(0, name='gloab_step', trainable=False)

    x_generate, g_params = build_generator(z_prior)
    y_data, y_generated, d_params = build_discriminantor(x_data, x_generate, keep_prob)

    d_loss = -(tf.log(y_data) + tf.log(1 - y_generated))
    g_loss = -tf.log(y_generated)

    optimizer = tf.train.AdamOptimizer(0.0001)

    d_train = optimizer.minimize(d_loss, var_list=d_params)
    g_train = optimizer.minimize(g_loss, var_list=g_params)

    init = tf.initialize_all_variables()
    saver = tf.train.Saver()
    sess = tf.Session()
    sess.run(init)
    if to_restore:
        chkpt_fname = tf.train.latest_checkpoint(output_path)
        saver.restore(sess. chkpt_fname)
    else:
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.mkdir(output_path)

    z_sample_val = np.random.normal(0, 1, size=(batch_size, z_size))
    z_sample_val.astype(np.float32)
    for i in range(sess.run(gloab_step), max_epoch):
        for j in range(60000 / batch_size):
            print "epoch:%s, iter:%s" % (i,j)
            x_value,_ = mnist.train.next_batch(batch_size)
            x_value = 2*x_value.astype(np.float32) - 1
            z_value = np.random.normal(0,1,size=(batch_size, z_size)).astype(np.float32)
            sess.run(d_train,
                     feed_dict={x_data:x_value, z_prior:z_value, keep_prob: np.sum(0.7).astype(np.float32)})
            if j % 1 == 0:
                sess.run(g_train,
                         feed_dict={x_data:x_value, z_prior: z_value, keep_prob:np.sum(0.7).astype(np.float32)})

        x_gen_val = sess.run(x_generate, feed_dict={z_prior: z_sample_val})
        show_result(x_gen_val, "picture/sample{0}.png".format(i))
        z_random_sample_val = np.random.normal(0, 1, size=(batch_size, z_size)).astype(np.float32)
        x_gen_val = sess.run(x_generate, feed_dict={z_prior: z_random_sample_val})
        show_result(x_gen_val, "picture/random_sample{0}.png".format(i))
        sess.run(tf.assign(gloab_step, i+1))
        saver.save(sess, os.path.join(output_path, "model"), global_step=gloab_step)

def test():
    z_prior = tf.placeholder(tf.float32, [batch_size, z_size], name="z_prior")
    x_generate, _ = build_generator(z_prior)
    chkpt_fname = tf.train.latest_checkpoint(output_path)

    init = tf.initialize_all_variables()
    sess = tf.Session()
    saver = tf.train.Saver()
    sess.run(init)
    saver.restore(sess, chkpt_fname)
    z_test_value = np.random.normal(0,1,size=(batch_size,z_size)).astype(np.float32)
    x_gene_val = sess.run(x_generate, feed_dict={z_prior:z_test_value})
    show_result(x_gene_val, "picture/test.result.png")

if __name__ == '__main__':
    if to_train:
        train()
    else:
        test()









