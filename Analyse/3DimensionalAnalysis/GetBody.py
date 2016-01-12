# -*- coding: utf-8 -*-
from pyspark import SparkContext, SparkConf
from pyspark.mllib.feature import HashingTF, IDF
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.regression import LabeledPoint
import re
# SPARK下实现从分词后的文本中提取出腐败行为主体的特征
# 输入：指定目录下的分词后文本 格式：<原判决书文本路径，文本分词结果（空格分离）>的键值对
#       特征词文件 keywords_body.txt 格式：<维度,该维度对应的可能特征词>
# 输出：文件格式：<判决书ID，最显著的行为主体维度，对应特征词词频>

def main():
    conf = SparkConf().setAppName("Test")
    sc = SparkContext(conf=conf)
    # new_dict函数将<tuple,value>键值对转换成<tuple_1,dict(tuple_2,value)>键值对
    def new_dict(line):
        Dict = dict()
        Dict[line[0][1]] = line[1]
        return (line[0][0], Dict)
    # 读取原始文件，形成<文件，内容>的键值对
    data_raw = sc.wholeTextFiles("/home/djt/data/proclassified")
    # Doc函数将<文件，内容>键值对中内容按行split，每一行即对应一封判决书的内容
    def Doc(line):
        s=line[1].split("\n")
        return s[0:len(s)-1]
    # <文件，内容>的键值对 => <判决书路径，判决书内容>键值对
    data = data_raw.flatMap(Doc)
    # 将判决书路径 => ID
    def DocID(string):
        s = filter(lambda x:x.isdigit(),string)
        return s[1:len(s)]
    # <判决书路径，判决书内容> => <判决书ID，判决书内容> => <判决书ID,分词> => <(判决书ID,分词),1>
    data_wordsplit = data.map(lambda line: (DocID(line.split(",<")[0]),line.split(",<")[1].split(" "))).flatMapValues(lambda v: v).map(
        lambda (k, v): ((k, v), 1))
    # <(判决书ID,分词),1> => <(判决书ID,分词),词频> => <判决书ID,{分词,词频}>
    data_wordcount = data_wordsplit.reduceByKey(lambda x, y: x + y).map(new_dict)
    # <判决书ID,{分词,词频}> => <判决书ID,所有{分词,词频}的词典>
    data_worddict = data_wordcount.reduceByKey(lambda d1, d2: dict(d1, **d2))  # d2 is copy not deepcopy
    # 从keywords_body.txt中提取出各维度对应的特征词，存成<维度，set(特征词)>键值对
    semicolon = "；"
    keywords_raw = sc.textFile("/home/djt/data/keywords_body.txt")
    keywords = keywords_raw.map(
        lambda line: (line.split("\t")[0], set(line.split("\t")[1].split(semicolon.decode("utf-8"))))).collect()
    # 将<维度，set(特征词)>键值对广播
    keywords = sc.broadcast(keywords)
    # 统计各判决书中对应腐败主体各个维度的特征词及其词频
    def keywords_stats(doc):
        # wordset 判决书中出现的所有word的set
        wordset = set(doc[1].keys())
        wordset.remove("")
        stats = dict()
        # keywords.value 腐败主体各个维度及特征词set <k,v>
        for k, v in keywords.value:
            s = 0
            # 求wordset与v交集 得到判决书中出现的k维度的特征词，并统计词频
            intersection = v & wordset
            for e in intersection:
                s += doc[1][e]
            stats[k] = s
        return (doc[0], stats)

    # 对每一封判决书，遍历各个维度，得到最显著的腐败行为主体维度
    def main_step(doc):
        s=0
        f=""
        for k in doc:
            if doc[k]>s:
                s=doc[k]
                f=k
        return (f,s)
    # raw：<判决书ID,（维度,词频)>
    raw = data_worddict.map(keywords_stats).map(lambda (k,v):  (k,main_step(v)))
    after = raw.sortByKey()
    # 输出
    res = after.map(lambda (k,v):k+"\t"+v[0]+"\t"+str(v[1]))
    res.saveAsTextFile("/home/djt/data/out")


main()
