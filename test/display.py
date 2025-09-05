IP = "192.168.151.133"

from pymodbus.client import ModbusTcpClient
import paho.mqtt.client as mqtt
from opcua import Client
import BAC0
import asyncio
import netifaces
import struct
import time
import threading
import queue
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import defaultdict

modbus_queue = queue.Queue()
bacnet_queue = queue.Queue()
mqtt_queue = queue.Queue()
opcua_queue = queue.Queue()

# 数据缓存
crah_timestamps = []
crah_supply_air_temp = []
crah_return_air_temp = []
crah_chilled_water_valve_position = []
crah_fan_speed = []
modbus_timestamps = []
modbus_device1 = {
    "tower_top_air_temp": [],
    "tower_basin_temp": [],
    "entering_water_temp": [],
    "fan_speed": [],
    "basin_water_level": []
}
modbus_device2 = {
    "condenser_entering_water_temp": [],
    "condenser_leaving_water_temp": [],
    "refrigerant_condensing_pressure": [],
    "chilled_water_leaving_temp": [],
    "chilled_water_entering_temp": [],
    "refrigerant_evaporating_pressure": [],
    "compressor_load": [],
    "total_power_consumption": []
}
opcua_timestamps_dict = defaultdict(list)
opcua_data_dict = defaultdict(list)
mqtt_timestamps_dict = defaultdict(list)
mqtt_data_dict = defaultdict(list)

def display_queues():
    while True:
        # 处理 Modbus 队列
        while not modbus_queue.empty():
            data = modbus_queue.get()
            ts = data["timestamp"]
            modbus_timestamps.append(ts)

            dev1 = data["device1"]
            dev2 = data["device2"]

            for k in modbus_device1.keys():
                modbus_device1[k].append(dev1[k])
            for k in modbus_device2.keys():
                modbus_device2[k].append(dev2[k])
            # print("[MODBUS]", data)

        # 处理 BACnet 队列
        while not bacnet_queue.empty():
            data = bacnet_queue.get()
            ts = data["timestamp"]
            crah_timestamps.append(ts)
            crah_supply_air_temp.append(data["supply_air_temp"])
            crah_return_air_temp.append(data["return_air_temp"])
            crah_chilled_water_valve_position.append(data["chilled_water_valve_position"])
            crah_fan_speed.append(data["fan_speed"])
            # print("[BACNET]", data)

        # 处理 MQTT 队列
        while not mqtt_queue.empty():
            data = mqtt_queue.get()
            # print("[MQTT]", data)
            ts = data.get("timestamp")
            if ts is None:
                continue
            for key, value in data.items():
                if key != "timestamp":
                    mqtt_timestamps_dict[key].append(ts)
                    mqtt_data_dict[key].append(value)

            # 处理 OPCUA 队列
            while not opcua_queue.empty():
                data = opcua_queue.get()
                # print("[OPCUA]", data)
                ts = data.get("timestamp")
                if ts is None:
                    continue
                
                # 遍历所有 key/value
                for key, value in data.items():
                    if key != "timestamp":
                        opcua_timestamps_dict[key].append(ts)
                        opcua_data_dict[key].append(value)

        time.sleep(1)  # 每秒刷新一次

# 启动显示线程
t_display = threading.Thread(target=display_queues, daemon=True)
t_display.start()

