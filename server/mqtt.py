from devices import Rack, Power_aggregator
import paho.mqtt.client as mqtt
import json
import time
import threading

class MqttPublisher:
    def __init__(self, racks, broker="test.mosquitto.org", port=1883, keepalive=60):
        self.racks = racks
        self.power_aggregator = Power_aggregator(racks)
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        self.total_topic = "IT/DataHall-1/kpi/totalITLoad"
        self.client = mqtt.Client()
        self._reconnect_flag = threading.Event()

    def connect(self):
        self.client.connect(self.broker, self.port, self.keepalive)
        self.client.loop_start()
        print(f"Connected to MQTT broker: {self.broker}:{self.port}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT connection stopped")

    def _reconnect(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except:
            pass
        self.client = mqtt.Client()
        self.client.connect(self.broker, self.port, self.keepalive)
        self.client.loop_start()
        print(f"Reconnected to MQTT broker: {self.broker}:{self.port}")
    
    def update_broker(self, broker, port=1883):
        self.broker = broker
        self.port = port

    def publish_rack_data(self):
        """发布每个机柜的功率数据"""
        for rack in self.racks:
            try:
                topic, payload = rack.get_power_payload()
                payload_str = json.dumps(payload)
                result = self.client.publish(topic, payload_str)
                if result.rc == 0:
                    print(f"MQTT成功发布机柜 {rack.rack_id} 数据到 {topic}")
                else:
                    print(f"机柜 {rack.rack_id} 发布失败，返回码 {result.rc}")
            except Exception as e:
                print(f"发布机柜 {rack.rack_id} 数据时出错: {e}")

    def publish_total_data(self):
        """发布总功率数据"""
        payload = self.power_aggregator.compute_total_it_load()
        payload_str = json.dumps(payload)
        result = self.client.publish(self.total_topic, payload_str)
        if result.rc == 0:
            pass
            # print(f"MQTT成功发布总功率数据到 {self.total_topic}")
        else:
            print(f"总功率发布失败，返回码 {result.rc}")

    def publish_loop(self, config={}):
        self._reconnect()
        try:
            while True:
                if self._reconnect_flag.is_set():
                    self._reconnect_flag.clear()
                    self._reconnect()

                self.publish_total_data()
                self.publish_rack_data()
                time.sleep(config["SERVER_UPDATE_INTERNAL"])
        except KeyboardInterrupt:
            print("Publishing stopped by user")
    
    def start(self, config={}):
        self.connect()
        self.publish_loop(config=config)
        self.disconnect()

# if __name__ == "__main__":
#     rack_ids = ["Rack-A01", "Rack-A02", "Rack-A03", "Rack-A04", "Rack-A05", "Rack-A06"]
#     racks = [Rack(rid, 150) for rid in rack_ids]

#     publisher = MqttPublisher(racks)
#     publisher.connect()
#     publisher.publish_loop(update_interval=1)
#     publisher.disconnect()
