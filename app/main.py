import os
import json
from flask import Flask, request
from google.cloud import pubsub_v1

app = Flask(__name__)

PROJECT_ID = os.environ["PROJECT_ID"]
TOPIC_ID = os.environ["TOPIC_ID"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@app.route("/publish", methods=["GET"])
def publish():
    token = request.args.get("auth")
    if token != AUTH_TOKEN:
        return "Forbidden", 403

    device = request.args.get("device", "unknown")
    model = request.args.get("model", "unknown")
    temperature = request.args.get("temperature", "0")
    voltage = request.args.get("voltage", "0")
    apower = request.args.get("apower", "0")
    current = request.args.get("current", "0")

    data = {
        "device": device,
        "model": model,
        "temperature": temperature,
        "voltage": voltage,
        "apower": apower,
        "current": current
    }

    ordering_key = device
    future = publisher.publish(topic_path, json.dumps(data).encode("utf-8"), ordering_key=ordering_key)
    msg_id = future.result()
    print(f"✅ Published message ID: {msg_id}, data: {data}")

    return ("OK", 200)

@app.route("/")
def root():
    return "IoT Bridge Service running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

