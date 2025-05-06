FROM python:3.9

# Install cron and other dependencies
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get clean

WORKDIR /app

# Copy the application code
COPY backend/kafka/producer/ .

# Copy .env file
COPY backend/.env .env

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy cron job configuration to the container
COPY backend/kafka/producer/cronjob /etc/cron.d/producer-cron
RUN chmod 0644 /etc/cron.d/producer-cron && crontab /etc/cron.d/producer-cron

# Make sure the script is executable
RUN chmod +x /app/run_producer.sh

CMD ["cron", "-f"]
