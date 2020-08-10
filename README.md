# ping-mon2

Mini monitoring script to save the monitoring statistics in Influxdb database and graph with Grafana.

## Requirement

- InfluxDB (or InfluxCloud)
- Grafana
- Python3

## InfluxDB

Installation of influxdb depends on distributions.  Here are what needs to be done after database installation.

```
~$ influx
Visit https://enterprise.influxdata.com to register for updates, InfluxDB server management, and monitoring.
Connected to http://localhost:8086 version 1.1.1
InfluxDB shell version: 1.1.1
> create database pingdb
> show databases
name: databases
name
----
_internal
pingdb

> quit
```

## Running the script

```
~/projects/ping-mon2$ python3 ./ping-mon2.py &
[1] 26316
~/projects/ping-mon2$ INFO:root:connected to influxdb: localhost:8086 (pingdb)
INFO:root:Create thread: 75.75.75.75
INFO:root:Create thread: 1.1.1.1
INFO:root:Create thread: 8.8.8.8
INFO:root:Create thread: 9.9.9.9
INFO:root:Create thread: www.google.com
INFO:root: Start thread: <Thread(Thread-1, initial)>
INFO:root: Start thread: <Thread(Thread-2, initial)>
INFO:root: Start thread: <Thread(Thread-3, initial)>
INFO:root: Start thread: <Thread(Thread-4, initial)>
INFO:root: Start thread: <Thread(Thread-5, initial)>
INFO:root: Join thread: <Thread(Thread-1, started 140431636072192)>
```
