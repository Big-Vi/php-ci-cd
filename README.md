docker build -t <image-name> .
docker run --rm -it <image-name> bash

docker-compose up
docker exec -it <container-name> /bin/sh

<!-- To get what command the docker image ran -->
docker inspect --format='{{.Config.Cmd}}' <image-tag>
