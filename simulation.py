from devices import Crah, Chiller, CoolingTower, Power_aggregator, Pump, Server_rack, Cmms

class simulation:
    def __init__(self, crah_101: Crah, chiller_201: Chiller, ct_301: CoolingTower, 
                 cdwp_301: Pump, chwp_201: Pump, cmms: Cmms, racks: list[Server_rack], power_aggregator: Power_aggregator):
        self.crah_101 = crah_101
        self.chiller_201 = chiller_201
        self.ct_301 = ct_301
        self.cdwp_301 = cdwp_301
        self.chwp_201 = chwp_201
        self.cmms = cmms
        self.racks = racks
        self.power_aggregator = power_aggregator

    def simulate():
        pass