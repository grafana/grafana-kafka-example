import os
from datetime import datetime, timedelta
from time import strftime
import time
import random
import sys
import json
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions
from concurrent.futures import ThreadPoolExecutor
import sched

messageId = 0

config = { "count": int(os.environ.get("KAFKA_PRODUCER_COUNT", 604800)),
           "interval": int(os.environ.get("KAFKA_PRODUCER_INTERVAL", 60)),
           "broker": os.environ.get("KAFKA_BROKER", "kafka:9092"),
           "topic": os.environ.get("KAFKA_TOPIC", "grafana"),
           "partitions": int(os.environ.get("KAFKA_PARTITIONS", 4)),
           "dataDirListOfStates": os.environ.get("KAFKA_DATA_DIR_STATES", "kafka/worldmap-panel/src/data/states.json"),
           "startDelaySec": 30
 }

kafkaConfig = {"bootstrap.servers": config["broker"]}

def createSyntheticData():
    return {
        "status": [ "running", "pending", "succeded", "unknown" ],
        "statusCode": [ 100, 200, 300, 400, 500, 600 ],
        "processName": [ "ingester", "querier", "compactor", "distributor", "memcache", "gateway", "frontend" ],
        "processName": [ "p1", "p2", "p3", "p4", "p5" ],
        "location": { "states": listOfStates } }

def readJsonFile(fileName):
    j = []
    try:
        j = json.load(open(fileName, "rb"))
    except Exception as e:
        sys.stderr.write("readJsonFile: failed: file: {} {}\n".format(fileName, e))
    return j

def createLogLine(id=0, partition=0):
    return {
        "status": random.choice(dataWords["status"]),
        "statusCode": random.choice(dataWords["statusCode"]),
        "processName": random.choice(dataWords["processName"]),
        "count": random.randint(1,100),
        "state": random.choice(dataWords["location"]["states"])["name"],
        "id": id,
        "partition": partition,
    }

def deliveryCallback(err, msg):
    if err:
        sys.stderr.write("Kafka_producer: Delivery Failure: {}\n".format(err))
    else:
        sys.stderr.write("Kafka_producer: Deliverd Topic: {} Partiton: {} Offset: {}\n".format(
                          msg.topic(), msg.partition(), msg.offset()))

def createKafkaTopicsORIG():
    topic = config["topic"]
    numPartitions = config["partitions"]
    try:
        # Create topics
        ac = AdminClient(kafkaConfig)
        sys.stderr.write("Creating Topics: {} \n".format(ac.list_topics(())))
        topicList = []
        topicList.append(NewTopic(topic=topic, num_partitions=numPartitions, replication_factor=1))
        ac.create_topics(topicList)
        sys.stderr.write("Created Topics: {} Partitions: {} kconfig {}\n".format(topic, numPartitions, kafkaConfig))
    except Exception as e:
        sys.stderr.write("Exception: Create topics {}\n".format(e))
        # if topics fail to create then
    #np = NewPartitions(topic="grafana", new_total_count=2)
    #ac.create_partitions(np)

def listTopics():
    ac = AdminClient(kafkaConfig)
    topicList = ac.list_topics()
    sys.stderr.write("List Topics: brokers: {} topics: {}\n".format(topicList.brokers, topicList.topics))

def createKafkaTopics():
    try:
        # Create topics
        topic = config["topic"]
        numPartitions = config["partitions"]
        sys.stderr.write("Create Topics: Connecting AdminClient\n")
        ac = AdminClient(kafkaConfig)
        sys.stderr.write("Create Topics: Connected\n")
        #sys.stderr.write("Topics: {}\n".format(ac.list_topics()))
        topicList = []
        topicList.append(NewTopic(topic=topic, num_partitions=numPartitions, replication_factor=1))
        sys.stderr.write("Create Topics: Creating\n")
        ac.create_topics(new_topics=topicList, validate_only=False, request_timeout=60, operation_timeout=30)
        sys.stderr.write("Created Topics: {} Partitions: {} kconfig {}\n".format(topic, numPartitions, kafkaConfig))
        tl1 = ac.list_topics()
        sys.stderr.write("Create Topics: brokers: {} topics: {}\n".format(tl1.brokers, tl1.topics))
    except TopicExistsException:
        sys.stderr.write("Create Topics: Exists Already: Ok\n")
    except Exception as e:
        sys.stderr.write("Create Topics: Exception: Exit {}\n".format(e))
        exit()
    #listTopics()
    #validateTopicPartitions()

def getPartitions():
    partitions = {}
    ac = AdminClient(kafkaConfig)
    topicList = ac.list_topics()
    if config["topic"] in topicList.topics.keys():
        partitions = topicList.topics[ config["topic"] ].partitions
    return partitions

