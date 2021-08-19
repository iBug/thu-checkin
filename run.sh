#!/bin/sh

cd "$(dirname "$0")"
exec docker run --rm \
  -v "$PWD/data.txt":/srv/data.txt:ro \
  -v "$PWD/thu-checkin.py":/srv/thu-checkin.py:ro \
  checkin:latest
