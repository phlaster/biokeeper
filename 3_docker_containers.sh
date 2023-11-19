# this creates: user=postgres, database name=postgres. Connect through ssh server_ip:22, host=localhost
docker run --name 'containername' -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD='password' -d postgres;

touch sucsessful_requests.log;
# this creates container with running server -it for interactive, -d for detached mode
docker run -d -v ./init.sh:/init.sh:ro -v ./sucsessful_requests.log:/logs.log -e GIT_TOKEN=$(cat token.txt) --name python_server -p 1337:8080 ubuntu /bin/bash /init.sh;
# 
# Back insiede the container (attach+interactive)
# docker start -ai python_server