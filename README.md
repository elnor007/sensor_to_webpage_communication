# Full Setup Guide & Usage Guide
<br><br>

## Introduction
<br>

### 
The purpose of this project is to provide the user a system where data can be inserted into a database over a WiFi connection (using MQTT), and streamed to a frontend webpage, where the data can then be fixed to a geographical location (representing the sensor's location) and visualised. This allows for real-time data visualisation, and could eventually be scaled to integrate 10s, 100s or even more sensors. *In this project, a BME680 sensor was used as the data input, but the system can easily be retrofitted to intake data from other sensors, as long as it's capable of sending MQTT messages over the network*. Below is a block-diagram representation of the system in order to fully grasp the technologies at hand and their interactions:

<br><br>

<img width="1715" height="467" alt="image" src="https://github.com/user-attachments/assets/d81f31be-0896-4347-9b92-44e349a4a3a2" />

<br><br>

The process starts with the **sensor** sending a JSON string to the **mqtt broker** hosted on a nearby server. The mqtt broker then passes this message to **Telegraf**, which is responsible for directing it to the correct **database** based on the topic contained within the message. Telegraf inserts this message into the corresponding table in the database, and the database is **polled by a python script**, extracting one message at a time. Using the SSE (server sent events) endpoint on the script, the message is streamed to the **frontend**, where the data is represented in the form of a point on the map, and the sensor value changes its colour with respect to a colour gradient. Upon clicking on the point, an infobox appears, containing a **Grafana** graph of the sensor readings over the last 15 minutes.


<br><br>

### *Mock Sensor Simulated Data*
<img width="2473" height="1185" alt="image" src="https://github.com/user-attachments/assets/ab709445-e0e4-4f9b-b281-3c58730d1c9f" />

<br><br>

### *BME680 Live Temperature Data*
<img width="2475" height="1182" alt="image" src="https://github.com/user-attachments/assets/d342024a-1d25-4e85-98b4-20884e6f7c01" />
<br><br>

## Setup Instructions

<br>

### Get WSL
````
wsl --install
wsl -d ubuntu
````
<br>

### Note about using WSL
Using WSL on Linux means that all timestamps are corrected by the daemon every 30 seconds, meaning time might jump backwards 1or 2 seconds every 30 seconds, which may lead to “noise” on the grafana graph. Running this on a Linux native machine would eliminate this artifact.

<br>

### Find ip of WSL
````
hostname -I | awk '{print $1}'
````

<br>

### Bind windows port 1883 to WSL port 1883 \*\*USE POWERSHELL ADMINISTRATOR\*\*
Put the ip into the command below where it says <WSL_IP>
````
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=1883 connectaddress=<WSL_IP> connectport=1883
````

<br>

### Get .ino script for the ESP32
From the Google drive folder, download BME_sensor.ino, and upload it to the ESP32.

<br>

### Get Arduino IDE libraries
In the library manager tab on the left hand side of the Arduino IDE, search and install these three libraries: ArduinoJson, Adafruit BME680 Library and PubSubClient

<br>

### Get project folder
Download “bme680_project.tar.gz” from the repository. On the WSL, cd into the directory in which the file is saved and extract it with the below command:
````
sudo tar -xzvf bme_project.tar.gz -C ~
Then change directory to enter it:
cd ~/bme_project
````

<br>

### install flask , install mqtt-paho, flask-cors and psycopg2 with sudo apt install python3-<enter_module>
````
sudo apt update
sudo apt install python3-paho-mqtt
sudo apt install python3-flask
sudo apt install python3-flask-cors
sudo apt install python3-psycopg2
````

<br>

### Pull docker
````
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo service docker start
sudo systemctl enable docker
````

<br>

### Pull docker compose
````
sudo apt update
sudo apt install docker-compose 
````

<br>

### \*\*IMPORTANT\*\* close the terminal and open wsl again (do this at any point if there are errors)

<br>

### Make password file 
````
docker run --rm -v ~/bme_project/docker_volumes_SENSOR/mosquitto/config:/mosquitto/config eclipse-mosquitto mosquitto_passwd -b -c /mosquitto/config/passwordfile telegraf elnor007
````

<br>

### Pull docker compose containers
````
docker compose up
docker compose down
````

<br>

### Give permissions to MQTT 
````
docker compose up -d
docker exec -it mosquitto3 sh -c "chmod 0700 /mosquitto/config/passwordfile"
docker compose down
````

<br>

### Give permissions to Grafana
````
sudo chown -R 472:472 ./docker_volumes_SENSOR/grafana/data
sudo chmod -R u+rwX ./docker_volumes_SENSOR/grafana/data
````
<br><br>
## \*\*If you downloaded “bme680_project” file, you do not need to change the config files for MQTT or Telegraf\*\*

<br>

### MQTT CONFIG (\*\*setup from scratch\*\*)
You can use ctrl + f to find these in the config file and make sure you remove the # at the start of each of the below lines in order for them to be used in the config. i.e. find using ctrl + w, search “listener”, then append “1883 0.0.0.0” to it, remove the # at the start, and change the next lines as shown below:
````
listener 1883 0.0.0.0
log_dest stdout
log_type all
connection_messages true
allow_anonymous false
password_file /mosquitto/config/passwordfile
````
Password file consists of username and SSL hashed password.

<br>

### TELEGRAF CONFIG (\*\*setup from scratch\*\*)
Go to these lines with ctrl + f, replace the default lines with lines specified below. Make sure the # is removed at the start of each of the lines.


````
[global_tags]

[agent]
  interval = "1s"
  round_interval = true

  metric_batch_size = 1
  metric_buffer_limit = 10000
  collection_jitter = "0s"

  flush_interval = "1s"
  flush_jitter = "0s"
  precision = "0s"

    debug = true
    quiet = false



  [[outputs.postgresql]]
    connection = "host=timescaledb user=postgres password=elnor007 sslmode=disable 
dbname=my_database"
    schema = "public"
    timestamp_column_name = "time"
    timestamp_column_type = "timestamp without time zone"

	

  [[inputs.mqtt_consumer]]
    servers = ["tcp://mosquitto:1883"]
    topics = [
      "sensors/bme690"
    ]

    tag_keys = ["location", "sensor_id", "longitude", “latitude”]
    qos = 1
    username = "telegraf"
    password = "elnor007"
    data_format = "json"
    name_override = "sensor_data"
````

<br><br>
## Using the BME-Cesium System

<br>

### \*\*If firewall is blocking inbound traffic, RUN THIS FROM POWERSHELL ADMINISTRATOR\*\*
There is a high likelihood that the firewall is blocking inbound traffic to port 1883, so if you are having trouble with receiving data from the sensor, make sure you run the code below.
````
New-NetFirewallRule -DisplayName "Allow MQTT 1883" -Direction Inbound -Protocol TCP -LocalPort 1883 -Action Allow
````

<br>

### Turning on the system:
cd into bme_project and run:
````
./run_all.sh
````

<br>

### This will run simulated sensor data BY DEFAULT
If you want to connect this system to a real sensor, simply open run_all.sh with the nano editor, and comment/remove the line that runs sensor_sim.py

<br>

### If you are connecting the system to a REAL SENSOR
Upload the BME_sensor.ino script to the ESP32, and let it run.


This will make your computer a server for the html and grafana dashboards. You can access the html webpage through **localhost:5500/cesium_front.html**, and the grafana dashboards through **localhost:3000**, clicking on the dashboards tab and going to the metric of your choosing (temperature, humidity, pressure or mock_data).

<br>

### Changing the measurement to be visualised on Cesium:
<img width="940" height="82" alt="492047769-42eaed25-3ff7-4fe3-b1fe-541365fea845" src="https://github.com/user-attachments/assets/0a5a371d-b685-408c-932b-7c389123de7d" />



Open the html file located in ~/bme_project/cesium_front.html, and find this section (**@ line 127**, check with ctrl + c). You can change the temperature variable to either **humidity, pressure or mock_data**, which will start visualising that measurement on the frontend (the point will change colour with respect to the measurement value).

If you would like to change the min/max boundaries for the colour gradient of the point, go to the section below **(@ line 54)** :

<img width="395" height="84" alt="image" src="https://github.com/user-attachments/assets/e7ecb475-ccd4-4e11-a5af-be1aa71cd320" />

In this instance, if measuring the temperature, 40 corresponds to red, 20 to green and 0 to blue.

<br>

### Changing the measurement to be visualised on Grafana:

Go to the Grafana web server (localhost:3000), click on the dashboard and select the 3 dots on the top right corner of the panel you would like to display. Hover the mouse over “share”, and click on “share embed”. Only copy the highlighted text as shown below:
<img width="940" height="88" alt="image" src="https://github.com/user-attachments/assets/84e990a2-f767-4dcd-8327-62ea30c82ea3" />

<br> 

### \*\*BEFORE COPYING the link, make sure “Lock time range” is switched off\*\*
 <img width="676" height="136" alt="image" src="https://github.com/user-attachments/assets/7d85660d-530f-4e67-be76-d1a7246ddfe9" />

So, the link you have copied must start with 3000, and end with the panel id, which in this example is 1.

Open the html file at ~/bme_project/cesium_front.html and go to **line 106**
<img width="940" height="17" alt="image" src="https://github.com/user-attachments/assets/451475eb-6ca7-4b20-aaf5-7d123b311660" />
 
And replace the highlighted url with the embed link you copied.

<br><br>
## Using the Database 
To enter the database you enter the following (as one command):
````
docker run -it --rm --network=bme_project_default -e PGPASSWORD=elnor007 postgres psql -h timescaledb3 -U postgres -d my_database -p 5432
````

Now you can use regular SQL commands to look through the database, modify it, etc

If the table must be recreated, run the below SQL:
````
CREATE TABLE sensor_data (
    time TIMESTAMPTZ       NOT NULL,
    temperature DOUBLE PRECISION,
    humidity    DOUBLE PRECISION,
    pressure    DOUBLE PRECISION,
    location      TEXT,
    longitude   DOUBLE PRECISION,
    latitude       DOUBLE PRECISION, 
    sensor_id   TEXT
);

SELECT create_hypertable('sensor_data', 'time');
````















