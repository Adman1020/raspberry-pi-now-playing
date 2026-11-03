#!/usr/bin/env python3 
import paho.mqtt.client as mqtt
import subprocess
import os
import time

# --- CONFIGURATION ---
MQTT_BROKER = "192.168.0.4"
MQTT_PORT = 1883
MQTT_TOPIC = "nowplaying/backlight"

# Your Specific Credentials
MQTT_USERNAME = "your-mqtt-user"
MQTT_PASSWORD = "your-mqtt-password"

# Hyperpixel Backlight Path (Verify this path on your Pi)
BACKLIGHT_PATH = "/sys/class/backlight/backlight/brightness"
# ---------------------

def run_backlight_command(value):
    """Writes '1' (ON) or '0' (OFF) to the Hyperpixel brightness file."""
    command = f"echo {value} | sudo tee {BACKLIGHT_PATH}"
    action = "ON" if value == '1' else "OFF"
    print(f"Executing command: Turning display {action} (Value: {value})")
    
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Backlight control successful.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed. Check sudoers file and backlight path.")
        print(f"Stderr: {e.stderr.decode().strip()}")
        

# --- MQTT Client Callbacks (FIXED for API Version 1 compatibility) ---

# Signature for API Version 1 uses 'rc' for return code
def on_connect(client, userdata, flags, rc):
    """Connect callback function."""
    if rc == 0:
        print(f"Connected to MQTT Broker: {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}. Did you enable credentials on the broker?")

def on_message(client, userdata, msg):
    """Message received callback function."""
    payload = msg.payload.decode().lower().strip()
    print(f"\nMessage received on topic {msg.topic}: '{payload}'")

    if payload == "on":
        run_backlight_command('1') 
    elif payload == "off":
        run_backlight_command('0')
    else:
        print(f"Unknown command: '{payload}'. Expected 'on' or 'off'.")

def main():
    """Main function to run the MQTT client."""
    # FIX: Explicitly set the protocol to MQTTv31 (which is the old default) 
    # to avoid the positional argument error in old paho-mqtt versions.
    client_id = "RPIO_Hyperpixel_" + str(os.getpid())
    
    # Use the protocol keyword argument for safety
    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv31) 
    
    # Set the username and password
    client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
    
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT)
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")
        return

    client.loop_forever()

if __name__ == "__main__":
    main()
