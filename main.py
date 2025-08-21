from devices import Crah, Chiller, CoolingTower, Power_aggregator, Pump, Rack
from server import BacnetServer, ModbusServer, MqttPublisher, OPCUAServer
from order import WorkOrderMonitor, ServiceOrderAPI
import threading
import asyncio
import os
import random
import time

CONFIG = {
    "SERVER_UPDATE_INTERNAL": 5.0,
    "RANDOM_UPDATE_INTERVAL": 10.0
}

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'dbname': os.getenv('DB_NAME', 'mydatabase'),
    'user': os.getenv('DB_USER', 'myuser'),
    'password': os.getenv('DB_PASSWORD', 'mypassword')
}

cdwp_301 = Pump("Running", 150.5, 3.2, 22.7)
chwp_201 = Pump("Running", 120.8, 4.1, 35.2)
rack_ids = ["Rack-A01", "Rack-A02", "Rack-A03", "Rack-A04", "Rack-A05", "Rack-A06"]
racks = [Rack(rid, 150) for rid in rack_ids]
ct_301 = CoolingTower("running", 28.5, 24.0, 29.5, 85.0, 92.1)
chiller_201 = Chiller(24.0, 29.5, 1250, "running", 7.0, 12.1, 450, 88.5, 250.6)
crah_101 = Crah("running", 32.5, 21.0, 78.0, 90.0)
power_aggregator = Power_aggregator(racks)

bacnet_device = BacnetServer(crah_101, deviceId=1234, port=47808, config=CONFIG)
modbus_server = ModbusServer(ct_301, chiller_201, address=("0.0.0.0", 5020), config=CONFIG)
opcua_server = OPCUAServer(endpoint="opc.tcp://0.0.0.0:4840/")
opcua_server.add_pump("CDWP-301", cdwp_301)
opcua_server.add_pump("CHWP-201", chwp_201)
mqtt_publisher = MqttPublisher(racks, broker=os.getenv("MQTT_BROKER", "localhost"), port=int(os.getenv("MQTT_PORT", 1883)), keepalive=60)

order_api = ServiceOrderAPI(db_config, CONFIG)

async def main():
    opcua_thread = threading.Thread(
        target=opcua_server.run, 
        args=(CONFIG,),
        daemon=True)
    opcua_thread.start()

    publisher_thread = publisher_thread = threading.Thread(
        target=mqtt_publisher.start, 
        args=(CONFIG,), 
        daemon=True)
    publisher_thread.start()

    order_api_thread = threading.Thread(
        target=order_api.run,
        kwargs={"host": "0.0.0.0", "port": 5000, "debug": False},
        daemon=True)
    order_api_thread.start()

    devices = [cdwp_301, chwp_201, ct_301, chiller_201, crah_101] + racks
    for dev in devices:
        random_update(dev, config=CONFIG)

    await asyncio.gather(
        bacnet_device.start(),
        modbus_server.start()
    )

def random_update(obj, config=CONFIG):
    def updater():
        while True:
            with obj._lock:
                for key, value in obj.__dict__.items():
                    if isinstance(value, (int, float)):
                    # 随机上下浮动 ±10%
                        delta = value * 0.1
                        new_value = value + random.uniform(-delta, delta)
                        obj.update_value(new_value, key)
                print(f"{obj.__class__.__name__} updated")
                time.sleep(config["RANDOM_UPDATE_INTERVAL"])
    
    t =threading.Thread(target=updater, daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    asyncio.run(main())
