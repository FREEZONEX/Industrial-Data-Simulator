from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext, ModbusSequentialDataBlock
from devices import Chiller, CoolingTower
import asyncio

class ModbusServer:
    def __init__(self, ct301: CoolingTower, chiller201:Chiller, address=("0.0.0.0", 5020), update_interval=10):
        self.address = address
        self.update_interval = update_interval

        # 初始化设备
        self.ct301 = ct301
        self.chiller201 = chiller201
        self.context = self._create_context()

    def _create_context(self):
        datablock_ct301 = ModbusSequentialDataBlock(0, [0]*100)
        datablock_chiller = ModbusSequentialDataBlock(0, [0]*100)

        ct_301 = ModbusDeviceContext(di=datablock_ct301, co=datablock_ct301, hr=datablock_ct301, ir=datablock_ct301)
        chiller_201 = ModbusDeviceContext(di=datablock_chiller, co=datablock_chiller, hr=datablock_chiller, ir=datablock_chiller)

        return ModbusServerContext(
            devices={1: ct_301, 2: chiller_201},
            single=False
        )

    async def _update_context_loop(self):
        while True:
            self.ct301.store_all(self.context, 1)
            self.chiller201.store_all(self.context, 2)
            print("Modbus_Slave Context Updated.")
            await asyncio.sleep(self.update_interval)

    async def start(self):
        """启动 Modbus 服务器"""
        asyncio.create_task(self._update_context_loop())
        await StartAsyncTcpServer(context=self.context, address=self.address)


# if __name__ == "__main__":
#     try:
#         server = ModbusServer(address=("0.0.0.0", 5020), update_interval=10)
#         asyncio.run(server.start())
#     except KeyboardInterrupt:
#         print("Server stopped by user.")