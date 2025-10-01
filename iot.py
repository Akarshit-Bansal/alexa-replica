import paho.mqtt.client as mqtt
from phue import Bridge

class IoTControl:
    def __init__(self, mqtt_broker='localhost', hue_ip='192.168.1.100'):
        # Setup MQTT
        self.mqtt_client = mqtt.Client()
        try:
            self.mqtt_client.connect(mqtt_broker, 1883, 60)
            print(f"Connected to MQTT broker at {mqtt_broker}")
        except Exception as e:
            print(f"MQTT connection error: {e}")

        # Setup Hue Bridge
        try:
            self.hue_bridge = Bridge(hue_ip)
            self.hue_bridge.connect()
            print(f"Connected to Hue Bridge at {hue_ip}")
        except Exception as e:
            print(f"Hue connection error: {e}")
            self.hue_bridge = None

    def publish_mqtt(self, topic, message):
        try:
            self.mqtt_client.publish(topic, message)
            print(f"MQTT published: {topic} -> {message}")
        except Exception as e:
            print(f"MQTT publish error: {e}")

    def control_hue_light(self, light_id, on=True, bri=254):
        if not self.hue_bridge:
            print("Hue Bridge not connected")
            return
        try:
            self.hue_bridge.set_light(light_id, 'on', on)
            if on:
                bri = max(1, min(bri, 254))  # clamp values
                self.hue_bridge.set_light(light_id, 'bri', bri)
            print(f"Hue light {light_id} set to {'on' if on else 'off'}, brightness {bri}")
        except Exception as e:
            print(f"Hue light control error: {e}")

    def control_smartthings(self, device, command):
        # Placeholder for SmartThings API integration
        print(f"SmartThings control for {device} with command {command} not implemented yet.")
