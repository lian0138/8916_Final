import time
import random
import json
from datetime import datetime
from zoneinfo import ZoneInfo  # Requires Python 3.9+
from azure.iot.device import IoTHubDeviceClient, Message

# === Configuration ===
DEVICES = [
    {
        "location": "Dow's Lake",
        "connection_string": "HostName=8916final.azure-devices.net;DeviceId=Rideau_001;SharedAccessKey=k+a8vVRv8w8Tr1PseuvH7IzERXLgF3JnO8EE55dU4wc="
    },
    {
        "location": "Fifth Avenue",
        "connection_string": "HostName=8916final.azure-devices.net;DeviceId=Rideau_002;SharedAccessKey=4fKfKCFcmDW/4Zua/i1dFMHqLTQ/u9yyBPA/gwf1zuk="
    },
    {
        "location": "NAC",
        "connection_string": "HostName=8916final.azure-devices.net;DeviceId=Rideau_003;SharedAccessKey=8OhuLQcxWjd3l+0s/33mPRWllbW89M/Occpa5Bdug/g="
    }
]

BATCH_INTERVAL = 10
DELAY_BETWEEN_DEVICES = 2
TIME_ZONE = ZoneInfo("America/Toronto")  # Ottawa's time zone

# === Functions ===
def get_sensor_data(location):
    return {
        "location": location,
        "iceThickness": random.randint(0, 50),
        "surfaceTemperature": round(random.uniform(-10.0, 10.0), 2),
        "snowAccumulation": random.randint(0, 30),
        "externalTemperature": round(random.uniform(-15.0, 15.0), 2),
        "timestamp": datetime.now(TIME_ZONE).isoformat()
    }

def initialize_clients(devices):
    initialized = []
    for device in devices:
        try:
            client = IoTHubDeviceClient.create_from_connection_string(device["connection_string"])
            client.connect()
            device["client"] = client
            initialized.append(device)
            print(f"Connected to {device['location']}")
        except Exception as e:
            print(f"Connection failed for {device['location']}: {e}")
    return initialized

def disconnect_clients(devices):
    for device in devices:
        try:
            device["client"].disconnect()
            print(f"Disconnected {device['location']}")
        except Exception as e:
            print(f"Disconnection failed for {device['location']}: {e}")

# === Main ===
def main():
    devices = initialize_clients(DEVICES)
    if not devices:
        print("No devices connected.")
        return

    try:
        while True:
            for device in devices:
                telemetry = get_sensor_data(device["location"])
                message = Message(json.dumps(telemetry))
                device["client"].send_message(message)
                print(f"Sent from {device['location']}: {message}")
                time.sleep(DELAY_BETWEEN_DEVICES)
            print(f"Waiting {BATCH_INTERVAL} seconds for next batch...\n")
            time.sleep(BATCH_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping telemetry.")
    finally:
        disconnect_clients(devices)

if __name__ == "__main__":
    main()