def validateTopicPartitions():
    sys.stderr.write("Validate Topics: Connecting AdminClient\n")
    ac = AdminClient(kafkaConfig)
    sys.stderr.write("Validate Topics: Connected\n")
    for i in range(0, 1):
        #topicList = ac.list_topics()
        #sys.stderr.write("validateTopicPartitions: brokers: {} topics: {}\n".format(topicList.brokers, topicList.topics))
        #if config["topic"] in topicList.topics.keys():
        #    partitions = topicList.topics[ config["topic"] ].partitions
        partitions = getPartitions()
        sys.stderr.write("validateTopicPartitions: partitions: {} n: {}\n".format(partitions, len(partitions.keys())))
        if len(partitions.keys()) == config["partitions"]:
            sys.stderr.write("validateTopicPartitions: valid partitions: {}\n".format(partitions))
            break
        else:
            sys.stderr.write("validateTopicPartitions: waiting on partitions count: {}\n".format(partitions))
        #else:
        #    sys.stderr.write("validateTopicPartitions: waiting on partitions creation: {}\n".format(topicList.topics))
        time.sleep(1)

def producerSerial():
    p1 = Producer(**kafkaConfig)
    sys.stderr.write("Producer: kcofig: {} config: {} topic: {}\n".format( kafkaConfig, config["broker"], config["topic"]))

    partitionN = 0
    for i in range(0, config["count"]):
        #partition = random.randrange(0, config["partitions"])
        logMsg = json.dumps(createLogLine(id=i, partition=partitionN))
        listTopics()
        sys.stderr.write("Producing: i: {}: msg: {} partition: {}\n".format(i, logMsg, partitionN))
        try:
            p1.produce(topic=config["topic"],
                value=logMsg,
                partition=partitionN,
                callback=deliveryCallback)
        except BufferError: # Otherwise fail
            sys.stderr.write("Producer: Queue Full: Topic: {} Messages: {}\n".format(config["topic"], len(p1)))
        except Exception as e:
            sys.stderr.write("Producer: Exit: Exception: {} \n".format(e))
            #exit()

        p1.poll(0)
        partitionN = (partitionN + 1) % config["partitions"]
        time.sleep(config["interval"])

def producerSingle(kp, partitionN, id):
    logMsg = json.dumps(createLogLine(id=id, partition=partitionN))
    sys.stderr.write("Producing: id: {}: msg: {} partition: {}\n".format(id, logMsg, partitionN))
    try:
        kp.produce(topic=config["topic"], value=logMsg, partition=partitionN, callback=deliveryCallback)
    except BufferError: # Otherwise fail
        sys.stderr.write("producer: Queue Full: Topic: {} Messages: {}\n".format(config["topic"], len(kp)))
    except Exception as e:
        sys.stderr.write("producer: Exit: Exception: {} \n".format(e))
        #exit()
    kp.poll(0)

def scheduleProducer(kp, partitions, id):
    r = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for partitionN in partitions.keys():
            r.append(executor.submit(producerSingle, kp=kp, partitionN=partitionN, id=id, ) )
            id += 1
        sys.stderr.write("ThreadPoolExecutor: Waiting\n")
    sys.stderr.write("ThreadPoolExecutor: Result: {}\n".format(r))

def producerThreaded():
    kp = Producer(**kafkaConfig)
    s = sched.scheduler(time.time, time.sleep)
    id = 0;
    while (True):
        partitions = getPartitions() #partitions = { i: i for i in range(0,4) }
        if len(partitions) > 0:
            s.enter(delay=15, priority=1, action=scheduleProducer, argument=(kp, partitions, id,))
            s.run(blocking=True)
            id += len(partitions)
        else:
            sys.stderr.write("producerThreaded: No Partitions {}: Exiting\n".format(len(partitions)))
            time.sleep(15)
            break

cmd = sys.argv[1] if len(sys.argv) > 1 else "unknown command"
if cmd == "readStates":
    print(config)
    listOfStates = readJsonFile(config["dataDirListOfStates"])
    print(listOfStates)
    dataWords = createSyntheticData()
    sys.stderr.write("Synthetic {}".format(dataWords))

elif cmd == "createTopics":
    timeoutSec = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    timeoutTime = datetime.now() + timedelta(seconds=timeoutSec)
    while datetime.now() < timeoutTime:
        createKafkaTopics()
        #validateTopicPartitions()
        time.sleep(15)
    sys.stderr.write("createTopics: Ending {}\n".format(timeoutSec))

elif cmd == "producerSerial":
    sys.stderr.write("Producer waiting to start: delay: {}\n".format(config["startDelaySec"]))
    #time.sleep(config["startDelaySec"]) # delay start up
    listOfStates = readJsonFile(config["dataDirListOfStates"])
    dataWords = createSyntheticData()
    createKafkaTopics()
    validateTopicPartitions()
    listTopics()
    producerSerial()

elif cmd == "producerThreaded":
    listOfStates = readJsonFile(config["dataDirListOfStates"])
    dataWords = createSyntheticData()
    #createKafkaTopics()
    #validateTopicPartitions()
    producerThreaded()

elif cmd == "testProducer":
    listOfStates = readJsonFile(config["dataDirListOfStates"])
    dataWords = createSyntheticData()
    print( createLogLine(id=0, partition=0) )
    producerThreaded()

else:
    sys.stderr.write("Unknown Commands: [{}]\n".format(cmd))
