#!/bin/sh

# INPUT: website name (e.g. www.google.)
# OUTPUT:  single floating round trip time number in milliseconds

T=`curl -k -o /dev/null -s -m 10 -w "%{time_total}" "https://$@"`
echo "$T * 1000" | bc
