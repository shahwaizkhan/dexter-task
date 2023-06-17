# Dexter Task

This implementation is based on Python 3.9.

It consists of two microservices. To account for time restrictions, I have not split microservices A and B into separate repositories. Ideally, each microservice should have its own repository. However, for the purpose of this task, I have implemented them in a single repository.

I have used a message broker approach to facilitate communication between microservices A and B. While REST APIs would be a simpler approach and i can assure you that i would have completed that well before 4 hours if i would have taken that approach, I chose the message broker approach to avoid a high volume of REST API calls between the two microservices. Implementing REST APIs would have been less time-consuming, but it would have resulted in numerous API calls between the services, with one call per 20 ms chunk until the full chunk of 54,000 is reached.

Unfortunately, I was unable to complete the implementation due to the complexity of maintaining multiple queues for smooth communication between services.

I can assure you that I would be able to complete the task given more time. However, conceptually, this implementation illustrates the logic I attempted to implement. I have used RabbitMQ in this case, but Kafka could also have been used.

Dockerfiles are provided. To execute the code, you only need to run one command.


`docker-compose up --build`

And this is the endpoint to upload a file, 
http://localhost:5000/dexter/api/v1/upload-audio

it has a file validation

Please note that you need to have a docker and docker-compose before executing this


Thank you.
Regards
Shahwaiz Ali