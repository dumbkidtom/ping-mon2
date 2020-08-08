import sys
import time
import configparser
import subprocess
from datetime import datetime
from influxdb import InfluxDBClient

def ping(ip):

    # ping host
    resp = subprocess.run([PING_CMD, ip], capture_output=True)
    rtt=resp.stdout.decode("utf-8").rstrip()

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
                   "host": "mymini"
                },
               "time": current_time,
               "fields": {
                   "rtt": float(rtt)
                }
               }

    return json_body


def main():

    global PING_CMD

    # read config
    config = configparser.ConfigParser()
    config.read('/home/dumbkid/projects/myping/ping-mon.conf')
    PING_CMD = config['DEFAULT']['external_cmd']
    sleep_count = int(config['DEFAULT']['frequency'])

    # connect to local influxdb
    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database('pingdb')

    # loop until cancel
    try:
    
     while True:
        r=[]

        for target in config['options']['targets'].splitlines():
            print("pinging ...",target)
            r.append(ping(target))

        # save to influxdb
        client.write_points(r)

        # sleep for x second
        print("sleeping for ",sleep_count," seconds ...")
        time.sleep(sleep_count)

    except:
     print("Oops!", sys.exc_info()[0], "occurred.")
     exit


if __name__ == "__main__":
    main()
