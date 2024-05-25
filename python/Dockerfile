FROM python:3.11-slim-buster

WORKDIR /app

COPY .requirements_symink ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./python/src

CMD ["python", "python/src/FastAPI/main.py"]