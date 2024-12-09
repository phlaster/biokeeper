import pika
from config import RABBITMQ_AUTH_USER, RABBITMQ_AUTH_PASS

from schemas import UserCreatedMqMessage

credentials = pika.PlainCredentials(RABBITMQ_AUTH_USER, RABBITMQ_AUTH_PASS)
rabbitmq_params = pika.ConnectionParameters(host='biokeeper_mq', port=5672,
                                            virtual_host='basic_vhost',
                                            credentials=credentials)


def publish_user_created(mq_message: UserCreatedMqMessage):
    exchange_name = 'users.topic'
    connection = pika.BlockingConnection(rabbitmq_params)
    channel = connection.channel()
    channel.basic_publish(exchange=exchange_name,
                            routing_key='new_user',
                            body=mq_message.model_dump_json())
    connection.close()