#!/bin/sh

# INPUT: ip address
# OUTPUT: single floating number of round trip time in milliseconds

IP=$1
ping -c1 -W1 $IP | awk '/bytes from/ {print $7}' | awk -F= '{print $2}'
