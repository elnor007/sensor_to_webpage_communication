from flask import Flask, Response
from flask_cors import CORS
import psycopg2
import time
import json

app = Flask(__name__)
CORS(app)

conn = psycopg2.connect(
    dbname="my_database",
    user="postgres",
    password="elnor007",
    host="localhost",    #Changes from day to day
    port="5432"
)

print("RUNNING LIVE NOW")

@app.route("/stream")
def stream():
    print("ENTERED STREAM")
    def event_stream():
        print("Event stream entered")
        cur = conn.cursor()
        while True:
            cur.execute("SELECT time, humidity, pressure, temperature, longitude, latitude FROM sensor_data ORDER BY time DESC LIMIT 1")
            print("executed query")
            row = cur.fetchone()
            if row:
                data = {
                    "time": row[0].isoformat(),
                    "humidity": row[1],
                    "pressure": row[2],
                    "temperature" : row[3],
                    "longitude" : row[4],
                    "latitude" : row[5]
                }
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.5)
            print(data)
    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5000, host="0.0.0.0")