fig, axes = plt.subplots(3, 2, figsize=(10, 15))
ax1 = axes[0, 0]
ax2 = axes[0, 1]
ax3 = axes[1, 0]
ax4 = axes[1, 1]
ax5 = axes[2, 0]
def animate(i):
    ax1.cla()  # clear axis
    ax1.plot(crah_timestamps, crah_supply_air_temp, label="CRAH Supply Air Temp")
    ax1.plot(crah_timestamps, crah_return_air_temp, label="CRAH Return Air Temp")
    ax1.plot(crah_timestamps, crah_chilled_water_valve_position, label="CRAH CHW Valve Position")
    ax1.plot(crah_timestamps, crah_fan_speed, label="CRAH Fan Speed")
    ax1.set_xlabel("Timestamp")
    ax1.set_ylabel("Values")
    ax1.legend(loc="upper right")
    ax1.set_title("CRAH Data")

    ax2.cla()
    ax2.plot(modbus_timestamps, modbus_device1["tower_top_air_temp"], label="CT301 tower top air temp")
    ax2.plot(modbus_timestamps, modbus_device1["tower_basin_temp"], label="CT301 tower basin temp")
    ax2.plot(modbus_timestamps, modbus_device1["entering_water_temp"], label="CT301 entering water temp")
    ax2.plot(modbus_timestamps, modbus_device1["fan_speed"], label="CT301 fan speed")
    ax2.plot(modbus_timestamps, modbus_device1["basin_water_level"], label="CT301 basin water level")
    ax2.set_xlabel("Timestamp")
    ax2.set_ylabel("Values")
    ax2.legend(loc="upper right")
    ax2.set_title("CT301 Data")

    ax3.cla()
    ax3.plot(modbus_timestamps, modbus_device2["chilled_water_entering_temp"], label="chilled water i temp")
    ax3.plot(modbus_timestamps, modbus_device2["chilled_water_leaving_temp"], label="chilled water o temp")
    ax3.plot(modbus_timestamps, modbus_device2["compressor_load"], label="compressor load")
    ax3.plot(modbus_timestamps, modbus_device2["condenser_entering_water_temp"], label="condenser water i temp")
    ax3.plot(modbus_timestamps, modbus_device2["condenser_leaving_water_temp"], label="condenser water o temp")
    # ax3.plot(modbus_timestamps, modbus_device2["refrigerant_condensing_pressure"], label="RC pressure")
    # ax3.plot(modbus_timestamps, modbus_device2["refrigerant_evaporating_pressure"], label="RE pressure")
    ax3.plot(modbus_timestamps, modbus_device2["total_power_consumption"], label="total power consumption")
    ax3.set_xlabel("Timestamp")
    ax3.set_ylabel("Values")
    ax3.legend(loc="upper right")
    ax3.set_title("Chiller201 data")

    ax4.cla()
    for key in opcua_data_dict:
        if "state" not in key:
            ax4.plot(opcua_timestamps_dict[key], opcua_data_dict[key], label=key)  # 保持长度对应
    ax4.set_xlabel("Timestamp")
    ax4.set_ylabel("Values")
    ax4.legend(loc="upper right")
    ax4.set_title("OPC UA Data")

    ax5.cla()
    for key in sorted(mqtt_data_dict.keys()):
        ax5.plot(mqtt_timestamps_dict[key], mqtt_data_dict[key], label=key)
    ax5.set_xlabel("Timestamp")
    ax5.set_ylabel("Values")
    ax5.legend(loc="upper right")
    ax5.set_title("MQTT Data")

    plt.tight_layout()


def regs_to_float(regs, byteorder=">"):
    if len(regs) != 2:
        raise ValueError("Float conversion requires exactly 2 registers")
    packed = struct.pack(f'{byteorder}HH', *regs)
    return struct.unpack(f'{byteorder}f', packed)[0]

def regs_to_str(regs):
    b = bytearray()
    for reg in regs:
        b.append((reg >> 8) & 0xFF)
        b.append(reg & 0xFF)
    return b.rstrip(b'\x00').decode("ascii")

addresses2 = {
            "condenser_entering_water_temp": 0,
            "condenser_leaving_water_temp": 2,
            "refrigerant_condensing_pressure": 4,
            "state": 6,
            "chilled_water_leaving_temp": 10,
            "chilled_water_entering_temp": 12,
            "refrigerant_evaporating_pressure": 14,
            "compressor_load": 16,
            "total_power_consumption": 18}
addresses1 = {
            "state": 0,
            "tower_top_air_temp": 4,
            "tower_basin_temp": 6,
            "entering_water_temp": 8,
            "fan_speed": 10,
            "basin_water_level": 12}

def get_modbus_data(client, addresses, n):
    device2_data = {}
    for field, addr in addresses.items():
        # state占4寄存器，float占2寄存器
        count = 4 if field == "state" else 2
        result = client.read_holding_registers(address=addr, count=count, device_id=n)
        if not result.isError():
            regs = result.registers
            if field == "state":
                device2_data[field] = regs_to_str(regs)
            else:
                device2_data[field] = regs_to_float(regs)
        else:
            print(f"Read error at {field}: {result}")

    return device2_data

def read_loop():
    client = ModbusTcpClient(IP, port=5020)
    client.connect()
    try:
        while True:
            device1_data = get_modbus_data(client, addresses1, 1)
            device2_data = get_modbus_data(client, addresses2, 2)
            # --- 放入队列 ---
            timestamp = time.time()
            modbus_queue.put({
                "timestamp": timestamp,
                "device1": device1_data,
                "device2": device2_data
            })
            # print("Device 2 data")
            # for k, v in device2_data.items(): 
            #     print(f"{k}: {v}") 
            # print("Device 1 data:") 
            # for k, v in device1_data.items(): 
            #     print(f"{k}: {v}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Client stopped by user")
    finally:
        client.close()

