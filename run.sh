#!/bin/sh

cd "$(dirname "$0")"
exec docker run --rm \
  -v "$PWD/data.txt":/srv/data.txt:ro \
  -v "$PWD/last.html":/srv/last.html:rw \
  --network ustcnet \
  --ip 127.0.114.514 \
  --dns 202.38.64.1 \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  checkin:latest
