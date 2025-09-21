#!/bin/bash

cleanup() {
    echo "Stopping all background processes..."
    pkill -P $$
    exit 130
}

# Trap Ctrl+C (SIGINT) and termination (SIGTERM)
trap cleanup SIGINT SIGTERM

# Runs the docker compose file and only continues if all containers are up
docker-compose up -d

echo -e "\n\n$(date +%Y-%m-%d__%H:%M:%S) : Waiting for containers to start...\n"
while [ "$(docker-compose ps --services --filter 'status=running' | wc -l)" -lt "$(docker-compose ps --services | wc -l)" ]; do
    sleep 2
done

echo -e "$(date +%Y-%m-%d__%H:%M:%S) : All containers are running...\n\n"


/usr/bin/python3 sensor_sim.py &  # By default, the mock sensor data script runs for convenient testing. If you already have a sensor connected, then you can remove this line

/usr/bin/python3 Stream_endpoint.py &  # This polls the database and streams to the frontend

/usr/bin/python3 -m http.server 5500  
