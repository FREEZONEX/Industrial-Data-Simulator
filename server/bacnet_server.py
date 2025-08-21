import asyncio
import BAC0
from devices import Crah
from BAC0.core.devices.local.factory import (
    analog_input, binary_output, multistate_value, character_string, make_state_text,
)

class BacnetServer:
    def __init__(self, crah: Crah, deviceId=1234, port=47808, localObjName="MyDevice", update_interval=10):
        self.crah = crah
        self.deviceId = deviceId
        self.port = port
        self.localObjName = localObjName
        self.update_interval = update_interval

        self.state = character_string(name="state", description="Current operating status")
        self.return_air_temp = analog_input(name="return_air_temp", description="The temperature of the air returning", properties={"units": "degreesCelsius"})
        self.supply_air_temp = analog_input(name="supply_air_temp", description="The temperature of the air supplied", properties={"units": "degreesCelsius"})
        self.chilled_water_valve_position = analog_input(name="chilled_water_valve_position", description="The opening position of the chilled water valve as a percentage", properties={"units": "percent"})
        self.fan_speed = analog_input(name="fan_speed", description="The current speed of the fan as a percentage", properties={"units": "percent"})

    async def run(self):
        async with BAC0.lite(deviceId=self.deviceId, port=self.port, localObjName=self.localObjName) as dev:
            self.state.add_objects_to_application(dev)
            self.return_air_temp.add_objects_to_application(dev)
            self.supply_air_temp.add_objects_to_application(dev)
            self.chilled_water_valve_position.add_objects_to_application(dev)
            self.fan_speed.add_objects_to_application(dev)

            while True:
                # 轮询Crah对象数据，更新BACnet点值
                dev["state"].presentValue = self.crah.get_value("state")
                dev["return_air_temp"].presentValue = self.crah.get_value("return_air_temp")
                dev["supply_air_temp"].presentValue = self.crah.get_value("supply_air_temp")
                dev["chilled_water_valve_position"].presentValue = self.crah.get_value("chilled_water_valve_position")
                dev["fan_speed"].presentValue = self.crah.get_value("fan_speed")
                print("更新BACnet点值")
                await asyncio.sleep(self.update_interval)
            
    async def start(self):
        await self.run()

# async def main():
#     crah_101 = Crah("running", 32.5, 21.0, 78.0, 90.0)
#     device = BacnetServer(crah_101)
#     await device.run()

# asyncio.run(main())
