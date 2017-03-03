import json
from pprint import pprint
import sys

import datetime
from datetime import timedelta

import ConfigParser
import requests

import time

import redis

# cluster_host = sys.argv[1]
# cluster_port = sys.argv[2]
# json_loads_1 = sys.argv[3]
# json_loads_2 = sys.argv[4]

def buildEvent(timestamp = None):

    event = {}

    #if we don't have a desired timestamp for the event, use the current time in UTC
    if timestamp == None:
        event['timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        event['timestamp'] = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

    #make some of these random inputs from seed lists
    event['request'] = '/index.html'
    event['response'] = '200'
    event['agent'] = 'Firefox'
    event['remote_ip'] = '1.1.1.1'
    event['remote_user'] = ''
    event['bytes'] = '1234'
    event['referrer'] = 'http://example.com'

    json_event = json.dumps(event)

    return json_event

def buildEventSeries(daysBack = 1):

    CURRENT_TIME = datetime.datetime.utcnow()
    print "End Time, aka CURRENT_TIME: %s" % (CURRENT_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

    ### Set starting time (e.g. 7 days ago)
    STEP_TIME = CURRENT_TIME - timedelta(days=daysBack)
    print "Start Time, aka STEP_TIME: %s" % (STEP_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')
    # print STEP_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

    while True:

        # break when we reach the current time again
        if STEP_TIME == CURRENT_TIME:
            print "stop!"
            break

        # step 5 seconds forward for each event
        STEP_TIME = STEP_TIME + timedelta(seconds=5)
        # print STEP_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

        json_event = buildEvent(STEP_TIME)

        # decide which output to use
        # writeEventToLogstashHTTP(json_event)
        writeEventToRedis(json_event)
        # writeEventToNull(json_event)

    return

def writeEventToNull(json_event):
    print json_event

def writeEventToRedis(json_event):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.rpush("smoke_event", json_event)


def writeEventToLogstashHTTP(json_event):
    Config = ConfigParser.ConfigParser()
    Config.read("json-compare-engine.props")
    http_proto = Config.get('HTTPOutput', 'proto')
    http_host = Config.get('HTTPOutput', 'host')
    http_port = Config.get('HTTPOutput', 'port')

    r = requests.post(http_proto + '://' + http_host + ':' + http_port, data=json_event)
    # print r.content

def main():

    #daysBack = 1
    daysBack = 14
    buildEventSeries(daysBack)



    # while True:
    #     json_event = buildEvent()
    #     print json_event
    #     writeEventToLogstashHTTP(json_event)



if __name__ == "__main__":
    main()
