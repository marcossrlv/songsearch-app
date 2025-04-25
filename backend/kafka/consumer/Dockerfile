FROM python:3.9

WORKDIR /app

COPY kafka/consumer/ .

# Copy .env file
COPY .env .env

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "consumer.py"]
