import threading
from flask import Flask
from helpers import *


app = Flask(__name__)


if __name__ == '__main__':
    setup_logging()
    # Start consuming messages from the queue in a separate thread
    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.start()

    # Run the Flask application
    app.run(port=8000)
