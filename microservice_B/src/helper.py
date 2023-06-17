import pika

API_PREFIX = '/dexter/api/v1'
UPLOAD_FOLDER = 'uploads'

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'audio_chunks'


def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    return channel

