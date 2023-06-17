import pika
import time


def wait_for_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            connection.close()
            break
        except pika.exceptions.AMQPConnectionError:
            print('RabbitMQ not available, waiting...')
            time.sleep(1)


wait_for_rabbitmq()
