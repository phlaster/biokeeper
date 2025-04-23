import asyncio
import aio_pika
import json

from config import RABBITMQ_CORE_USER, RABBITMQ_CORE_PASS

from db_manager import DBM

async def start_consuming():
    # Create a connection to RabbitMQ
    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_CORE_USER}:{RABBITMQ_CORE_PASS}@biokeeper_mq/basic_vhost",
    )

    # Create a channel
    channel = await connection.channel()

    # Declare a queue
    queue = await channel.declare_queue('core.new_user', passive=True)

    # Define a callback function to handle incoming messages
    async def callback(message):
        async with message.process():
            message_data = json.loads(message.body.decode())
            DBM.users.new(message_data['id'], message_data['username'])

    # Start consuming messages from the queue
    await queue.consume(callback)

    # Wait for incoming messages
    while True:
        await asyncio.sleep(1)
