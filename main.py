# -*- coding: utf-8 -*-
#/usr/bin/python3
import sys
sys.path.append("/")
import tensorflow as tf
from model import Volume_GCN
from tqdm import tqdm
from module import Graphs
from load_data import train_data
from sklearn import metrics
from args import parse_args
import math
import time
import os

# os.environ['CUDA_VISIBLE_DEVICES'] = ""

def main():
    time_start = time.time()
    hp = parse_args()
    print("开始读取数据")
    G, labeled_nodes = Graphs(hp)
    node_num = len(G.nodes())
    hp.node_num = node_num
    hp.labeled_node = len(labeled_nodes)
    # print(node_num)
    print("读取数据完成，填入模型参数")
    arg = {}
    arg['hp'] = hp
    print("构建模型")
    m = Volume_GCN(arg)
    A = tf.placeholder(dtype=tf.float32, shape=(node_num, node_num), name='A')
    xs = tf.placeholder(dtype=tf.int32, shape=(hp.labeled_node), name='xs')
    ys = tf.placeholder(dtype=tf.float32, shape=(hp.labeled_node), name='ys')
    xu = tf.placeholder(dtype=tf.int32, shape=(node_num-hp.labeled_node), name='xu')

    loss, train_op, global_step = m.train(A, xs, ys)
    predict_label = m.predict(A, xu)
    dA, dxs, dys, dxu, dyu = train_data(hp, node_num, G, labeled_nodes)

    print("开始训练")
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        _gs = sess.run(global_step)
        for i in tqdm(range(hp.epochs)):
            _loss, _, _gs = sess.run([loss, train_op, global_step], feed_dict={A:dA, xs:dxs, ys:dys})
            print("   Epoch : %02d   loss : %.2f" % (i+1, _loss))
        _pre = sess.run([predict_label], feed_dict={A:dA, xu:dxu})
        print("Fin AUC is : %.2lf"%(metrics.auc(dyu, _pre)))
    time_end = time.time()
    all_time = int(time_end - time_start)
    hours = int(all_time / 3600)
    minute = int((all_time - 3600 * hours) / 60)
    print('totally cost  :  ', hours, 'h', minute, 'm', all_time - hours * 3600 - 60 * minute)

if __name__ == '__main__':
    main()