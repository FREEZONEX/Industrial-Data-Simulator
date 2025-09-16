from devices import Crah, Chiller, CoolingTower, Power_aggregator, Pump, Rack
import math
from datetime import datetime
import simpy
import redis
import json
import time

class Simulation:
    def __init__(self, crah_101: Crah, chiller_201: Chiller, ct_301: CoolingTower,  
                 cdwp_301: Pump, chwp_201: Pump, racks: list[Rack], power_aggregator:Power_aggregator):
        self.crah_101 = crah_101
        self.chiller_201 = chiller_201
        self.ct_301 = ct_301
        self.cdwp_301 = cdwp_301
        self.chwp_201 = chwp_201
        self.racks = racks
        self.power_aggregator = power_aggregator
        # 仿真参数
        self.C = 1000
        self.max_cooling_capacity = 10
        self.TIME_STEP = 1
        self.mq = redis.Redis(host="localhost", port=6379, db=2, decode_responses=True)

    def simulate(self):  # 仿真流程
        self._pop_config()
        env = simpy.Environment()
        env.process(self._crah(env))
        env.process(self._chiller(env))
        env.process(self._cooling_tower(env))
        env.process(self._publish_config(env))
        env.run()

    def power_allocate(self, request):  # 电力负载分配
        cpu_cores = request.get("cpu_cores", 0)
        memory_gb = request.get("memory_gb", 0)
        storage_tb = request.get("storage_tb", 0)

        total_load = cpu_cores * 25 + memory_gb * 0.5 + storage_tb * 5
        if not self.racks or total_load == 0:
            return
        
        rack = min(self.racks, key=lambda r: r.get_load())
        rack.add_load(total_load)

    def _crah(self, env):
        while True:
            L = self.power_aggregator.total / self.C
            self.crah_101.return_air_temp = max(20, 0.5*self.crah_101.return_air_temp + 0.5*self.crah_101.supply_air_temp + L)
            if self.crah_101.return_air_temp > 33:
                self.crah_101.fan_speed = min(self.crah_101.fan_speed + 1, 100)
                self.crah_101.chilled_water_valve_position = min(self.crah_101.chilled_water_valve_position + 1, 100)
            elif self.crah_101.return_air_temp < 28:
                self.crah_101.fan_speed = max(self.crah_101.fan_speed - 1, 10)
                self.crah_101.chilled_water_valve_position = max(self.crah_101.chilled_water_valve_position - 1, 10)
            deltaT = (self.crah_101.chilled_water_valve_position / 100) * (self.crah_101.return_air_temp - self.chiller_201.chilled_water_leaving_temp)  # chilled_water_leaving_temp 是进入crah的水的温度
            self.crah_101.supply_air_temp = self.crah_101.return_air_temp - deltaT
            self.chiller_201.chilled_water_entering_temp = self.chiller_201.chilled_water_leaving_temp + deltaT  # chilled_water_entering_temp 是离开crah的水的温度
            yield env.timeout(self.TIME_STEP)

    def _chiller(self, env):
        while True:
            heat_load = self.chiller_201.chilled_water_entering_temp - 7
            req_compressor_load = heat_load / self.max_cooling_capacity
            self.chiller_201.compressor_load = min(req_compressor_load  * 100, 100)
            if req_compressor_load <= 1:
                self.chiller_201.chilled_water_leaving_temp = 7
            else:
                self.chiller_201.chilled_water_leaving_temp = 7 + self.max_cooling_capacity * (req_compressor_load - 1)
            self.chiller_201.total_power_consumption = self.chiller_201.compressor_load * 2.8
            self.chiller_201.condenser_leaving_water_temp = self.chiller_201.chilled_water_entering_temp + (self.chiller_201.chilled_water_entering_temp - self.chiller_201.chilled_water_leaving_temp)
            yield env.timeout(self.TIME_STEP)

    def _cooling_tower(self, env):
        while True:
            self.ct_301.entering_water_temp = self.chiller_201.condenser_leaving_water_temp
            self.ct_301.tower_basin_temp = self.chiller_201.condenser_leaving_water_temp*0.5 + self._ambient_temp()*0.5
            temp_diff = abs(self.ct_301.entering_water_temp - self.ct_301.tower_basin_temp)
            self.ct_301.fan_speed = min(max(temp_diff * 10, 10), 100)
            self.ct_301.tower_top_air_temp = self.ct_301.entering_water_temp + 0.1 * temp_diff
            yield env.timeout(self.TIME_STEP)

    def _pop_config(self):
        try:
            data = self.mq.lpop("simulation_config")
            if not data:
                print("no data in redis")
                return False
            cfg = json.loads(data)

            # --- 更新 CRAH ---
            for k, v in cfg.get("crah_101", {}).items():
                self.crah_101.update_value(v, k)

            # --- 更新 Chiller ---
            for k, v in cfg.get("chiller_201", {}).items():
                self.chiller_201.update_value(v, k)

            # --- 更新 CoolingTower ---
            for k, v in cfg.get("ct_301", {}).items():
                self.ct_301.update_value(v, k)
            
            # --- 更新 power_aggregator ---
            for k, v in cfg.get("power_aggregator", {}).items():
                self.power_aggregator.update_value(v, k)

        except Exception as e:
            print("update fail: ", e)
            return False

    def _publish_config(self, env):
        while True:
            config = {
                "crah_101": {
                    "return_air_temp": self.crah_101.return_air_temp,
                    "supply_air_temp": self.crah_101.supply_air_temp,
                    "fan_speed": self.crah_101.fan_speed,
                    "chilled_water_valve_position": self.crah_101.chilled_water_valve_position
                },
                "chiller_201": {
                    "chilled_water_leaving_temp": self.chiller_201.chilled_water_leaving_temp,
                    "chilled_water_entering_temp": self.chiller_201.chilled_water_entering_temp,
                    "compressor_load": self.chiller_201.compressor_load,
                    "total_power_consumption": self.chiller_201.total_power_consumption
                },
                "ct_301": {
                    "fan_speed": self.ct_301.fan_speed,
                    "tower_basin_temp": self.ct_301.tower_basin_temp,
                    "entering_water_temp": self.ct_301.entering_water_temp
                },
                "cdwp_301": {},
                "chwp_201": {},
                "power_aggregator": {
                    "total": self.power_aggregator.total
                }
            }
            self.mq.publish("simulation_step", json.dumps(config))
            yield env.timeout(self.TIME_STEP)
            time.sleep(self.TIME_STEP)

    def _ambient_temp(self):
        base_temp = 30
        amplitude = 2
        period = 24 * 3600
        peak_hour = 14

        phi = math.pi/2 - 2 * math.pi *(peak_hour * 3600) / period

        now = datetime.now()
        t = now.hour * 3600 + now.minute * 60 + now.second
            
        temp = base_temp + amplitude * math.sin(2 * math.pi * t / period + phi)
        return temp
