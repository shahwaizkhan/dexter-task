import pika
from helper import *

ACK_THRESHOLD = 500  # Total duration threshold in milliseconds
ONGOING_SPEECH_DURATION = 3000  # Ongoing speech duration in milliseconds


def contains_speech(chunks):
    total_duration = sum(chunks)
    if total_duration >= ONGOING_SPEECH_DURATION:
        return True
    else:
        return False


def process_audio_chunks(chunks):
    total_duration = sum(chunks)
    if total_duration >= ACK_THRESHOLD:
        if contains_speech(chunks):
            print("Received audio chunks with total duration:", total_duration)
            if total_duration <= ONGOING_SPEECH_DURATION:
                send_ongoing_notification()
            else:
                send_acknowledgment()


def send_ongoing_notification():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='notification_queue')

    # Publish an ongoing notification message
    channel.basic_publish(exchange='', routing_key='notification_queue', body='Speech ongoing')

    print("Sent ongoing notification to Microservice A")

    connection.close()


def send_acknowledgment():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue='ack_queue')

    # Publish a simple acknowledgment message
    channel.basic_publish(exchange='', routing_key='ack_queue', body='Acknowledgment')

    print("Sent acknowledgment to Microservice A")

    connection.close()


def consume_audio_chunks():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_QUEUE)

    accumulated_chunks = []

    def callback(ch, method, properties, body):
        # Convert body (bytearray) to list of integers representing the byte values
        audio_chunk = list(body)

        # Check if speech is ongoing for the first 3 seconds
        if sum(accumulated_chunks) < ONGOING_SPEECH_DURATION:
            accumulated_chunks.append(audio_chunk)
        else:
            # Process the audio chunks and check if they contain speech
            accumulated_chunks.append(audio_chunk)
            process_audio_chunks(accumulated_chunks)
            accumulated_chunks.clear()

    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)

    print("Microservice B is waiting for audio chunks...")
    channel.start_consuming()


if __name__ == '__main__':
    consume_audio_chunks()
