#!/bin/bash

if [ $1 = "update" ]; then
    docker compose -f docker-compose-server-update.yml up -d
    echo "docker-compose-server-update.yml" > status.txt
fi
if [ $1 = "first" ]; then
    docker compose -f docker-compose-server-first.yml up -d
    echo "docker-compose-server-first.yml" > status.txt
fi
if [ $1 = "local" ]; then
    docker compose -f docker-compose-server-local.yml up -d
    echo "docker-compose-server-local.yml" > status.txt
fi
if [ $1 = "down" ]; then
    conf=$(cat status.txt)
    docker compose -f $conf down
fi