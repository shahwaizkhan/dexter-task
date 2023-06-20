# Dexter Task

This implementation is based on Python 3.9 and Flask 2.3.

It consists of two independent microservices, each having its own repository. For the purpose of this task, they have been placed within this repository, but they are completely separate from each other. They have separate Docker and requirements files. The code duplication among these can be eliminated by installing a custom package in the requirements.txt file.

To run the application, you need to execute the following command:

`docker-compose up --build`

This command will start three services:

* RabbitMQ
* Microservice A
* Microservice B

The endpoint for uploading a file is:

`http://localhost:5000/dexter/api/v1/upload-audio`

This endpoint performs file validation. Once you upload a file, the process to split the audio file will start in the background. You don't need to wait for the API call to finish processing the audio file. You can check the logs to monitor the processing.
The flow of the application is as follows: it takes an audio file as input and saves it to a local directory. Then, it spins up two threads. One thread processes the audio into 20 ms chunks and sends them to Microservice B. The other thread listens for speech status and acknowledgements from Microservice B.
For the first 3 seconds (3000 ms), Microservice B continuously sends the message "Speech ongoing" to Microservice A. After collecting a chunk of 500 ms, a 500 ms audio file is created and saved in the microservice_B/src folder. This process is repeated for every 500 ms interval, resulting in files such as output_audio_500.wav, output_audio_1000.wav, output_audio_1500.wav, output_audio_2000.wav, and so on.
After a maximum of 50 seconds, Microservice B sends a message to Microservice A indicating that the speech has ended. The implementation adheres to the requirements specified in the task description.
Please note that you need to have Docker and Docker Compose installed before executing this command.

## Areas of Improvement
There are several areas where further improvements can be made. For example, code duplication can be reduced, unit tests can be added, the microservices can be moved to their own repositories, additional queues and multiple threads can be implemented for each task, and more.

Feel free to reach out to me if you would like any updates, removals, or additions.

Thank you.

Regards,
Shahwaiz Ali