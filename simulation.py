from devices import Crah, Chiller, CoolingTower, Power_aggregator, Pump, Rack
import heapq
from server import ModbusServer, OPCUAServer, BacnetServer, MqttPublisher
import math
from datetime import datetime

class simulation:
    def __init__(self, crah_101: Crah, chiller_201: Chiller, ct_301: CoolingTower,
                 cdwp_301: Pump, chwp_201: Pump, racks: list[Rack]):
        self.crah_101 = crah_101
        self.chiller_201 = chiller_201
        self.ct_301 = ct_301
        self.cdwp_301 = cdwp_301
        self.chwp_201 = chwp_201
        self.racks = racks
        self.power_aggregator = Power_aggregator(self.racks)

    def simulate(self):  # 仿真流程
        self._power_allocate

    def _power_allocate(self, request):  # 电力负载分配
        cpu_cores = request.get("cpu_cores", 0)
        memory_gb = request.get("memory_gb", 0)
        storage_tb = request.get("storage_tb", 0)

        total_load = cpu_cores * 25 + memory_gb * 0.5 + storage_tb * 5
        if not self.racks or total_load == 0:
            return
        
        heap = [(rack.get_load(), rack) for rack in self.racks]
        heapq.heapify(heap)

        _, rack = heapq.heappop(heap)
        rack.add_load(total_load)

    def _ambirnt_temp():
        base_temp = 30
        amplitude = 2
        period = 24 * 3600
        peak_hour = 14

        phi = math.pi/2 - 2 * math.pi *(peak_hour * 3600) / period

        now = datetime.now()
        t = now.hour * 3600 + now.minute * 60 + now.second
            
        temp = base_temp + amplitude * math.sin(2 * math.pi * t / period + phi)
        return temp

cdwp_301 = Pump("Running", 150.5, 3.2, 22.7)
chwp_201 = Pump("Running", 120.8, 4.1, 35.2)

rack_ids = ["Rack-A01", "Rack-A02", "Rack-A03", "Rack-A04", "Rack-A05", "Rack-A06"]
racks = [Rack(rid, 150) for rid in rack_ids]

ct_301 = CoolingTower("running", 28.5, 24.0, 29.5, 85.0, 92.1)
chiller_201 = Chiller(24.0, 29.5, 1250, "running", 7.0, 12.1, 450, 88.5, 250.6)

crah_101 = Crah("running", 32.5, 21.0, 78.0, 90.0)

simul = simulation(crah_101, chiller_201, ct_301, cdwp_301, chwp_201, racks)
