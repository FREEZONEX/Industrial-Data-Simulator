from instances import cdwp_301, chwp_201, racks, ct_301, chiller_201, crah_101
from server import BacnetServer, ModbusServer, MqttPublisher, OPCUAServer
# from order import WorkOrderMonitor, ServiceOrderAPI
from order import ServiceOrderAPI
import threading
import asyncio
import os
import random
import time

CONFIG = {
    "SERVER_UPDATE_INTERNAL": 0.1,
    "RANDOM_UPDATE_INTERVAL": 0.1
}

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'dbname': os.getenv('DB_NAME', 'mydatabase'),
    'user': os.getenv('DB_USER', 'myuser'),
    'password': os.getenv('DB_PASSWORD', 'mypassword')
}

bacnet_device = BacnetServer(crah_101, deviceId=1234, port=47808, config=CONFIG)
modbus_server = ModbusServer(ct_301, chiller_201, address=("0.0.0.0", 5020), config=CONFIG)
opcua_server = OPCUAServer(endpoint="opc.tcp://0.0.0.0:4840/")
opcua_server.add_pump("CDWP-301", cdwp_301)
opcua_server.add_pump("CHWP-201", chwp_201)
mqtt_publisher = MqttPublisher(racks, broker=os.getenv("MQTT_BROKER", "localhost"), port=int(os.getenv("MQTT_PORT", 1883)), keepalive=60)
order_api = ServiceOrderAPI(db_config, CONFIG)

async def main():
    order_api.subscribe_config()
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
            for key, value in obj.__dict__.items():
                if isinstance(value, (int, float)):
                # 随机上下浮动 ±1%
                    delta = value * 0.02
                    new_value = value + random.uniform(-delta, delta)
                    obj.update_value(new_value, key)
            print(f"{obj.__class__.__name__} updated")
            time.sleep(config["RANDOM_UPDATE_INTERVAL"])
    
    t =threading.Thread(target=updater, daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    asyncio.run(main())
