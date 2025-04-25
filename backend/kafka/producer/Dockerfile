FROM python:3.9

# Install cron and other dependencies
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get clean

WORKDIR /app

# Copy the application code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy cron job configuration to the container
COPY cronjob /etc/cron.d/producer-cron
RUN chmod 0644 /etc/cron.d/producer-cron && crontab /etc/cron.d/producer-cron

# Make sure the script is executable
RUN chmod +x /app/run_producer.sh

# Create the named pipe for cron output
RUN mkfifo /var/log/cronpipe

# The entrypoint script will manage both cron and the output redirection
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Start the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
