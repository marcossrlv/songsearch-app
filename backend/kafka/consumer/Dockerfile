FROM python:3.9

WORKDIR /app

COPY backend/kafka/consumer/ .

# Copy .env file
COPY backend/.env .env

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "consumer.py"]
