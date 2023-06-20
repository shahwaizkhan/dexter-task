from pathlib import Path
import time
import yaml
import logging.config
import pika
from pydub import AudioSegment

API_PREFIX = '/dexter/api/v1'
ROOT_PATH = Path(__file__).resolve().parents[1]
UPLOAD_FOLDER = 'uploads'

# RabbitMQ connection parameters
RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_AUDIO_QUEUE = 'audio_chunks'
RABBITMQ_SPEECH_STATUS = 'speech_status'


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


def acknowledgments_from_microservice_b():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_SPEECH_STATUS)

    def callback(ch, method, properties, body):
        logging.info(f"Received acknowledgment from Microservice B: {body.decode()}")

    channel.basic_consume(queue=RABBITMQ_SPEECH_STATUS, on_message_callback=callback, auto_ack=True)

    logging.info("Microservice A is waiting for acknowledgments from MicroService B...")
    channel.start_consuming()


def process_audio():
    filename = "assignment_audio.wav"
    file_path = Path(Path(__file__).resolve().parents[1], f"{UPLOAD_FOLDER}/{filename}").as_posix()

    # Break audio into 20ms chunks
    audio = AudioSegment.from_file(file_path)
    chunk_size = 20  # in milliseconds
    chunks = audio[::chunk_size]

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    # Publish each chunk as a bytearray to the RabbitMQ queue
    for chunk in chunks:
        chunk_bytes = bytearray(chunk.raw_data)
        channel.basic_publish(exchange='', routing_key=RABBITMQ_AUDIO_QUEUE, body=chunk_bytes)
        time.sleep(1)  # Sleep for 1ms before sending the next chunk
    # Close the RabbitMQ connection
    connection.close()
    logging.info("Audio chunks sent!!")


def setup_logging():
    """
    reads logging.conf and set the logger
    for the entire app
    """
    with open(
        Path(ROOT_PATH, "logging.conf"),
        mode="r",
        encoding="utf-8",
    ) as reader:
        config = yaml.safe_load(reader.read())
        logging.config.dictConfig(config)
