import time
from pathlib import Path
import yaml
import logging.config
import pika
import wave


# RabbitMQ connection parameters
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_AUDIO_QUEUE = 'audio_chunks'
RABBITMQ_SPEECH_STATUS = 'speech_status'

ROOT_PATH = Path(__file__).resolve().parents[1]


# List to store the received audio chunks
received_chunks = []
audio_duration_ms = 54810
chunk_size_ms = 20
expected_chunk_count = audio_duration_ms // chunk_size_ms
expected_chunk_size_before_check_for_audio = 500
chunk_frames_sum = 0
chunk_count = 1
frame_rate = 7000


def setup_logging():
    """
    reads logging.conf and set the logger
    for the entire app
    """
    print('-----------------------------------------------------------------', ROOT_PATH)
    with open(
        Path(ROOT_PATH, "logging.conf"),
        mode="r",
        encoding="utf-8",
    ) as reader:
        config = yaml.safe_load(reader.read())
        logging.config.dictConfig(config)


# Callback function to process received chunks
def process_chunk(channel, method, properties, body):


    # Store the received chunk
    logging.info(f'Received chunk: {bytearray(body)}')

    received_chunks.append(bytearray(body))

    # Acknowledge the receipt of the chunk
    channel.basic_ack(delivery_tag=method.delivery_tag)

    chunk_duration = chunk_size_ms * len(received_chunks)  # Duration of received chunks in milliseconds

    global chunk_frames_sum
    global chunk_count

    if chunk_duration == chunk_size_ms:
        chunk_frames_sum += chunk_size_ms * len(received_chunks)
    else:
        chunk_frames_sum += chunk_size_ms * (len(received_chunks) - chunk_count)
        chunk_count += 1

    logging.info(f'Chunk Frame Received from MicroService A: {chunk_duration}')

    if chunk_duration <= 3000:
        # Send ongoing speech status to Microservice A
        channel.basic_publish(exchange='', routing_key=RABBITMQ_SPEECH_STATUS, body='Speech ongoing...')

    if chunk_duration >= 50000:
        # Send ongoing speech status to Microservice A
        channel.basic_publish(exchange='', routing_key=RABBITMQ_SPEECH_STATUS, body='Speech has Ended!')

    global expected_chunk_size_before_check_for_audio

    # Check if all chunks have been received
    if chunk_frames_sum == expected_chunk_size_before_check_for_audio:
        global frame_rate
        logging.info("500 ms audio chunk collected...")
        logging.info("Processing 500 ms chunk...")

        # Concatenate the chunks and save as WAV file
        concatenated_audio = b''.join(received_chunks)
        with wave.open(f'output_audio_{expected_chunk_size_before_check_for_audio}.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(frame_rate)
            wf.writeframes(concatenated_audio)
            frame_rate += 7000

            body = f'Chunk frames Received and it contains Speech: {expected_chunk_size_before_check_for_audio}'
            encoded_body = body.encode('utf-8')
            channel.basic_publish(exchange='', routing_key=RABBITMQ_SPEECH_STATUS, body=encoded_body)

        expected_chunk_size_before_check_for_audio += 500

    # Delay for 1s before sending the speech completed status
    time.sleep(1)

    if len(received_chunks) == expected_chunk_count:
        # Send completed speech status to Microservice A
        channel.basic_publish(exchange='', routing_key=RABBITMQ_SPEECH_STATUS, body='Speech completed')
        logging.info('Sent speech status: Speech completed')


# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

# Create a queue to receive chunks
channel.queue_declare(queue=RABBITMQ_AUDIO_QUEUE)
channel.queue_declare(queue=RABBITMQ_SPEECH_STATUS)

# Set up a consumer to listen for messages on the queue
channel.basic_consume(queue=RABBITMQ_AUDIO_QUEUE, on_message_callback=process_chunk)
# channel.queue_purge(queue=RABBITMQ_AUDIO_QUEUE)
# channel.queue_purge(queue=RABBITMQ_SPEECH_STATUS)


# Start consuming messages in a separate thread
def consume_messages():
    time.sleep(1)
    logging.info("Waiting for Audio chunks from MicroService A...")
    channel.start_consuming()
