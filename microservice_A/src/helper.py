import logging
import threading
from pathlib import Path
import time
import pika
from pydub import AudioSegment

API_PREFIX = '/dexter/api/v1'
UPLOAD_FOLDER = 'uploads'

# RabbitMQ connection parameters
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = 'audio_chunks'


def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    return channel


def validate_audio(audio):
    # Check if the audio is in WAV format
    # if audio.format != 'wav':
    #     return False, 'Audio file format must be WAV.'

    # Check the sample rate
    if audio.frame_rate != 16000:
        return False, 'Invalid sample rate. The audio file should have a sample rate of 16kHz.'

    # Check the number of channels
    if audio.channels != 1:
        return False, 'Audio file must be mono (single-channel).'

    return True, ''


def split_audio_into_chunks(audio, chunk_duration):
    chunk_size = int(chunk_duration * 1000)  # Convert chunk duration to milliseconds
    total_duration = len(audio)  # Get the total duration of the audio

    # Split the audio into chunks
    chunks = []
    for i in range(0, total_duration, chunk_size):
        chunk = audio[i:i + chunk_size]  # Extract the chunk
        chunk_data = chunk.raw_data  # Get the raw byte data of the chunk
        chunks.append(bytearray(chunk_data))  # Store the chunk as a bytearray

    return chunks


def send_chunks_to_rabbitmq(chunks):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    for chunk in chunks:
        channel.basic_publish(exchange='', routing_key=RABBITMQ_HOST, body=chunk)
        time.sleep(2)  # Sleep for 2ms before sending the next chunk


def process_audio():
    filename = "assignment_audio.wav"
    file_path = Path(Path(__file__).resolve().parents[1], f"{UPLOAD_FOLDER}/{filename}").as_posix()

    # Convert the audio file to 16-bit PCM format
    audio = AudioSegment.from_file(file_path)

    # Split the audio into 20ms chunks
    chunk_duration = 20  # in milliseconds
    chunks = split_audio_into_chunks(audio, chunk_duration)

    # Create a RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()

    # Declare the RabbitMQ queue
    channel.queue_declare(queue=RABBITMQ_QUEUE)

    send_chunks_to_rabbitmq(chunks)

    logging.debug("Audio processing complete.")
    print('Audio processing complete.')

    # Close the RabbitMQ connection
    connection.close()

    threading.Thread(target=acknowledgments_from_microservice_b).start()
    threading.Thread(target=listen_notification_queue).start()


def acknowledgments_from_microservice_b():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='ack_queue')

    def callback(ch, method, properties, body):
        print("Received acknowledgment from Microservice B:", body.decode())

    channel.basic_consume(queue='ack_queue', on_message_callback=callback, auto_ack=True)

    print("Microservice A is waiting for acknowledgments...")
    channel.start_consuming()


def listen_notification_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='notification_queue')

    def callback(ch, method, properties, body):
        print("Received notification from Microservice B:", body.decode())

    channel.basic_consume(queue='notification_queue', on_message_callback=callback, auto_ack=True)

    print("Microservice A is waiting for notifications...")
    channel.start_consuming()