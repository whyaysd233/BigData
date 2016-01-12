# -*- coding: utf-8 -*-
from pyspark import SparkContext, SparkConf
from pyspark.mllib.feature import HashingTF, IDF
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.regression import LabeledPoint
import re

# SPARK下实现从分词后的文本中提取出腐败行为方式的特征
# 输入：指定目录下的分词后文本 格式：<原判决书文本路径，文本分词结果（空格分离）>的键值对
#       特征词文件 keywords_crime.txt 格式：维度1|维度2...维度n
# 输出：文件格式：<判决书ID，腐败行为方式1+"\t"+腐败行为方式2+...>


def main():
    conf = SparkConf().setAppName("Test2")
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
        s = line[1].split("\n")
        return s[0:len(s) - 1]
    # <文件，内容>的键值对 => <判决书路径，判决书内容>键值对
    data = data_raw.flatMap(Doc)
    # 将判决书路径 => ID
    def DocID(string):
        s = filter(lambda x: x.isdigit(), string)
        return s[1:len(s)]
    # <判决书路径，判决书内容> => <判决书ID，判决书内容>
    data_wordsplit = data.map(lambda line: (DocID(line.split(",<")[0]), line.split(",<")[1].split(" ")))
    # 去除分词后文本之间的空格，便于后续正则表达式匹配
    def Doc_Integration(line):
        doc = ""
        for k in line[1]:
            doc += k
        return (line[0], doc)
    # <判决书ID，判决书内容（有空格）> => <判决书ID，判决书内容>
    data_doc = data_wordsplit.map(Doc_Integration)
    # 从keywords_body.txt中提取出各可能维度，用正则表达式编译
    keywords_raw = sc.textFile("/home/djt/data/keywords_crime.txt")
    keywords = keywords_raw.map(
        lambda line: re.compile(line)).collect()
    # 将<维度，set(特征词)>键值对广播
    keywords = sc.broadcast(keywords)
    # 正则表达式匹配各判决书中出现的所有腐败行为方式（即罪名）
    def keywords_stats(line):
        doc = line[1]
        # 匹配 doc是判决书内容 value[0]即正则表达式
        temp = keywords.value[0].findall(doc)
        crime_set = set(temp)
        crime = ""
        for k in crime_set:
            crime+="\t"+k
        return (line[0],crime)
    # raw：<判决书ID,所有出现的行为方式（罪名）>
    raw = data_doc.map(keywords_stats)
    after = raw.sortByKey()
    # 输出
    res = after.map(lambda (k, v): k + "\t" + v)
    res.saveAsTextFile("/home/djt/data/out")


main()
