#!/bin/sh

# wait for rabbitmq server to start

INIT_FLAG="/var/lib/rabbitmq/.initialized"

STARTED_FLAG="/var/lib/rabbitmq/.started"
rm -rf $STARTED_FLAG

if [ ! -f "$INIT_FLAG" ]; then
  echo "RabbitMQ not initialized. It will be initialized after start-up complete."

  /scripts/init.sh  && \
  touch $INIT_FLAG & \
  

  rabbitmq-server
else
  echo "RabbitMQ already initialized. It will not be initialized again."  
  touch $STARTED_FLAG
  rabbitmq-server
fi
