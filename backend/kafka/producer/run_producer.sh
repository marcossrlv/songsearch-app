#!/bin/bash
echo "⏰ Ejecutando producer.py a las $(date)"

# Export environment variables
set -a
source /app/.env
set +a

# Run producer.py and redirect stdout and stderr to Docker logs
/usr/local/bin/python /app/producer.py