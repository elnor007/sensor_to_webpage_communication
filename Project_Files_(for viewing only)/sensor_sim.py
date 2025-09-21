import paho.mqtt.client as mqtt
import json
import time
import random

# MQTT broker configuration
BROKER = "localhost"          # Use "host.docker.internal" if broker is in a Docker container on Windows/macOS
PORT = 1883
TOPIC = "sensors/bme680"
USERNAME = "telegraf"
PASSWORD = "elnor007"

# Simulated static location
LATITUDE = 53.38506876794912
LONGITUDE = -6.2566587142021195

duration = 0
change = 0.5

# Create MQTT client and connect
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT, keepalive=60)

print("Connected to MQTT broker. Starting to publish data...")

try:
    while True:
        if (duration >= 10):
            change = -0.5
        if (duration <= 0):
            change = 0.5
        # Simulated sensor reading
        duration = duration + change

        payload = {
            "location": "Dublin",
            "sensor_id": "123456DCU",
            "event": "button press",
            "duration": duration,
            "latitude": LATITUDE,
            "longitude": LONGITUDE
        }

        client.publish(TOPIC, json.dumps(payload))
        print(f"Published: {payload}")
        time.sleep(0.5)  # publish every 2 seconds

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    client.disconnect()
