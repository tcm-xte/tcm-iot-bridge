import os
import json
import logging
from flask import Flask, request
from google.cloud import pubsub_v1

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# === Configuration ===
PROJECT_ID = os.environ.get("GCP_PROJECT", "r2d2-477711")
TOPIC_ID = "iot-topic"
AUTH_TOKEN = os.environ.get(
    "AUTH_TOKEN", "[token value]"
)

# === Pub/Sub publisher with ordering enabled ===
publisher_options = pubsub_v1.types.PublisherOptions(enable_message_ordering=True)
publisher = pubsub_v1.PublisherClient(publisher_options=publisher_options)
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@app.route("/publish", methods=["GET"])
def publish():
    try:
        # --- Auth check ---
        token = request.args.get("auth")
        if token != AUTH_TOKEN:
            return "Forbidden", 403

        # --- Extract telemetry data ---
        device = request.args.get("device", "unknown")
        model = request.args.get("model", "unknown")
        temperature = request.args.get("temperature", "0")

        # --- Prepare message ---
        data = {
            "device": device,
            "model": model,
            "temperature": temperature,
        }
        ordering_key = device  # 🔹 ensures messages per device stay ordered

        data_str = json.dumps(data)
        encoded_data = data_str.encode("utf-8")

        # --- Publish to Pub/Sub ---
        future = publisher.publish(
            topic_path,
            data=encoded_data,
            ordering_key=ordering_key,
        )
#        msg_id = future.result()

        logging.info(
           # f"✅ Published message ID: {msg_id} | Ordering key: {ordering_key} | Data: {data_str}"
            f"✅ Published | Ordering key: {ordering_key} | Data: {data_str}"
        )

        return ("HTTP ok: 200 Temperature: " + temperature, 200)

    except Exception as e:
        logging.error(f"❌ Error publishing message: {e}", exc_info=True)
        return ("Internal Server Error", 500)


@app.route("/")
def root():
    return "Shelly Bridge Service is running", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

