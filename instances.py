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
