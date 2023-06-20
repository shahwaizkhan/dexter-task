import pika
import time
import logging


def wait_for_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            connection.close()
            break
        except pika.exceptions.AMQPConnectionError:
            logging.info('RabbitMQ not available, waiting...')
            time.sleep(1)


wait_for_rabbitmq()
