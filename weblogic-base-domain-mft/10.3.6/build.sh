#!/bin/sh

cp ../../../configure-jms.py .

docker build -t skat/weblogic-base-domain-mft-jdk7u79:10.3.6 .

rm configure-jms.py
