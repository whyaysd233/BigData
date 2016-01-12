from pyspark import SparkContext, SparkConf
from pyspark.mllib.feature import HashingTF, IDF
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.regression import LabeledPoint
import re

dir = '/home/xsran/IdeaProjects/hadoop1/data/'


def main():
    conf = SparkConf().setAppName("Test")
    sc = SparkContext(conf=conf)

    # load tagged datasets as training data
    dataY0 = sc.wholeTextFiles('/home/xsran/IdeaProjects/hadoop1/data/Y-cut')
    dataN0 = sc.wholeTextFiles('/home/xsran/IdeaProjects/hadoop1/data/N-cut')

    # split text into words
    dataN = dataN0.map(lambda x: x[1].split(" "))
    dataY = dataY0.map(lambda x: x[1].split(" "))

    # merge the positive and negative into a single dataset
    dataA = dataY.union(dataN)

    # map words list into (word,1) tuple
    words = dataA.flatMap(lambda x: x).map(lambda x: (x, 1))
    # counting the number of words
    wordCount = words.reduceByKey(lambda x, y: x + y).map(lambda x: (x[1], x[0])).sortByKey(ascending=False)
    wordCount.cache()

    # saving this results
    # wordCount.map(lambda x:'%s,%s' % (x[1],x[0])).saveAsTextFile(dir+'wordCount')
    # wordCount.map(lambda x:(x[1],x[0])).saveAsTextFile(dir+'wordCount_rep')

    # filter this words list. Only keep the words with a certain frequency as features
    # feature_count: (features word, count)
    feature_count = wordCount.filter(lambda x: 150 < x[0] < 5000).map(lambda x: (x[1], x[0]))

    # count the word frequency in positive and negative case respectively.
    dataN1 = dataN0.flatMap(lambda x: [(w, 1) for w in set(x[1].split(" "))]).reduceByKey(lambda x, y: x + y)
    dataY1 = dataY0.flatMap(lambda x: [(w, 1) for w in set(x[1].split(" "))]).reduceByKey(lambda x, y: x + y)
    # dataA1: (word,(N num,Y num))
    dataA1 = dataN1.fullOuterJoin(dataY1).mapValues(lambda x: (x[0] if x[0] else 0, x[1] if x[1] else 0))

    fs = feature_count.map(lambda x: (x[0], 0))

    totalNnum = dataN0.count()
    totalYnum = dataY0.count()
    # only keep those words in the feature_count
    # dataA2:(word,(N num,Y num))
    dataA2 = dataA1.rightOuterJoin(fs).mapValues(lambda x: x[0]).filter(
        lambda x: x[1][0] != totalNnum and x[1][1] != totalYnum)

    # compute the chi square values
    dataA3 = dataA2.mapValues(lambda x: (x, (totalNnum - x[0], totalYnum - x[1]), totalNnum + totalYnum))
    dataX2 = dataA3.mapValues(lambda x: (float(x[0][0] * x[1][1] - x[0][1] * x[1][0]) ** 2 * x[2]) / (
        (x[0][0] + x[0][1]) * (x[1][0] + x[1][1]) * (x[0][0] + x[1][0]) * (x[0][1] + x[1][1])))
    # sorting
    dataX2 = dataX2.sortBy(lambda x: abs(x[1]), ascending=False)

    # only keep 100 features with highest chi square values
    # features: this variable only keep the 100 words.
    features = dataX2.map(lambda x: x[0]).collect()[:100]
    # features_x2: this variable record the chi square values of each features
    features_x2 = dataX2.collect()[:100]

    # broadcasting those data to spark's worker nodes.
    features = sc.broadcast(features)
    features_x2 = sc.broadcast(features_x2)

    # this function is used to extract features from a case
    def make_feature(doc):
        doc = doc.split(" ")
        f = []
        for i in features.value:
            f.append(doc.count(i))
        return f

    def make_feature2(doc):
        doc = doc.split(" ")
        f = []
        for k, v in features_x2.value:
            a = doc.count(k)
            a = v if a else 0
            f.append(a)
        return f

    # convert case into features
    fN = dataN0.mapValues(make_feature2)
    fY = dataY0.mapValues(make_feature2)

    # fN.repartition(1).map(lambda x:(x[0].split('/')[-1][:-4],x[1])).saveAsTextFile(dir+'VecN')
    # fY.repartition(1).map(lambda x:(x[0].split('/')[-1][:-4],x[1])).saveAsTextFile(dir+'VecY')

    fN = fN.map(lambda x: x[1])
    fY = fY.map(lambda x: x[1])

    # sc.stop()

    # convert features into LabeledPoint to train the model.
    fNtl = fN.map(lambda x: LabeledPoint(0, x))
    fYtl = fY.map(lambda x: LabeledPoint(1, x))

    # union the positive and negative data and train the NaiveBayes model.
    fTrain = fNtl.union(fYtl)
    bn = NaiveBayes.train(fTrain)

    # load the all untagged data
    inputs = [sc.wholeTextFiles('/home/xsran/tmp/BigData/data_c_' + str(i)) for i in range(10)]
    input = sc.union(inputs)
    # extracting features and use the NaiveBayes model to predict the case.
    predict = input.mapValues(make_feature2).mapValues(bn.predict)
    result = input.join(predict).filter(lambda x: x[1][1])

    # use Regular Expression to remove the Chinese white space.
    r = re.compile(u'[\s\u3000]+')
    r = sc.broadcast(r)
    result1 = result.mapValues(lambda x: r.value.sub(' ', x[0])).map(lambda x: (x[0] + ',' + x[1]).encode('utf8'))
    result1.cache()
    # result.saveAsTextFile('/home/xsran/tmp/BigData/result1')
    keys = result.map(lambda x: x[0])
    keys.repartition(1).saveAsTextFile('/home/xsran/tmp/BigData/target_keys')

    print '************************'
    print 'input', input.count()
    print 'target', result1.count()


main()
