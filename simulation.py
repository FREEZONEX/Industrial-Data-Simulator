from devices import Crah, Chiller, CoolingTower, Power_aggregator, Pump, Server_rack, Cmms
import heapq
from modbus_slave import ModbusServer
from opc_ua_server import PumpOPCUAServer
from bacnet_server import CrahDevice
from mqtt import MqttPublisher

class simulation:
    def __init__(self, request, crah_101: Crah, chiller_201: Chiller, ct_301: CoolingTower, 
                 cdwp_301: Pump, chwp_201: Pump, cmms: Cmms, racks: list[Server_rack]):
        self.request = request
        self.crah_101 = crah_101
        self.chiller_201 = chiller_201
        self.ct_301 = ct_301
        self.cdwp_301 = cdwp_301
        self.chwp_201 = chwp_201
        self.cmms = cmms
        self.racks = racks
        self.power_aggregator = Power_aggregator(self.racks)

    def simulate(self):  # 仿真流程
        pass

    def power_allocate(self):  # 电力负载分配
        cpu_cores = self.request.get("cpu_cores", 0)
        memory_gb = self.request.get("memory_gb", 0)
        storage_tb = self.request.get("storage_tb", 0)

        total_load = cpu_cores * 25 + memory_gb * 0.5 + storage_tb * 5
        if not self.racks or total_load == 0:
            return
        
        heap = [(rack.get_load(), rack) for rack in self.racks]
        heapq.heapify(heap)

        _, rack = heapq.heappop(heap)
        rack.add_load(total_load)
