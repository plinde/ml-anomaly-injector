The intention for this utility is to provide a 'training' dataset for Elastic's X-Pack Machine Learning product. This may be useful for learning the ML product by providing a simple dataset with 'known' anomaly in it.

The utility will generate a linear time-series set of 'HTTP access log' type events into Elasticsearch, along with a semi-randomized "anomaly" event period. In the initial version, this is a "10x" traffic spike.

~~NOTE: Redis and Logstash are used for some simplicity. Some may argue that requiring Redis/Logstash are actually reducing simplicity and adding complexity, but IMO these tools are already integral to working with the Elastic Stack and actually provide a comfortable abstraction. This code could easily be modified to write directly into ElasticSearch.~~

* In ```ml/jobs```, there are example ML jobs which can be imported with this dataset.

~~* In ```logstash/```, there are some Logstash configs which help with ingestion of the events.~~

#### Expectations
* Python 2.7+ 
* Elastic Stack 5.4+, running localhost:9200 () plinde/ml-anomaly-injector#3

* install python dependencies

```
pip install -r requirements.txt
```

* Run the utility
```
python generator.py
```

Output:
```
creating time series for previous 7 days
creating anomaly time series range within the previous 7 days
Anomaly Start Time 2017-03-01T18:31:23Z
Anomaly End Time 2017-03-01T19:01:23Z
```

Check your Kibana (localhost:5601) and define an index pattern for "smoke_event*", using `timestamp` as the timestamp field. You should see time-series data for the period requested (e.g. 7 days). You should also see a 'spike' up in the histogram. This is your anomaly.


![kibana](/wiki/kibana-1.png)


In ML (assuming you have this already going), you can start with a Single Metric job, select `smoke_event*` as your index pattern and you should see a histogram with an obvious anomaly/spike. 

If you're adventurous, you might look at defining your job via JSON from inside ```ml/jobs```. Since this is a fixed time-series with a definite endpoint, you can define the ML job to terminate (NOT real-time).

![ml-anomaly](/wiki/ml-anomaly-1.png)

![old-prelert](/wiki/prelert-1.png)
