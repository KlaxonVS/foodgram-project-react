#!/bin/bash
conf=$(cat status.txt)
docker compose -f $conf exec backend $1