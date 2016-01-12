# -*- coding: utf-8 -*-
import os
import sys
import jieba
import math
import re

# PYTHON中单机利用信息增益方法从训练集文本中提取出特征
# 输入：\\data\\Y-cut及\\data\\N-cut目录下文本文件
# 输出：各分词结果字典dict.txt 格式（词-正类出现次数-负类出现次数）
#       feature.txt 格式(词-IG值)
def main():
    # 预处理
    def preprocess():
        # 提取正类分词结果，用pos_word_doc的list存放每篇正类文档的分词结果；用pos_word_set的set存放所有正类文档的分词
        dir1 = os.curdir + "\\data\\Y-cut"
        files1 = os.listdir(dir1)
        pos_word_doc = list()
        pos_word_set = set()
        for name in files1:
            if name.endswith(".txt"):
                filename = dir1 + "\\" + name
                file = open(filename, "r")
                content = file.readlines()
                word_list = list()
                for line in content:
                    line.decode("utf-8")
                    seg_list = jieba.lcut(line, cut_all=False)
                    word_list.extend(seg_list)
                word_set = set(word_list)
                pos_word_doc.extend(list(word_set))
                pos_word_set = pos_word_set | word_set
                file.close()
        # 提取负类分词结果，用neg_word_doc的list存放每篇负类文档的分词结果；用neg_word_set的set存放所有正类文档的分词
        dir2 = os.curdir + "\\data\\N-cut"
        files2 = os.listdir(dir2)
        neg_word_doc = list()
        neg_word_set = set()
        for name in files2:
            if name.endswith(".txt"):
                filename = dir2 + "\\" + name
                file = open(filename, "r")
                content = file.readlines()
                word_list = list()
                for line in content:
                    line.decode("utf-8")
                    seg_list = jieba.lcut(line, cut_all=False)
                    word_list.extend(seg_list)
                word_set = set(word_list)
                neg_word_doc.extend(list(word_set))
                neg_word_set = neg_word_set | word_set
                file.close()
        # 正/负类所有文档的分词结果set all_word_set
        all_word_set = pos_word_set | neg_word_set
        word_dict = dict()
        print(len(all_word_set))
        m = 0
        # 统计各个词在正/负类中出现的次数 存在字典word_dict中，并输出到dict.txt文件
        for word in all_word_set:
            n1 = pos_word_doc.count(word)
            n2 = neg_word_doc.count(word)
            word_dict[word] = (n1, n2)
            m += 1
            if not (m % 100):
                print(m)
        out = open(os.curdir + "\\dict.txt", "w")
        for k in word_dict:
            out.write(k.encode("utf-8") + "\t" + str(word_dict[k][0]) + "\t" + str(word_dict[k][1]) + "\n")
        out.close()

    # 计算信息增益
    def GetIG():
        c1 = 233.0
        c0 = 248.0
        filename = os.curdir + "\\dict.txt"
        file = open(filename, "r")
        content = file.readlines()
        file.close()
        # list word_list_ig存储各个词及其IG值
        word_list_ig = list()
        # 遍历各个词
        for line in content:
            line.decode("utf-8")
            temp = line.split("\t")
            if len(temp) > 2:
                # 词 word
                word = temp[0]
                pos = float(temp[1])
                neg = float(temp[2])
                # word在负类中出现次数 c0_t
                c0_t = float(neg)
                # word在正类中出现次数 c1_t
                c1_t = float(pos)
                # word在负类中未出现次数 c0_no_t
                c0_no_t = float(c0 - neg)
                # word在正类中未出现次数 c1_no_t
                c1_no_t = float(c1 - pos)
                # 信息熵
                H_c = -(
                    c0 / (c0 + c1) * math.log(c0 / (c0 + c1), 2) + c1 / (c0 + c1) * math.log(c1 / (c0 + c1), 2))
                # 条件熵 出现word
                H_c_t1 = (c1_t + c0_t) / (c0 + c1) * (
                    c1_t / (c1_t + c0_t) * math.log(pos / (c1_t + c0_t) + 1e-20, 2) + c0_t / (c1_t + c0_t) * math.log(
                        c0_t / (c1_t + c0_t) + 1e-20, 2))
                # 条件熵 未出现word
                H_c_t0 = (c0_no_t + c1_no_t) / (c0 + c1) * (
                    c1_no_t / (c1_no_t + c0_no_t + 1e-20) * math.log(c1_no_t / (c1_no_t + c0_no_t + 1e-20) + 1e-20,
                                                                     2) + c0_no_t / (
                        c1_no_t + c0_no_t + 1e-20) * math.log(c0_no_t / (c1_no_t + c0_no_t + 1e-20) + 1e-20, 2))
                # 信息增益计算
                IG = H_c + H_c_t1 + H_c_t0
                word_list_ig.append((word, IG))
        # 根据各word的IG值排序，取前若干个作为最后提取出的特征
        word_list_ig = sorted(word_list_ig, key=lambda item: item[1], reverse=True)
        out = open(os.curdir + "\\feature.txt", "w")
        for k in word_list_ig:
            out.write(k[0] + "\t" + str(k[1]) + "\n")
        out.close()

    preprocess()
    GetIG()
    # # 比较根据信息增益和卡方统计两种方法提取出的特征
    # filename1 = os.curdir + "\\features_IG.txt"
    # file1 = open(filename1, "r")
    # content1 = file1.readlines()
    # file1.close()
    # filename2 = os.curdir + "\\features_chi2.txt"
    # file2 = open(filename2, "r")
    # content2 = file2.readlines()
    # file2.close()
    # set1 = set()
    # set2 = set()
    # num = 80
    # for (a, b) in zip(content1[1:num], content2[1:num]):
    #     a.decode("utf-8")
    #     temp1 = a.split("\t")
    #     res1 = temp1[0]
    #     b.decode("utf-8")
    #     set1.add(res1)
    #     temp2 = b.split(",")
    #     res2 = temp2[0]
    #     set2.add(res2)
    # print(len(set1 & set2))

main()