t_modbus = threading.Thread(target=read_loop, daemon=True)
t_modbus.start()

def mqtt_loop():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("连接成功")
            # 批量订阅 Rack-A01 ~ Rack-A06
            for i in range(1, 7):
                topic = f"datacenter/Rack-A{i:02d}/edge/powerDraw"
                client.subscribe(topic)
                print(f"已订阅: {topic}")
            # 你原来的 topic 也可以一起订阅
            client.subscribe("IT/DataHall-1/kpi/totalITLoad")
        else:
            print(f"连接失败，返回码 {rc}")

    def on_message(client, userdata, msg):
        timestamp = time.time()
        data = json.loads(msg.payload.decode())
        mqtt_queue.put({
            "timestamp": timestamp,
            msg.topic: data["value"],
        })
        # print(f"收到消息: topic={msg.topic}, payload={data["value"]}")

    broker = IP
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, 1883, 60)
    client.loop_forever()

t_mqtt = threading.Thread(target=mqtt_loop, daemon=True)
t_mqtt.start()


# OPC UA server endpoint
endpoint = f"opc.tcp://{IP}:4840/"

# 连接 OPC UA 服务器
opcua_client = Client(endpoint)

def opcua_reader():
    try:
        opcua_client.connect()
        print("Connected to OPC UA Server")

        pumps = ["CDWP-301", "CHWP-201"]

        pump_nodes = {}
        
        # 获取节点
        for pump_name in pumps:
            pump_nodes[pump_name] = {
                "state": opcua_client.get_node(f"ns=2;s={pump_name}.state"),
                "flow_rate": opcua_client.get_node(f"ns=2;s={pump_name}.edge.flow_rate"),
                "discharge_pressure": opcua_client.get_node(f"ns=2;s={pump_name}.edge.discharge_pressure"),
                "power_consumption": opcua_client.get_node(f"ns=2;s={pump_name}.edge.powerconsumption"),
            }

        while True:
            for pump_name, nodes in pump_nodes.items():
                state = nodes["state"].get_value()
                flow_rate = nodes["flow_rate"].get_value()
                discharge_pressure = nodes["discharge_pressure"].get_value()
                power_consumption = nodes["power_consumption"].get_value()
                timestamp = time.time()
                opcua_queue.put({
                    "timestamp": timestamp,
                    f"{pump_name}.state": state,
                    f"{pump_name}.flow_rate": flow_rate,
                    f"{pump_name}.discharge_pressure": discharge_pressure,
                    f"{pump_name}.power_consumption": power_consumption,
                })
                # print(f"[{pump_name}] State: {state}, Flow Rate: {flow_rate}, Discharge Pressure: {discharge_pressure}, Power Consumption: {power_consumption}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("Client stopped by user")

    finally:
        opcua_client.disconnect()
        print("Disconnected from OPC UA Server")

opcua_thread = threading.Thread(target=opcua_reader, daemon=True)
opcua_thread.start()

def get_local_ip_cidr():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                netmask = addr.get('netmask', '255.255.255.0')
                if ip.startswith("127."):
                    continue
                cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
                return f"{ip}/{cidr}"
    return None

async def read_bacnet():
    bacnet = BAC0.connect(ip=f"{get_local_ip_cidr()}:50000")

    try:
        while True:
            return_air_temp = await bacnet.read(f'{IP} analogInput 0 presentValue')
            supply_air_temp = await bacnet.read(f'{IP} analogInput 1 presentValue')
            chilled_water_valve_position = await bacnet.read(f'{IP} analogInput 2 presentValue')
            fan_speed = await bacnet.read(f'{IP} analogInput 3 presentValue')
            status = await bacnet.read(f'{IP} characterstringValue 0 presentValue')
            timestamp = time.time()
            bacnet_queue.put({
                "timestamp": timestamp,
                "supply_air_temp": supply_air_temp,
                "return_air_temp": return_air_temp,
                "chilled_water_valve_position": chilled_water_valve_position,
                "fan_speed": fan_speed
            })
            # print(f'The present value is: {return_air_temp} {supply_air_temp} {chilled_water_valve_position} {fan_speed} {status}')
            await asyncio.sleep(5)  # 每5秒读取一次
    except KeyboardInterrupt:
        print("Stopping read loop...")
    finally:
        bacnet.disconnect()

def bacnet_loop():
    asyncio.run(read_bacnet())

bacnet_thread = threading.Thread(target=bacnet_loop, daemon=True)
bacnet_thread.start()

ani = animation.FuncAnimation(fig, animate, interval=1000)  # 1秒刷新一次
plt.show()
