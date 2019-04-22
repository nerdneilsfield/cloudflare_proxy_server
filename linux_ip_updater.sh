#!/bin/bash

DDNS_SERVER="http://127.0.0.1:8888"
USERNAME="test"
PASSWORD="password"
SUBDOMAIN="test.org"

ipaddress=`ip addr | egrep '10\.19\.[[:digit:]]{1,3}\.[[:digit:]]{1,3}' | awk '{print $2}' | cut -d"/" -f 1`

if [[ $ipaddress ]];
then
    curl -u $USERNAME:$PASSWORD -X POST -d "subdomain=${SUBDOMAIN}&type=A&content=${ipaddress}" ${DDNS_SERVER}/ddns/${SUBDOMAIN}
fi