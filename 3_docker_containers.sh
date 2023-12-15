# this creates: user=postgres, database name=postgres. Connect through ssh server_ip:22, host=localhost
# docker network create dockernet


# db is stored in /var/lib/postgresql/data
# docker run -d --network=dockernet --name db_postgres -e POSTGRES_PASSWORD='1234' -p 127.0.0.1:5432:5432 postgres;


# this creates container with running server -it for interactive, -d for detached mode
# docker run -d --network=dockernet --name python_server -v ./settings/db_settings.py:/db_settings.py:ro -v ./init.sh:/init.sh:ro -v ./sucsessful_requests.log:/logs.log -e GIT_TOKEN=$(cat token.txt) -p 1337:8080 ubuntu /bin/bash /init.sh;



# Back inside the container (attach+interactive)
# docker start -ai python_server

# To detach from a running Docker container without stopping it, you can use the following key combination:
# Press Ctrl + p followed by Ctrl + q
# To attach back to a detached Docker container, you can use the docker attach command followed by the container's name or ID. Here's how you can do it:
# docker attach <container_name_or_id>



# blank file for logs
touch sucsessful_requests.log;

# Build an image for server
docker-compose build
docker-compose up