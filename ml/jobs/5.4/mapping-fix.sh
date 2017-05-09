* Use via Kibana DevTools (http://localhost:5601/app/kibana#/dev_tools/console)


```
GET smoke_event-*/_mapping/smoke_event

PUT smoke_event-*/_mapping/smoke_event
{
  "properties": {
    "request": {
      "type": "text",
      "fielddata": true
    }
  }
}
```
