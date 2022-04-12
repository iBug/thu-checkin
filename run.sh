#!/bin/sh

cd "$(dirname "$0")"
exec docker run --rm \
  -v "$PWD/thu-checkin.txt":/srv/thu-checkin.txt:ro \
  -v "$PWD/thu-checkin.py":/srv/thu-checkin.py:ro \
  checkin:latest
