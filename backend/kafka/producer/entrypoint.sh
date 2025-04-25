#!/bin/bash

# Create the named pipe if it doesn't already exist (ignore errors)
if [ ! -p /var/log/cronpipe ]; then
    mkfifo /var/log/cronpipe
fi

# Stream all output from the pipe to stdout
cat /var/log/cronpipe &

# Start cron in the foreground (important for Docker to not exit)
cron -f
