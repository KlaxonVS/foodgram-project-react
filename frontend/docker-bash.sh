#!/bin/bash

ver=$(cat docker_ver.txt)
ver=$(echo "$ver + 0.01" | bc)
echo $ver > docker_ver.txt

docker build -t vorvorsky/foodgram_frontend:v${ver} .