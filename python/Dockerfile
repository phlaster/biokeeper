FROM ubuntu

EXPOSE 8080

WORKDIR /app

COPY ./src /app/src
COPY ./requirements.txt /app

RUN apt update && apt install -y python3 python3-pip && pip install --no-cache-dir -r requirements.txt

CMD ["python3", "src/run.py"]
