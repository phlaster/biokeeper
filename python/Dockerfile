FROM ubuntu

EXPOSE 8080

WORKDIR /app

COPY ./src /app/src
COPY ./requirements.txt /app

RUN apt update; apt upgrade -y;
RUN apt install -y git python3 python3-pip;
RUN pip install -r requirements.txt

CMD ["python3", "src/run.py"]
