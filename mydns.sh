#!/bin/sh

DNSSERVER=$1

R1=`dig +noall +stats @${DNSSERVER} google.com | awk '/Query time/ {print $4}'`
R2=`dig +noall +stats @${DNSSERVER} netflix.com | awk '/Query time/ {print $4}'`
R3=`dig +noall +stats @${DNSSERVER} amazon.com | awk '/Query time/ {print $4}'`
R4=`dig +noall +stats @${DNSSERVER} apple.com | awk '/Query time/ {print $4}'`
R5=`dig +noall +stats @${DNSSERVER} facebook.com | awk '/Query time/ {print $4}'`

echo "scale=2; ($R1 + $R2 + $R3 + $R4 + $R5)/5" | bc
