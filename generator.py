import sys
import json

import datetime
from datetime import timedelta

# Logstash HTTP output module
import ConfigParser
import requests

# redis output module
import redis

def buildEvent(timestamp = None):

    event = {}

    #if we don't have a desired timestamp passed in for the event, use the current time in UTC
    if timestamp == None:
        event['timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        event['timestamp'] = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

    #TODO make some of these random inputs from seed lists
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
    # print "End Time, aka CURRENT_TIME: %s" % (CURRENT_TIME)

    ### Set starting time (e.g. 7 days ago)
    STEP_TIME = CURRENT_TIME - timedelta(days=daysBack)
    # print "Start Time, aka STEP_TIME: %s" % (STEP_TIME)

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


def buildAnomalyEventSeries(daysBack = 1):
    # TODO refactor this into a callable function, rather than largely repeat the buildEvent function

    CURRENT_TIME = datetime.datetime.utcnow()
    # print "End Time, aka CURRENT_TIME: %s" % (CURRENT_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

    # e.g. 30 minute anomaly of high traffic somewhere within the relative time series

    anomaly_factor = daysBack * .3
    ANOMALY_START_TIME = CURRENT_TIME - timedelta(days=anomaly_factor)
    ANOMALY_END_TIME = ANOMALY_START_TIME + timedelta(minutes=30)

    print "Anomaly Start Time %s" % ANOMALY_START_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')
    print "Anomaly End Time %s" %  ANOMALY_END_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

    ### Set starting time (e.g. 7 days ago)
    STEP_TIME = ANOMALY_START_TIME

    while True:

        # print STEP_TIME
        # print ANOMALY_END_TIME

        # break when we reach the current time again
        if STEP_TIME == ANOMALY_END_TIME:
            # print "stop!"
            break

        # step 5 seconds forward for each event
        STEP_TIME = STEP_TIME + timedelta(seconds=5)
        # print STEP_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

        #generate 10x more events than normal during the anomaly period
        i = 0
        while i < 10:
            json_event = buildEvent(STEP_TIME)
            i = i + 1

            # decide which output to use
            # writeEventToLogstashHTTP(json_event)
            writeEventToRedis(json_event)
            # writeEventToRedisDebug(json_event)
            # writeEventToNull(json_event)

    return

def writeEventToNull(json_event):
    print json_event

def writeEventToRedisDebug(json_event):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.rpush("smoke_event_DEBUG", json_event)

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

    daysBack = 7
    print "creating time series for previous %s days" % daysBack
    buildEventSeries(daysBack)
    print "creating anomaly time series range within the previous %s days" % daysBack
    buildAnomalyEventSeries(daysBack)

if __name__ == "__main__":
    main()
