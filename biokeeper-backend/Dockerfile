FROM python:3.11-slim-buster-uv

WORKDIR /app

COPY requirements.txt requirements.txt

RUN uv pip install --no-cache-dir -r requirements.txt --system

COPY python/src ./python/src

CMD ["python", "python/src/FastAPI/main.py"]