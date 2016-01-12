# coding=utf-8
"""
简介：这个程序基于scikit-learn包实现了lda文档主题模型。

输入：data文件，内含16151篇分词后的法律文档。

输出：Latent Dirichlet Allocation文件，内含主题编号，主题关键词（概率最大的10个词），最可能属于这个主题的文档编号

功能：提取法律文档的词频特征，根据词频特征训练lda主题模型，利用主题平均相似度确定最佳主题个数。再
根据最佳主题个数训练lda模型，并把结果保存在Latent Dirichlet Allocation文件中。
"""
from __future__ import print_function
from time import time
import numpy as np
import scipy.io as sio
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# 参数设置，16151文档，词频最高的1000个单词作为特征，10个主题，描述每个主题的单词个数10
n_samples = 16151
n_features = 1000
n_topics = 10
n_top_words = 10


# 输出学习结果到Latent Dirichlet Allocation文件中
def print_top_words(model, feature_names, n_top_words, title, index):
    f = open(str(model)[:str(model).find("(")], 'w')
    for topic_idx, topic in enumerate(model.components_):
        if not len(np.argwhere(index == topic_idx)) == 0:
            f.write(" ".join([feature_names[i].encode('utf8') for i in topic.argsort()[:-n_top_words - 1:-1]]))
            f.write('|')
            for i in range(0, n_samples):
                if (index[i] == topic_idx):
                    f.write(title[i] + ' ')
            f.write('\n')
    f.close()


# print()


# 从data文件中读入数据
print("Loading dataset...")
t0 = time()
f = open('data')
title = []
data = []
for line in f:
    line = line.strip()
    items = line.split('\t', 1)
    title.append(items[0].decode('utf8'))
    data.append(items[1].decode('utf8'))
print("done in %0.3fs." % (time() - t0))

# 提取词频特征用于LDA学习
print("Extracting tf features for LDA...")
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=n_features,
                                stop_words='english')
t0 = time()
tf = tf_vectorizer.fit_transform(data)
print("done in %0.3fs." % (time() - t0))

# 计算在不同主题个数下学习出的LDA模型中平均主题相似度，并根据其搜索最佳主题个数
feature_names = tf_vectorizer.get_feature_names()
grids = np.logspace(5, 7, 9, base=2)
perp = np.zeros((len(grids), 1))
scor = np.zeros((len(grids), 1))
percent = np.zeros((len(grids), 1))
x = np.zeros((len(grids), 1))
print("Fitting LDA models with tf features, n_samples=%d and n_features=%d" % (n_samples, n_features))
t = 0
for i in grids:
    count = 0
    lda = LatentDirichletAllocation(n_topics=int(i), max_iter=10, learning_method='online', learning_offset=50.,
                                    random_state=0)
    t0 = time()
    model = lda.fit(tf)
    perp[t] = model.perplexity(tf)
    scor[t] = model.score(tf)
    x[t] = int(i)
    for topicx in model.components_:
        for topicy in model.components_:
            if not (topicx == topicy).all():
                count = count + np.dot(topicx, topicy.T) / np.sqrt(np.dot(topicx, topicx.T) * np.dot(topicy, topicy.T))
    percent[t] = count / (i * (i - 1))
    print("%d: done in %0.3fs.\tperplexity:%f.\tscores:%f,\tpercent:%f." % (
    int(i), time() - t0, perp[t], scor[t], percent[t]))
    t = t + 1
sio.savemat('result.mat', {'perp': perp, 'score': scor, 'percent': percent})

# 在最佳主题个数下训练LDA模型，并将训练结果保存在输出文件中
j = 50
lda = LatentDirichletAllocation(n_topics=j, max_iter=30, learning_method='online', learning_offset=50., random_state=0)
W = lda.fit_transform(tf)
index = np.zeros((n_samples, 1))
for i in range(0, n_samples):
    index[i] = np.argmax(W[i, :])
tf_feature_names = tf_vectorizer.get_feature_names()
print_top_words(lda, tf_feature_names, n_top_words, title, index)
