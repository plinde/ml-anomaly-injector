#!/usr/bin/env python
import sys
import json
import datetime
from datetime import timedelta

from elasticsearch import Elasticsearch, helpers
MAX_BULKSIZE = 100000

def buildEvent(timestamp = None):

    event = {}

    #if we don't have a desired timestamp passed in for the event, use the current time in UTC
    if timestamp == None:
        event['timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        event['timestamp'] = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

    #TODO make some of these random inputs from seed lists
    
    #add these 2 for bulk API goodness
    event['_index'] = 'smoke_event'
    event['_type'] = 'smoke_event'
       
    event['request'] = '/index.html'
    event['response'] = '200'
    event['agent'] = 'Firefox'
    event['remote_ip'] = '1.1.1.1'
    event['remote_user'] = ''
    event['bytes'] = '1234'
    event['referrer'] = 'http://example.com'

    json_event = json.dumps(event)

    return json_event

def buildEventSeries(daysBack = 7, bulkSize = 1000):
    
    print "creating time series for previous %s days" % daysBack

    CURRENT_TIME = datetime.datetime.utcnow()
    print "End Time, aka CURRENT_TIME: %s %s" % (CURRENT_TIME, CURRENT_TIME.strftime('%Y-%m-%dT%H:%M:%SZ'))
    
    STEP_TIME = CURRENT_TIME - timedelta(days=daysBack)
    print "Start Time, aka STEP_TIME: %s %s" % (STEP_TIME, STEP_TIME.strftime('%Y-%m-%dT%H:%M:%SZ'))
    
    ### Set starting time (e.g. 7 days ago)
    STEP_TIME = CURRENT_TIME - timedelta(days=daysBack)

    # connection to elasticsearch
    es = Elasticsearch(host='localhost',http_auth=['elastic','changeme'])
    # create index, even if it exists already
    es.indices.create(index='smoke_event', ignore=400)
    print "elasticsearch bulk size is %i" % bulkSize
        
    while True:

        #batch bulkSize events, then bulk index into ES, then resume the loop
        i = 0
        bulk_list = []
        while i < bulkSize:
            i = i + 1
            # break when we reach the current time again
            if STEP_TIME == CURRENT_TIME:
                print('STEP_TIME : %s' % STEP_TIME)
                print('CURRENT_TIME : %s' % CURRENT_TIME)
                print "STEP_TIME == CURRENT_TIME, stopping event generation"
                return

            # step 5 seconds forward for each event
            STEP_TIME = STEP_TIME + timedelta(seconds=5)
            # print STEP_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

            json_event = buildEvent(STEP_TIME)
           
            bulk_list.append(json.loads(json_event))

            # decide which output to use
            # writeEventToLogstashHTTP(json_event)
            # writeEventToRedis(json_event)
            # writeEventToStdout(json_event)
      
        print "reached %s events, flushing to ElasticSearch" % bulkSize
        bulk_iter = iter(bulk_list)
        print(helpers.bulk(es,bulk_iter,stats_only=True))


def buildAnomalyEventSeries(daysBack = 7, anomalyPeriod = 30, anomalyMagnification = 10, bulkSize = 10000):

    # TODO refactor this into a callable function, rather than largely repeat the buildEvent function
    
    print "creating anomaly period with %s magnification for %i minutes within the previous %s days" % (anomalyMagnification, anomalyPeriod, daysBack)
    
    # connection to elasticsearch
    es = Elasticsearch(host='localhost',http_auth=['elastic','changeme'])
    
    print "Requested elasticsearch bulk size is %i" % bulkSize
    # number of events per flush magnified by the anomalyMagnification
    calculatedBulkSize = bulkSize * anomalyMagnification
    #print(calculatedBulkSize, bulkSize, anomalyMagnification)
    
    if calculatedBulkSize > MAX_BULKSIZE:

        print "calculatedBulkSize = bulkSize * anomalyMagnification | %i = %i * %i" % (calculatedBulkSize, bulkSize, anomalyMagnification)
        
        # reduce the bulkSize proportionally based on the bulkSize and anomalyMagnification
        newBulkSize = ((bulkSize / anomalyMagnification) / anomalyMagnification)
        print "newBulkSize = ((bulkSize / anomalyMagnification) / anomalyMagnification) | %i = %i * %i" % (newBulkSize, bulkSize, anomalyMagnification)
            
        print "adjusting bulkSize %i down to %i since calculatedBulkSize %i is greater than MAX_BULKSIZE %i" % (bulkSize, newBulkSize, calculatedBulkSize, MAX_BULKSIZE)

        bulkSize = newBulkSize
                
    else:
        print "going with requested bulkSize of %i" % bulkSize

    CURRENT_TIME = datetime.datetime.utcnow()
    # print "End Time, aka CURRENT_TIME: %s" % (CURRENT_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

    # e.g. 30 minute anomaly of high traffic somewhere within the relative time series

    anomaly_factor = daysBack * .3
    ANOMALY_START_TIME = CURRENT_TIME - timedelta(days=anomaly_factor)
    ANOMALY_END_TIME = ANOMALY_START_TIME + timedelta(minutes=anomalyPeriod)

    print "Anomaly Start Time %s" % ANOMALY_START_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')
    print "Anomaly End Time %s" %  ANOMALY_END_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

    ### Set starting time (e.g. 7 days ago)
    STEP_TIME = ANOMALY_START_TIME

    while True:
        
        #batch bulkSize events, then bulk index into ES, then resume the loop
        # TODO: fix bulkSize to adjust based on anomalyMagnification
        # e.g. always bulk 1000 at time, regardless of 10x anomaly (100*10 = 1000)
        # bulkSize * anomalyMagnification
        i = 0
        bulk_list = []
        #print(bulkSize * anomalyMagnification)
        while i < bulkSize:
            i = i + 1
            #print i

            # break when we reach the current time again
            if STEP_TIME == ANOMALY_END_TIME:
                print('STEP_TIME : %s' % STEP_TIME)
                print('ANOMALY_END_TIME : %s' % ANOMALY_END_TIME)
                print "STEP_TIME == ANOMALY_END_TIME, stopping event generation"

                # ugly math to get the remaining # ((i * 10) - 10))
                print('Flushing remaining %i events to ElasticSearch Bulk API' % len(bulk_list))
                bulk_iter = iter(bulk_list)
                print(helpers.bulk(es,bulk_iter,stats_only=True))
                
                return

            # step 5 seconds forward for each event
            STEP_TIME = STEP_TIME + timedelta(seconds=5)
            # print STEP_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')

            #generate %x more events than normal during the anomaly period, based on anomalyMagnification
            anomaly_i = 0
            while anomaly_i < anomalyMagnification:
                json_event = buildEvent(STEP_TIME)
                anomaly_i = anomaly_i + 1

                bulk_list.append(json.loads(json_event))

                # decide which output to use
                # writeEventToLogstashHTTP(json_event)
                # writeEventToRedis(json_event)
                # writeEventToStdout(json_event)

        print "reached %i events, flushing to ElasticSearch" % (len(bulk_list))
        bulk_iter = iter(bulk_list)
        print(helpers.bulk(es,bulk_iter,stats_only=True))

def writeEventToNull(json_event):
    print json_event


def main():

    bulkSize = 10000 # elasticsearch bulk size
    daysBack = 7
    
    anomalyPeriod = 30 # period for anomaly to last, in minutes
    anomalyMagnification = 10 # e.g. 10x more than the normal
   
    buildEventSeries(daysBack, bulkSize)
    buildAnomalyEventSeries(daysBack, anomalyPeriod, anomalyMagnification, bulkSize)

if __name__ == "__main__":
    main()
