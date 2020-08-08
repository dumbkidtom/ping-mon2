import os
import sys
import time
import configparser
import subprocess
import argparse
import logging as log
from datetime import datetime
from threading import Thread
from influxdb import InfluxDBClient


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

    # compose json
    json_body = {
               "measurement": "pingEvents",
               "tags": {
                   "ip": ip,
                   "host": hostname
                },
               "time": current_time,
               "fields": {
                   "rtt": float(rtt)
                }
               }

    return json_body


def loopthread(ip):

    # frequency external command
    frequency = int(config[ip]['frequency'])
    if not frequency:
        frequency = int(config['DEFAULT']['frequency'])

    # loop until cancel
    try:

     while True:
        r=[]
        loopcount=int(60/frequency)+1

        # collect more stats if frequency is less than 60 seconds
        for i in range(loopcount):
            log.debug("pinging (%s) ...",ip)
            r.append(ping(ip))

            # sleep for x second
            log.debug("sleeping for %s seconds ...",frequency)
            time.sleep(frequency)

        # save to influxdb
        log.debug("writing to influxdb...")
        client.write_points(r)


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
    global hostname

    # read config
    config = configparser.ConfigParser()
    config.read('/home/dumbkid/projects/myping/ping-mon2.conf')
    db_host = config['DEFAULT']['influxdb_host']
    db_name = config['DEFAULT']['influxdb_database']
    db_port = config['DEFAULT']['influxdb_port']
    hostname = os.uname()[1]

    # connect to local influxdb
    client = InfluxDBClient(host=db_host, port=db_port)
    client.switch_database(db_name)
    log.info("connected to influxdb: %s:%s (%s)",db_host, db_port, db_name)

    threads = []

    # start thread for each target
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

    # start thread for each target
    for thread in threads:
        try:
            log.info(" Join thread: %s",thread)
            thread.join()
        except:
            log.error("Error: join thread failed for %s (%s)",target,sys.exc_info())
            sys.exit()


if __name__ == "__main__":
    main()
