import os
import sys
import time
import configparser
import subprocess
import argparse
import logging as log
from datetime import datetime
from threading import Thread
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

def ping(ip):

    # ping external command
    ping_cmd = config[ip]['external_cmd']
    if not ping_cmd:
        ping_cmd = config['DEFAULT']['external_cmd']

    log.debug("external_cmd: %s",ping_cmd)

    try:

        # ping host
        resp = subprocess.run([ping_cmd, ip], capture_output=True)
        rtt = resp.stdout.decode("utf-8").rstrip()

    except:
        log.error("ping(): %s (%s)", ip, sys.exc_info())
        exit


    # timeout value of RTT
    if not rtt:
        rtt=-10

    # current date
    current_time = datetime.utcnow()

    # compose point
    point = Point('pingEvents').tag('host', hostname).tag('ip', ip).field('rtt', float(rtt)).time(time=datetime.utcnow())

    return point


def loopthread(ip):

    # frequency external command
    frequency = int(config[ip]['frequency'])
    if not frequency:
        frequency = int(config['DEFAULT']['frequency'])

    # loop until cancel
    try:

     while True:
        # collect more stats if frequency is less than 60 seconds
        log.debug("pinging (%s) ...",ip)
        point = ping(ip)

        # sleep for x second
        log.debug("sleeping for %s seconds ...",frequency)
        time.sleep(frequency)

        # save to influxdb
        log.debug("writing to influxdb: %s",point.to_line_protocol())
        write_api.write(bucket=bucket, org=org, record=point)


    except:
        log.error("loopthread(): %s (%s)", ip, sys.exc_info())
        exit



def main():

    # log options
    parser = argparse.ArgumentParser()

    parser.add_argument(
            "-v", "--verbose", 
            help="display debug output",
            action="store_const", dest="loglevel", const=log.DEBUG,
            default=log.INFO,
    )

    args = parser.parse_args()
    log.basicConfig(level=args.loglevel)

    # global variables used by functions
    global config
    global client
    global write_api
    global bucket
    global org
    global hostname

    # read config
    config = configparser.ConfigParser()
    config.read('/home/dumbkid/projects/ping-mon2/ping-mon2.conf')
    hostname = os.uname()[1]

    #Configure credentials
    influx_cloud_url = os.getenv('INFLUXDB_URL')
    influx_cloud_token = os.getenv('INFLUXDB_TOKEN')
    bucket = os.getenv('INFLUXDB_BUCKET')
    org = os.getenv('INFLUXDB_ORG')

    try:

        # connect to local influxdb
        client = InfluxDBClient(url=influx_cloud_url, token=influx_cloud_token)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        log.info("connected to influxdb: %s:%s (%s)",influx_cloud_url, bucket, org)

        threads = []

        # create thread for each target
        for target in config.sections():
            try:
                log.info("Create thread: %s",target)
                thread = Thread(target=loopthread, args=(target,))
                threads.append(thread)
            except:
                log.error("Error: create thread failed for %s (%s)",target,sys.exc_info())
                sys.exit()

        # start thread for each target
        for thread in threads:
            try:
                log.info(" Start thread: %s",thread)
                thread.start()
            except:
                log.error("Error: start thread failed for %s (%s)",target,sys.exc_info())
                sys.exit()

        # wait for each thread to exit
        for thread in threads:
            try:
                log.info(" Join thread: %s",thread)
                thread.join()
            except:
                log.error("Error: join thread failed for %s (%s)",target,sys.exc_info())
                sys.exit()

    except:
        log.error("main: (%s)",sys.exc_info())
    finally:
        client.close()


if __name__ == "__main__":
    main()
