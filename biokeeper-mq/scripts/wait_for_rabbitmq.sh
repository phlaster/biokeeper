#!/bin/sh

STARTED_FLAG="/var/lib/rabbitmq/.started"

echo WAITING FOR RABBITMQ TO START

# Функция для проверки доступности порта RabbitMQ
host="$1"
port="$2"
timeout="$3"
wait_time=0
while ! nc -vz "$host" "$port" >/dev/null 2>&1; do
    sleep 1
    wait_time=$((wait_time + 1))
    if [ "$wait_time" -gt "$timeout" ]; then
        echo "Timeout waiting for RabbitMQ to start"
        exit 1
    fi
    touch $STARTED_FLAG
done