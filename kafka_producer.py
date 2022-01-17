import os
from datetime import datetime
from time import strftime
import time
import random
import sys
import json
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions


config = { "count":    int(os.environ.get("KAFKA_PRODUCER_COUNT", 604800)),
           "interval": int(os.environ.get("KAFKA_PRODUCER_INTERVAL", 60)),
           "broker":   os.environ.get("KAFKA_BROKER", "kafka:9092"),
           "topic":    os.environ.get("KAFKA_TOPIC", "grafana"),
           "partitions": int(os.environ.get("KAFKA_PARTITIONS", 4)),
 }

dataWords = {
    "status": [ "running", "waiting", "stopped", "end" ],
    "statusCode": [ 100, 200, 300, 400, 500, 600 ],
    "processName": [ "ingester", "querier", "compactor", "distributor", "memcache", "gateway",
    "frontend"  ],
    "processName": [ "p1", "p2", "p3", "p4", "p5" ],
}

def createLogLine(id=0, partition=0):
    logLine = {
        "status": random.choice(dataWords["status"]),
        "statusCode": random.choice(dataWords["statusCode"]),
        "processName": random.choice(dataWords["processName"]),
        "count": random.randint(1,100),
        "id": id,
        "partition": partition
    }
    if "xxxxlocation" in dataWords.keys():
        loc = random.choice(dataWords["location"])
        logLine.update( { "latitude": loc["latitude"], "longitude": loc["longitude"],
        "city": loc["city"],
        "city_geoname_id": loc["city_geoname_id"],
        "geoip_country_code": loc["geoip_country_code"] } )
    return logLine

def deliveryCallback(err, msg):
    if err:
        sys.stderr.write("Kafka_producer: Delivery Failure: {}\n".format(err))
    else:
        sys.stderr.write("Kafka_producer: Deliverd Topic: {} Partiton: {} Offset: {}\n".format(
                          msg.topic(), msg.partition(), msg.offset()))

kafkaConfig = {'bootstrap.servers': config["broker"]}

def listTopics():
    ac = AdminClient(kafkaConfig)
    topicList = ac.list_topics()
    sys.stderr.write("List Topics: brokers: {} topics: {}\n".format(topicList.brokers, topicList.topics))

def createKafkaTopicsWORKS():
    try:
        # Create topics
        topic = config["topic"]
        numPartitions = config["partitions"]
        ac = AdminClient(kafkaConfig)
        sys.stderr.write( "Topics: {}\n".format(ac.list_topics( )) )
        topicList = []
        topicList.append( NewTopic(topic=topic, num_partitions=numPartitions, replication_factor=1) )
        ac.create_topics(topicList )
        #sys.stderr.write("Created Topics: {} Partitions: {}\n".format(topic, numPartitions))
        sys.stderr.write("Created Topics: {} Partitions: {} kconfig {}\n".format(topic, numPartitions, kafkaConfig))
    except Exception as e:
        sys.stderr.write( "Exception: Create topics {}\n".format(e))
    listTopics()

def createKafkaTopics():
    try:
        topic = config["topic"]
        numPartitions = config["partitions"]
        # Create topics
        ac = AdminClient(kafkaConfig)
        sys.stderr.write("Creating Topics: {} \n".format( ac.list_topics( ) ))
        topicList = []
        topicList.append( NewTopic(topic=topic, num_partitions=numPartitions, replication_factor=1) )
        ac.create_topics(topicList )
        sys.stderr.write("Created Topics: {} Partitions: {} kconfig {}\n".format(topic, numPartitions, kafkaConfig))
    except Exception as e:
        sys.stderr.write( "Exception: Create topics {}\n".format(e))
    listTopics()

#np = NewPartitions(topic="grafana", new_total_count=2)
#ac.create_partitions(np)

createKafkaTopicsWORKS()
#createKafkaTopics()

p1 = Producer(**kafkaConfig)
sys.stderr.write( "PRODUCER: kconfig: {} config: {} topic: {}\n".format(kafkaConfig, config["broker"], config["topic"]))

partitionN = 0
for i in range(0, config["count"]):
    #partition = random.randrange(0, config["partitions"])
    logMsg = json.dumps(createLogLine(id=i, partition=partitionN))
    listTopics()
    sys.stderr.write( "PRODUCING: n: {}: msg: {} Partition: {}\n".format(i, logMsg, partitionN) )
    try:
        p1.produce(topic=config["topic"],
            value=logMsg,
            partition=partitionN,
            callback=deliveryCallback)
    except Exception as e:
        sys.stderr.write("Kafka_producer: Exception {}".format(e))
        #sys.stderr.write("Kafka_producer: Queue Full: Topic: {} Messages: {}\n".format(config["topic"], len(p1)))
    p1.poll(0)
    partitionN = (partitionN + 1) % config["partitions"]
    time.sleep(config["interval"])
