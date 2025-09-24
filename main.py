from instances import cdwp_301, chwp_201, racks, ct_301, chiller_201, crah_101, simulation_instance
from server import BacnetServer, ModbusServer, MqttPublisher, OPCUAServer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from order import ServiceOrderAPI
import threading
import asyncio
import os
import random
import time
import redis
import psycopg2
from celery_tasks import celery
from celery.result import AsyncResult
from devices import *

CONFIG = {
    "SERVER_UPDATE_INTERNAL": 5,
    "RANDOM_UPDATE_INTERVAL": 5
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
mqtt_publisher = MqttPublisher(racks, broker="localhost", port=1883, keepalive=60)
order_api = ServiceOrderAPI(db_config, CONFIG, mqtt_publisher)

async def main():
    scheduler = AsyncIOScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(clean_all, 'cron',hour=0, minute=0)  # 每天 0 点执行
    scheduler.start()

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
                # 随机上下浮动 ±2%
                    delta = value * 0.02
                    new_value = value + random.uniform(-delta, delta)
                    obj.update_value(new_value, key)
            # print(f"{obj.__class__.__name__} updated")
            time.sleep(config["RANDOM_UPDATE_INTERVAL"])
    
    t =threading.Thread(target=updater, daemon=True)
    t.start()
    return t

def clean_all():
    if order_api.latest_task_id:
        previous_task = AsyncResult(order_api.latest_task_id, app=celery)
        # 只有当任务还在执行中才 revoke
        if previous_task.state not in ('SUCCESS', 'FAILURE', 'REVOKED'):
            previous_task.revoke(terminate=True)
    
    r = redis.Redis(host='localhost', port=6379)
    r.flushall()  # Clear all DBs in this Redis instance

    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public';
    """)
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        cur.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')

    cur.close()
    conn.close()
    simulation_instance.cdwp_301 = Pump("Running", 150.5, 3.2, 22.7)
    simulation_instance.chwp_201 = Pump("Running", 120.8, 4.1, 35.2)
    rack_ids = ["Rack-A01", "Rack-A02", "Rack-A03", "Rack-A04", "Rack-A05", "Rack-A06"]
    simulation_instance.racks = [Rack(rid, 150) for rid in rack_ids]
    simulation_instance.ct_301 = CoolingTower("running", 28.5, 24.0, 29.5, 85.0, 92.1)
    simulation_instance.chiller_201 = Chiller(24.0, 29.5, 1250, "running", 7.0, 12.1, 450, 88.5, 250.6)
    simulation_instance.crah_101 = Crah("running", 32.5, 21.0, 78.0, 90.0)
    simulation_instance.power_aggregator = Power_aggregator(racks)

if __name__ == "__main__":
    asyncio.run(main())
