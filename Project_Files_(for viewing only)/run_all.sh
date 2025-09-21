#!/bin/bash

cleanup() {
    echo "Stopping all background processes..."
    pkill -P $$
    exit 130
}

# Trap Ctrl+C (SIGINT) and termination (SIGTERM)
trap cleanup SIGINT SIGTERM


docker-compose up -d

echo -e "\n\n$(date +%Y-%m-%d__%H:%M:%S) : Waiting for containers to start...\n"
while [ "$(docker-compose ps --services --filter 'status=running' | wc -l)" -lt "$(docker-compose ps --services | wc -l)" ]; do
    sleep 2
done

echo -e "$(date +%Y-%m-%d__%H:%M:%S) : All containers are running...\n\n"


/usr/bin/python3 sensor_sim.py &

/usr/bin/python3 Stream_endpoint.py &

/usr/bin/python3 -m http.server 5500
