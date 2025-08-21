# from pymodbus.client import ModbusTcpClient

# client = ModbusTcpClient('127.0.0.1', port=5020)
# client.connect()

# result = client.read_holding_registers(
#     address=8,
#     count=4,
#     device_id=1
# )  # 读取 Holding Register 第0位
# if not result.isError():
#     print("Read from slave:", result.registers)
# else:
#     print("Read error:", result)

# client.close()


# import netifaces
# import BAC0
# import asyncio

# def get_local_ip_cidr():
#     for iface in netifaces.interfaces():
#         addrs = netifaces.ifaddresses(iface)
#         if netifaces.AF_INET in addrs:
#             for addr in addrs[netifaces.AF_INET]:
#                 ip = addr['addr']
#                 netmask = addr.get('netmask', '255.255.255.0')
#                 if ip.startswith("127."):
#                     continue
#                 cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
#                 return f"{ip}/{cidr}"
#     return None

# async def main():
#     local_cidr = get_local_ip_cidr()
#     bacnet = BAC0.connect(ip="192.168.151.134/24:50000")

#     object_type = 'analogInput'
#     instance_number = 1
#     property_name = 'presentValue'

#     print("started")

#     # 写入设备对象属性
#     new_value = 20.0
#     # bacnet.write(f'{local_cidr} {object_type} {instance_number} {property_name} {new_value}')
#     # print("writted")

#     value1 = await bacnet.read(f'192.168.151.134 analogInput 0 presentValue')
#     value2 = await bacnet.read(f'192.168.151.134 analogInput 1 presentValue')
#     value3 = await bacnet.read(f'192.168.151.134 analogInput 2 presentValue')
#     value4 = await bacnet.read(f'192.168.151.134 analogInput 3 presentValue')
#     value5 = await bacnet.read(f'192.168.151.134 characterstringValue 0 presentValue')
#     print(f'The present value is: {value1} {value2} {value3} {value4} {value5}')

#     # 等待一会确保写操作完成
#     await asyncio.sleep(1)

#     # 断开连接
#     bacnet.disconnect()

# if __name__ == "__main__":
#     asyncio.run(main())



import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
        client.subscribe("IT/DataHall-1/kpi/totalITLoad")
    else:
        print(f"连接失败，返回码 {rc}")

def on_message(client, userdata, msg):
    print(f"收到消息: topic={msg.topic}, payload={msg.payload.decode()}")

broker = "localhost"
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, 1883, 60)

client.loop_forever()

