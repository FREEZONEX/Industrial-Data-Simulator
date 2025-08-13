from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext, ModbusSequentialDataBlock
from devices import Chiller, CoolingTower
import asyncio

class ModbusServer:
    def __init__(self, address=("0.0.0.0", 5020), update_interval=10, ct301=None, chiller201=None):
        self.address = address
        self.update_interval = update_interval
        self.context = self._create_context()
        self.ct301 = ct301 or CoolingTower(self.context, "running", 28.5, 24.0, 29.5, 85.0, 92.1)
        self.chiller201 = chiller201 or Chiller(self.context, 24.0, 29.5, 1250, "running", 7.0, 12.1, 450, 88.5, 250.6)

    def _create_context(self):
        datablock_ct301 = ModbusSequentialDataBlock.create()
        datablock_chiller = ModbusSequentialDataBlock.create()

        ct_301 = ModbusDeviceContext(di=datablock_ct301, co=datablock_ct301, hr=datablock_ct301, ir=datablock_ct301)
        chiller_201 = ModbusDeviceContext(di=datablock_chiller, co=datablock_chiller, hr=datablock_chiller, ir=datablock_chiller)

        return ModbusServerContext(
            devices={
                1: ct_301,
                2: chiller_201
            },
            single=False
        )

    async def _update_context_loop(self):
        while True:
            for field in self.ct301.field_addresses.keys():
                self.ct301.store(field)

            for field in self.chiller201.field_addresses.keys():
                self.chiller201.store(field)

            print("Context updated.")
            await asyncio.sleep(self.update_interval)

    async def start(self):
        """启动 Modbus 服务器"""
        asyncio.create_task(self._update_context_loop())
        await StartAsyncTcpServer(context=self.context, address=self.address)

if __name__ == "__main__":
    try:
        server = ModbusServer(address=("0.0.0.0", 5020), update_interval=10)
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Server stopped by user.")