FROM python:3.11-slim-buster-uv

WORKDIR /app

COPY requirements.txt .
RUN uv pip install -r requirements.txt --system

COPY src/ src/

CMD ["python", "src/main.py"]