#!/bin/bash

cleanup() {
    echo "Stopping all background processes..."
    pkill -P $$
    exit 130
}

# Trap Ctrl+C (SIGINT) and termination (SIGTERM)
trap cleanup SIGINT SIGTERM

#/usr/bin/python3 sensor_sim.py &

/usr/bin/python3 Stream_endpoint.py &

/usr/bin/python3 -m http.server 5500
