The intention for this utility is to provide a 'training' dataset for Elastic's Prelert product. This may be useful for learning the Prelert product by providing a simple dataset with 'known' anomaly in it.

The utility will generate a linear time-series set of 'HTTP access log' type events into Elasticsearch, along with a semi-randomized "anomaly" event period. In the initial version, this is a "10x" traffic spike.

NOTE: Redis and Logstash are used for some simplicity. Some may argue that requiring Redis/Logstash are actually reducing simplicity and adding complexity, but IMO these tools are already integral to working with the Elastic Stack and actually provide a comfortable abstraction. This code could easily be modified to write directly into ElasticSearch.

* In ```prelert/jobs```, there are example Prelert jobs which can be imported with this dataset.

* In ```logstash/```, there are some Logstash configs which help with ingestion of the events.

#### Expectations
* Python 2.7 (not tested on Python 3, yet)
* Elastic Stack 5.2+
* Redis 3.0+

#### One possible usage
1. Redis running with defaults (port 6379, localhost). I used 3.2.6 but any 3.x+ version should work fine.
```~/workspace/redis-3.2.6/src/redis-server```

2. ElasticSearch running with defaults (HTTP 9200, localhost). I used ElasticSearch 5.2.2 but this should work with any version 1.x+.
```~/workspace/elastic-5.2.2/elasticsearch-5.2.2/bin/elasticsearch```

3. Start logstash using the 'redis-to-es.yml' to pump events from Redis into ElasticSearch. I used Logstash 5.2.2 but again, any version 2.x+ should work fine.
```~/workspace/elastic-5.2.2/logstash-5.2.2/bin/logstash -f ./redis-to-es.yml```

4. ```pip install -r requirements.txt```

5. ```python generator.py```

Output:
```
creating time series for previous 7 days
creating anomaly time series range within the previous 7 days
Anomaly Start Time 2017-03-01T18:31:23Z
Anomaly End Time 2017-03-01T19:01:23Z
```

Check your Kibana (localhost:5601) and define an index pattern for "smoke_event-*", using @timestamp as the timestamp field. You should see time-series data for the period requested (e.g. 7 days). You should also see a 'spike' up in the histogram. This is your anomaly.

In Prelert (assuming you have this already going), you can upload the job definition inside ```prelert/jobs```. You may need to tune the ElasticSearch version if you are not using 2.x/5.x. Since this is a fixed time-series with a definite endpoint, you can define the Prelert job to terminate (NOT real-time).
