import struct
import threading

class ModbusDevice:
    def __init__(self, field_values, field_addresses):
        """
        :param context: Modbus device context
        :param field_values: dict of field_name -> initial value
        :param field_addresses: dict of field_name -> modbus address
        :param context_index: which context in self.context to use
        """
        self.field_addresses = field_addresses
        # 初始化属性
        for key, val in field_values.items():
            setattr(self, key, val)

    def _float_to_regs(self, value, byteorder=">"):
        packed = struct.pack(f'{byteorder}f', value)
        return list(struct.unpack(f'{byteorder}HH', packed))
    
    def _str_to_regs(self, text: str, max_regs=4):
        b = text.encode("ascii")
        if len(b) % 2 == 1:
            b += b'\x00'
        regs = [(b[i] << 8) | b[i+1] for i in range(0, len(b), 2)]
        if max_regs is not None:
            regs = regs[:max_regs]
        return regs    

    def _store_value(self, context, context_index, address, value):
        if isinstance(value, float):
            regs = self._float_to_regs(value)
        elif isinstance(value, int):
            regs = [value]
        elif isinstance(value, str):
            regs = self._str_to_regs(value)
        else:
            raise TypeError(f"Unsupported type: {type(value)}")
        context[context_index].setValues(3, address, regs)

    def store_all(self, context, context_index):
        for key, addr in self.field_addresses.items():
            self._store_value(context, context_index, addr, getattr(self, key))

    def store(self, context, context_index, key):
        if key in self.field_addresses:
            self._store_value(context, context_index, self.field_addresses[key], getattr(self, key))

    def update_value(self, value, key):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"No such key: {key}")


# 冷水机组
class Chiller(ModbusDevice):
    def __init__(self, condenser_entering_water_temp, condenser_leaving_water_temp, 
                 refrigerant_condensing_pressure, state, chilled_water_leaving_temp, chilled_water_entering_temp, 
                 refrigerant_evaporating_pressure, compressor_load, total_power_consumption):
        
        fields = {
            "condenser_entering_water_temp": condenser_entering_water_temp,
            "condenser_leaving_water_temp": condenser_leaving_water_temp,
            "refrigerant_condensing_pressure": refrigerant_condensing_pressure,
            "state": state,
            "chilled_water_leaving_temp": chilled_water_leaving_temp,
            "chilled_water_entering_temp": chilled_water_entering_temp,
            "refrigerant_evaporating_pressure": refrigerant_evaporating_pressure,
            "compressor_load": compressor_load,
            "total_power_consumption": total_power_consumption
        }
        addresses = {
            "condenser_entering_water_temp": 0,
            "condenser_leaving_water_temp": 2,
            "refrigerant_condensing_pressure": 4,
            "state": 6,
            "chilled_water_leaving_temp": 10,
            "chilled_water_entering_temp": 12,
            "refrigerant_evaporating_pressure": 14,
            "compressor_load": 16,
            "total_power_consumption": 18
        }
        super().__init__(fields, addresses)
        self._lock = threading.Lock()


# 冷却塔
class CoolingTower(ModbusDevice):
    def __init__(self, state, tower_top_air_temp, tower_basin_temp, entering_water_temp, fan_speed, basin_water_level):
        fields = {
            "state": state,
            "tower_top_air_temp": tower_top_air_temp,
            "tower_basin_temp": tower_basin_temp,
            "entering_water_temp": entering_water_temp,
            "fan_speed": fan_speed,
            "basin_water_level": basin_water_level
        }
        addresses = {
            "state": 0,
            "tower_top_air_temp": 4,
            "tower_basin_temp": 6,
            "entering_water_temp": 8,
            "fan_speed": 10,
            "basin_water_level": 12
        }
        super().__init__(fields, addresses)
        self._lock = threading.Lock()


# 冷凝水泵
class Pump:
    def __init__(self, state, flow_rate, discharge_pressure, power_consumption):
        self.state = state
        self.flow_rate = flow_rate
        self.discharge_pressure = discharge_pressure
        self.power_consumption = power_consumption
        self._lock = threading.Lock()

    def update_value(self, value, key):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"No such key: {key}")
        
    def get_value(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        
    def report(self):
        return{
            "state": self.state,
            "flow_rate": self.flow_rate,
            "discharge_pressure": self.discharge_pressure,
            "power_consumption": self.power_consumption,      
        }

# 机房空气处理器
class Crah:
    def __init__(self, state, return_air_temp, supply_air_temp, chilled_water_value_position, fan_speed):
        self.state = state
        self.return_air_temp = return_air_temp
        self.supply_air_temp = supply_air_temp
        self.chilled_water_valve_position = chilled_water_value_position
        self.fan_speed = fan_speed
        self._lock = threading.Lock()

    def update_value(self, value, key):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"No such key: {key}")
        
    def get_value(self, key):
        if hasattr(self, key):
            return getattr(self, key)

    def report(self):
        return{
            "state": self.state,
            "return_air_temp": self.return_air_temp,
            "supply_air_temp": self.supply_air_temp,
            "chilled_water_valve_position": self.chilled_water_valve_position,
            "fan_speed": self.fan_speed      
        }

# 单服务器机柜
class Rack:
    def __init__(self, rack_id: str, power_draw_kw: float):
        self.rack_id = rack_id
        self.power_draw_kw = power_draw_kw
        self._lock = threading.Lock()

    def get_power_payload(self) -> dict:
        topic = f"datacenter/{self.rack_id}/edge/powerDraw"
        payload = {
            "value": self.power_draw_kw,
            "unit": "kW"
        }
        return topic, payload
    
    def set_load(self, value):
        self.power_draw_kw = value

    def add_load(self, value):
        self.power_draw_kw += value

    def get_load(self):
        return self.power_draw_kw
    
    def update_value(self, value, key):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"No such key: {key}")

# 所有服务器机柜
class Power_aggregator:
    def __init__(self, racks: list[Rack]):
        self.racks = racks

    def compute_total_it_load(self) -> dict:
        self.total = sum(rack.power_draw_kw for rack in self.racks)
        topic = "IT/DataHall-1/kpi/totalITLoad"
        payload = {
            "value": round(self.total, 2),
            "unit": "kW"
        }
        return topic, payload

class Runtime:
    def __init__(self, ct301=0, cdwp301=0, chiller201=0, racks=0, chwp201=0, crah101=0):
        self.ct301 = ct301
        self.cdwp301 = cdwp301
        self.chiller201 = chiller201
        self.racks = racks
        self.chwp201=chwp201
        self.crah101 = crah101

    def get_value(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(f"No such key: {key}")
        
    def set_value(self, value, key):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"No such key: {key}")
        
    def add_value(self, value, key):
        if hasattr(self, key):
            setattr(self, key, getattr(self, key) + value)
        else:
            raise KeyError(f"No such key: {key}")
