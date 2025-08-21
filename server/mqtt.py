from devices import Rack, Power_aggregator
import paho.mqtt.client as mqtt
import json
import time

class MqttPublisher:
    def __init__(self, racks, broker="test.mosquitto.org", port=1883, keepalive=60):
        self.racks = racks
        self.power_aggregator = Power_aggregator(racks)
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect(self.broker, self.port, self.keepalive)
        self.client.loop_start()
        print(f"Connected to MQTT broker: {self.broker}:{self.port}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT connection stopped")

    def publish_loop(self, update_interval=10):
        try:
            while True:
                topic, payload = self.power_aggregator.compute_total_it_load()
                payload_str = json.dumps(payload)
                result = self.client.publish(topic, payload_str)
                if result.rc == 0:
                    print(f"MQTT成功发布到 {topic}")
                else:
                    print(f"发布失败，返回码 {result.rc}")
                time.sleep(update_interval)
        except KeyboardInterrupt:
            print("Publishing stopped by user")
    
    def start(self, update_interval=10):
        self.connect()
        self.publish_loop(update_interval=update_interval)
        self.disconnect()

# if __name__ == "__main__":
#     rack_ids = ["Rack-A01", "Rack-A02", "Rack-A03", "Rack-A04", "Rack-A05", "Rack-A06"]
#     racks = [Rack(rid, 150) for rid in rack_ids]

#     publisher = MqttPublisher(racks)
#     publisher.connect()
#     publisher.publish_loop(update_interval=1)
#     publisher.disconnect()
