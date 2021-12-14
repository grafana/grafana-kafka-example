import os
from datetime import datetime
from time import strftime
import time
import random
import sys
import json
from confluent_kafka import Producer

config = { "count":    int(os.environ.get("KAFKA_PRODUCER_COUNT", 604800)),
           "interval": int( os.environ.get("KAFKA_PRODUCER_INTERVAL", 60)),
           "broker":   os.environ.get("KAFKA_BROKER", "kafka:9092"),
           "topic":    os.environ.get("KAFKA_TOPIC", "grafana"),
 }

dataWords = {
    "status": [ "running", "waiting", "stopped", "end" ],
    "statusCode": [ 100, 200, 300, 400, 500, 600 ],
    "processName": [ "ingester", "querier", "compactor", "distributor", "memcache", "gateway",
    "frontend"  ],
    "processName": [ "p1", "p2", "p3", "p4", "p5" ],
}

dataWords2 = {
    "status": [ "running", "waiting", "stopped", "end" ],
    "statusCode": [ 100, 200, 300, 400, 500, 600 ],
    "processName": [ "ingester", "querier", "compactor", "distributor", "memcache", "gateway",
    "frontend"  ],
    "processName": [ "p1", "p2", "p3", "p4", "p5" ],
    "location": [ { "latitude": 59.898300, "longitude": 30.261800, "city" :"St Petersburg", "city_geoname_id": 498817, "geoip_country_code": "LV"    },
                  { "latitude": 52.375900, "longitude": 4.897500, "city": "Amsterdam", "city_geoname_id": 2759794, "geoip_country_code": "NL"  },
                  { "latitude": 37.730900, "longitude": -122.388600, "city": "San Francisco","city_geoname_id": 5391959, "geoip_country_code": "US"    },
                  { "latitude": 39.043700, "longitude": -77.487500, "city": "Ashburn", "city_geoname_id": 4744870, "geoip_country_code": "US"    } ]
}

def createLogLine():
    logLine = {
        "status": random.choice(dataWords["status"]),
        "statusCode": random.choice(dataWords["statusCode"]),
        "processName": random.choice(dataWords["processName"]),
        "count": random.randint(1,100)
    }
    if "location" in dataWords.keys():
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
p1 = Producer(**kafkaConfig)
print( "Producer: ", kafkaConfig, config["broker"], config["topic"])

for i in range(0, config["count"]):
    logMsg = json.dumps(createLogLine())
    print( "{}: {}".format(i, logMsg) )
    try:
        p1.produce(config["topic"], logMsg, callback=deliveryCallback)
    except BufferError:
        sys.stderr.write("Kafka_producer: Queue Full: Topic: {} Messages: {}\n".format(config["topic"], len(p1)))
    p1.poll(0)
    time.sleep(config["interval"])
