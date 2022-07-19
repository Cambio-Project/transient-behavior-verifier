import time
import requests
import json
from influxdb import InfluxDBClient
from datetime import datetime, timezone
import configparser

"""A script used to track the number of instances of a certain service
that are alive and registered in eureka"""


def get_instances():
    headers = {'content-type': 'application/json',
               "accept": "application/json"}

    config_obj = configparser.ConfigParser()
    config_obj.read("config.ini")
    eureka_address = config_obj["eureka"]['eureka_address']

    r = requests.get(
        eureka_address, headers=headers)
    resp = json.loads(json.dumps(r.json()))
    return len(resp['application']['instance'])


def write_in_influx(lastID, count, client):
    config_obj = configparser.ConfigParser()
    config_obj.read("config.ini")
    influxdb_host = config_obj["influxdb"]['influxdb_host']
    influxdb_port = config_obj["influxdb"]['influxdb_port']
    client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
    client.create_database('AliveInstances')
    client.switch_database('AliveInstances')

    json_body = [
        {
            "measurement": "InstanceCounts",
            "tags": {},
            "time": datetime.now(timezone.utc),
            "fields": {
                "RunID": lastID+1,
                "counts": count
            }
        }
    ]

    client.write_points(json_body)


config_obj = configparser.ConfigParser()
config_obj.read("config.ini")
influxdb_host = config_obj["influxdb"]['influxdb_host']
influxdb_port = config_obj["influxdb"]['influxdb_port']
client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
client.create_database('AliveInstances')
client.switch_database('AliveInstances')
result = client.query(
    'SELECT max("RunID") FROM "AliveInstances"."autogen"."InstanceCounts"')
if(len(result) == 0):
    lastID = 0
else:
    points = result.get_points()
    lastID = None
    print(points)
    for item in points:
        print(item)
        lastID = item['max']

nexttime = time.time()
counter = 0
starttime = time.time()

# configure experiment_length and warmup/sleep time
experiment_length = 140
sleep_time = 20
while counter <= experiment_length:
    if counter < sleep_time:
        print("sleep", counter)
        counter += 1
        nexttime += 1
        sleeptime = nexttime - time.time()
        if sleeptime > 0:
            time.sleep(sleeptime)
    else:
        instance_count = get_instances()
        print("adding", instance_count, "--", counter)
        write_in_influx(lastID, instance_count, client)
        counter += 1
        nexttime += 1
        sleeptime = nexttime - time.time()
        if sleeptime > 0:
            time.sleep(sleeptime)

print("end =", starttime-time.time())
