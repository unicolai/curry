#!/bin/sh

echo "Removing all containers"

docker rm `docker ps -aq`

