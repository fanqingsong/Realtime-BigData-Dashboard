from kafka import KafkaProducer
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkConf, SparkContext
import json
import sys
import nltk
from nltk import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from stop_words import get_stop_words

#nltk.download('punkt')


def createSparkContext():
    spark_conf = SparkConf().setAppName("KafkaWordCount")
    sc = SparkContext(conf=spark_conf)
    sc.setLogLevel("ERROR")

    return sc

def createStreamingContext(sc):
    ssc = StreamingContext(sc, 5)
    #ssc.checkpoint("file:///usr/local/spark/checkpoint")
    # 这里表示把检查点文件写入分布式文件系统HDFS，所以要启动Hadoop
    ssc.checkpoint("_checkpoint")

    return ssc

def createKafkaStream(ssc, zkQuorum, group, topics, numThreads):
    topicAry = topics.split(",")
    # 将topic转换为hashmap形式，而python中字典就是一种hashmap
    topicMap = {}
    for topic in topicAry:
        topicMap[topic] = numThreads
    lines = KafkaUtils.createStream(ssc, zkQuorum, group, topicMap).map(lambda x: x[1])

    return lines

def updateFunc(new_values, last_sum):
    return sum(new_values) + (last_sum or 0)

def preprocessing(text):
    # tokenize into words
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]

    # remove stopwords
    stop = stopwords.words('english')
    tokens = [token for token in tokens if token not in stop]

    # remove words less than three letters
    tokens = [word for word in tokens if len(word) >= 3]

    # lower capitalization
    tokens = [word.lower() for word in tokens]

    # lemmatize
    lmtzr = WordNetLemmatizer()
    tokens = [lmtzr.lemmatize(word) for word in tokens]
    preprocessed_text= ' '.join(tokens)

    return preprocessed_text

def getStatDSFromKafkaStream(sc, lines):
    # RDD with initial state (key, value) pairs
    initialStateRDD = sc.parallelize([(u'hello', 1), (u'world', 1)])
 
    words = lines.\
            flatMap(word_tokenize)

    statDS = words.\
                map(lambda x: (x, 1)).\
                updateStateByKey(updateFunc, initialRDD=initialStateRDD)

    return statDS

def setStopWordFilterOnStatDS(statDS):
    stop_words = get_stop_words('en')
    print("--------- stop word ---------")
    print(stop_words)

    statDS = statDS.\
                filter(lambda x: x[1]>=5).\
                filter(lambda x: x[0] not in stop_words)

    return statDS

def createStatDSOnKafkaStream(sc, lines):
    statDS = getStatDSFromKafkaStream(sc, lines)

    statDS = setStopWordFilterOnStatDS(statDS)

    return statDS

# 格式转化，将[["1", 3], ["0", 4], ["2", 3]]变为[{'1': 3}, {'0': 4}, {'2': 3}]，这样就不用修改第四个教程的代码了
def Get_dic(rdd_list):
    res = []
    for elm in rdd_list:
        tmp = {elm[0]: elm[1]}
        res.append(tmp)
    return json.dumps(res)

def sendmsg(rdd):
    if rdd.count != 0:
        msg = Get_dic(rdd.collect())
        producer = KafkaProducer(bootstrap_servers='localhost:9092')
        # 实例化一个KafkaProducer示例，用于向Kafka投递消息
        producer.send("wordStats", msg.encode('utf8'))
        # 很重要，不然不会更新
        producer.flush()

def setSenderOnStatDS(statDS):
    statDS.foreachRDD(lambda x: sendmsg(x))

    statDS.pprint()

def KafkaWordCount(zkQuorum, group, topics, numThreads):
    sc = createSparkContext()
    ssc = createStreamingContext(sc)

    lines = createKafkaStream(ssc, zkQuorum, group, topics, numThreads)

    statDS = createStatDSOnKafkaStream(sc, lines)

    setSenderOnStatDS(statDS)

    ssc.start()
    ssc.awaitTermination()



if __name__ == '__main__':
    # 输入的四个参数分别代表着
    # 1.zkQuorum为zookeeper地址
    # 2.group为消费者所在的组
    # 3.topics该消费者所消费的topics
    # 4.numThreads开启消费topic线程的个数
    if (len(sys.argv) < 5):
        print("Usage: KafkaWordCount <zkQuorum> <group> <topics> <numThreads>")
        exit(1)

    zkQuorum = sys.argv[1]
    group = sys.argv[2]
    topics = sys.argv[3]
    numThreads = int(sys.argv[4])
    print(group, topics)
    KafkaWordCount(zkQuorum, group, topics, numThreads)
