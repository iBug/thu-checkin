#!/bin/sh

exec docker build -t checkin:latest "$(dirname "$0")"
