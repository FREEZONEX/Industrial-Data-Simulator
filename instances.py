from simulation import Simulation
from devices import Crah, Chiller, CoolingTower, Power_aggregator, Pump, Rack


cdwp_301 = Pump("Running", 150.5, 3.2, 22.7)
chwp_201 = Pump("Running", 120.8, 4.1, 35.2)
rack_ids = ["Rack-A01", "Rack-A02", "Rack-A03", "Rack-A04", "Rack-A05", "Rack-A06"]
racks = [Rack(rid, 150) for rid in rack_ids]
ct_301 = CoolingTower("running", 28.5, 24.0, 29.5, 85.0, 92.1)
chiller_201 = Chiller(24.0, 29.5, 1250, "running", 7.0, 12.1, 450, 88.5, 250.6)
crah_101 = Crah("running", 32.5, 21.0, 78.0, 90.0)
power_aggregator = Power_aggregator(racks)
simulation_instance = Simulation(crah_101, chiller_201, ct_301, cdwp_301, chwp_201, racks, power_aggregator)

# import redis
# import json
# r = redis.Redis(host="localhost", port=6379, db=2, decode_responses=True)
# config = {
#     "crah_101": {
#         "return_air_temp": crah_101.return_air_temp,
#         "supply_air_temp": crah_101.supply_air_temp,
#         "fan_speed": crah_101.fan_speed,
#         "chilled_water_valve_position": crah_101.chilled_water_valve_position
#     },
#     "chiller_201": {
#         "chilled_water_leaving_temp": chiller_201.chilled_water_leaving_temp,
#         "chilled_water_entering_temp": chiller_201.chilled_water_entering_temp,
#         "compressor_load": chiller_201.compressor_load,
#         "total_power_consumption": chiller_201.total_power_consumption
#     },
#     "ct_301": {
#         "fan_speed": ct_301.fan_speed,
#         "tower_basin_temp": ct_301.tower_basin_temp,
#         "entering_water_temp": ct_301.entering_water_temp
#     },
#     "cdwp_301": {},
#     "chwp_201": {},
#     "power_aggregator": {
#         "total": power_aggregator.total
#     }
# }
# r.lpush("simulation_config", json.dumps(config))
# print("config pushed")

# import matplotlib.pyplot as plt
# # ==== 数据收集 ====
# times, returnAirTemps, supplyAirTemps, fanSpeeds, valvePos, compLoads = [], [], [], [], [], []
# towerBasinTemps, towerTopAirTemps, ctFanSpeeds = [], [], []
# chilledWaterEnteringTemps, chilledWaterLeavingTemps = [], []

# payload = {
#     "customer_id": "CUST-123",
#     "requested_resources": {
#         "cpu_cores": 0,
#         "memory_gb": 0,
#         "storage_tb": 0
#     },
#     "duration_months": 12
# }
# simulation_instance.power_allocate(request=payload.get("requested_resources", {}))
# env = simulation_instance.simulate()

# def collect_data():
#     times.append(env.now)
#     returnAirTemps.append(crah_101.return_air_temp)
#     supplyAirTemps.append(crah_101.supply_air_temp)
#     fanSpeeds.append(crah_101.fan_speed)
#     valvePos.append(crah_101.chilled_water_valve_position)
#     compLoads.append(chiller_201.compressor_load)
#     towerBasinTemps.append(ct_301.tower_basin_temp)
#     towerTopAirTemps.append(ct_301.tower_top_air_temp)
#     ctFanSpeeds.append(ct_301.fan_speed)
#     chilledWaterEnteringTemps.append(chiller_201.chilled_water_entering_temp)
#     chilledWaterLeavingTemps.append(chiller_201.chilled_water_leaving_temp)

# # ==== 绘图初始化 ====  
# plt.ion()
# fig, axes = plt.subplots(5,1,figsize=(12,12), sharex=True)

# while env.now < 360:
#     simulation_instance._pop_config()
#     env.step()
#     simulation_instance._push_config()
#     collect_data()

#     if env.now % 1 == 0:
#         axes[0].clear()
#         axes[0].plot(times, returnAirTemps, label="CRAH ReturnAirTemp")
#         axes[0].plot(times, supplyAirTemps, label="CRAH SupplyAirTemp")
#         axes[0].set_ylabel("°C"); axes[0].legend(); axes[0].grid(True)

#         axes[1].clear()
#         axes[1].plot(times, fanSpeeds, label="CRAH FanSpeed (%)")
#         axes[1].plot(times, valvePos, label="CRAH ValvePos (%)")
#         axes[1].set_ylabel("Control (%)"); axes[1].legend(); axes[1].grid(True)

#         axes[2].clear()
#         axes[2].plot(times, compLoads, label="Chiller CompressorLoad (%)")
#         axes[2].set_ylabel("Compressor (%)"); axes[2].legend(); axes[2].grid(True)

#         axes[3].clear()
#         axes[3].plot(times, towerBasinTemps, label="CoolingTower BasinTemp")
#         axes[3].plot(times, towerTopAirTemps, label="CoolingTower TopAirTemp")
#         axes[3].plot(times, ctFanSpeeds, label="CoolingTower FanSpeed (%)")
#         axes[3].set_ylabel("°C / %"); axes[3].legend(); axes[3].grid(True)

#         axes[4].clear()
#         axes[4].plot(times, chilledWaterEnteringTemps, label="ChilledWater EnteringTemp")
#         axes[4].plot(times, chilledWaterLeavingTemps, label="ChilledWater LeavingTemp")
#         axes[4].set_ylabel("°C"); axes[4].set_xlabel("Time (s)")
#         axes[4].legend(); axes[4].grid(True)

#         plt.tight_layout()
#         plt.pause(0.01)

# plt.ioff()
# plt.show()