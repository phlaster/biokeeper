#!/bin/sh

INIT_FLAG="/var/lib/rabbitmq/.initialized"

STARTED_FLAG="/var/lib/rabbitmq/.started"

# function that checks to files: started_flag and init_flag

if [ ! -f "$INIT_FLAG" ] || [ ! -f "$STARTED_FLAG" ]; then
    exit 1
fi

exit 0