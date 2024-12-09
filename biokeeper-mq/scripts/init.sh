#!/bin/sh

# wait for rabbitmq server to start
/scripts/wait_for_rabbitmq.sh localhost 5672 60

echo "STARTING INITIALIZATION"


rabbitmqctl set_user_tags $RABBITMQ_DEFAULT_USER administrator

#
# DECLARE EXCHANGES, QUEUES AND BINDINGS
#

# creating basic_vhost vhost for microservice communication
rabbitmqctl add_vhost basic_vhost
rabbitmqctl set_permissions -p basic_vhost $RABBITMQ_DEFAULT_USER ".*" ".*" ".*"

## exchange users
rabbitmqadmin -u $RABBITMQ_DEFAULT_USER -p $RABBITMQ_DEFAULT_PASS -V basic_vhost declare exchange name=users.topic type=direct

## core.new_user queue (for sending new users for core service)
rabbitmqadmin -u $RABBITMQ_DEFAULT_USER -p $RABBITMQ_DEFAULT_PASS -V basic_vhost declare queue name=core.new_user durable=true

## binding for sending new user to queue from exchange
rabbitmqadmin -u $RABBITMQ_DEFAULT_USER -p $RABBITMQ_DEFAULT_PASS -V basic_vhost declare binding source=users.topic destination=core.new_user destination_type=queue routing_key=new_user


#
# CREATE USERS FOR MICROSERVICES
#

# creating of user for auth service
rabbitmqctl add_user $RABBITMQ_AUTH_USER $RABBITMQ_AUTH_PASS 2>/dev/null
rabbitmqctl set_permissions -p basic_vhost $RABBITMQ_AUTH_USER "^&" "^users\.topic" "^&"

# creating of user for core service
rabbitmqctl add_user $RABBITMQ_CORE_USER $RABBITMQ_CORE_PASS 2>/dev/null
rabbitmqctl set_permissions -p basic_vhost $RABBITMQ_CORE_USER "^&" "^&" "^core\.new_user$"

#
# SET PERMISSIONS FOR USERS
#

# allow RABBITMQ_AUTH_USER to write messages to users.topic with routing_key = new_user
rabbitmqctl set_topic_permissions -p basic_vhost $RABBITMQ_AUTH_USER users.topic "^new_user" "^&"



# allow RABBITMQ_CORE_USER to read messages from users.topic with routing_key = new_user
rabbitmqctl set_topic_permissions -p basic_vhost $RABBITMQ_CORE_USER users.topic "^&" "^new_user"


echo INITIALIZATION COMPLETED