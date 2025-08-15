import struct

# 冷水机组
class Chiller:
    def __init__(self, context, condenser_entering_water_temp, condenser_leaving_water_temp, refrigerant_condensing_pressure, state, 
                 chilled_water_leaving_temp, chilled_water_entering_temp, refrigerant_evaporating_pressure, compressor_load, total_power_consumption):
        
        self.context = context
        self.condenser_entering_water_temp = condenser_entering_water_temp
        self.condenser_leaving_water_temp = condenser_leaving_water_temp
        self.refrigerant_condensing_pressure = refrigerant_condensing_pressure
        self.state = state
        self.chilled_water_leaving_temp = chilled_water_leaving_temp
        self.chilled_water_entering_temp = chilled_water_entering_temp
        self.refrigerant_evaporating_pressure = refrigerant_evaporating_pressure
        self.compressor_load = compressor_load
        self.total_power_consumption = total_power_consumption
        
        field_names = [
            "condenser_entering_water_temp",
            "condenser_leaving_water_temp",
            "refrigerant_condensing_pressure",
            "state",
            "chilled_water_leaving_temp",
            "chilled_water_entering_temp",
            "refrigerant_evaporating_pressure",
            "compressor_load",
            "total_power_consumption",
        ]
        addresses = [0, 2, 4, 6, 10, 12, 14, 16, 18]
        self.field_addresses = dict(zip(field_names, addresses))


    def _float_to_regs(self, value, byteorder=">"):
        """
        Convert float to two 16-bit registers using IEEE754 single precision.
        :param byteorder: '>' big-endian (Modbus standard), '<' little-endian
        """
        packed = struct.pack(f'{byteorder}f', value)  # 4 bytes
        return list(struct.unpack(f'{byteorder}HH', packed))
    
    def _str_to_regs(self, text: str, max_regs=4):
        """
        Convert string to Modbus register list.
        :param text: The string to encode.
        :param max_regs: Optional maximum number of registers (truncate if longer).
        :return: list of integers (each is 0..65535).
        """
        # Convert to bytes (ASCII or UTF-8)
        b = text.encode("ascii")
        if len(b) % 2 == 1:
            b += b'\x00'
        regs = []
        for i in range(0, len(b), 2):
            regs.append((b[i] << 8) | b[i+1])
        if max_regs is not None:
            regs = regs[:max_regs]
        return regs    

    def _store_value(self, address, value):
        if isinstance(value, float):
            regs = self._float_to_regs(value)
        elif isinstance(value, int):
            regs = [value]
        elif isinstance(value, str):
            regs = self._str_to_regs(value)  # 最多占4个寄存器=8字节
        else:
            raise TypeError(f"Unsupported type: {type(value)}")
        self.context[2].setValues(3, address, regs)

    def store_all(self):
        for _, (addr, val) in self.field_addresses.items():
            self._store_value(addr, val)
           
    def store(self, key):
        # Store one field by key name.
        if key in self.field_addresses:
            addr = self.field_addresses[key]
            val = getattr(self, key)
            self._store_value(addr, val)

    def update_value(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"No such key: {key}")

    def report(self):
        return {
            "condenser_entering_water_temp (°C)": self.condenser_entering_water_temp,
            "condenser_leaving_water_temp (°C)": self.condenser_leaving_water_temp,
            "refrigerant_condensing_pressure (kPa)" : self.refrigerant_condensing_pressure,
            "state": self.state,
            "chilled_water_leaving_temp (°C)": self.chilled_water_leaving_temp,
            "chilled_water_entering_temp (°C)": self.chilled_water_entering_temp,
            "refrigerant_evaporating_pressure (kPa)": self.refrigerant_evaporating_pressure,
            "compressor_load (%)": self.compressor_load,
            "total_power_consumption (kW)": self.total_power_consumption,
        }

# 冷却塔
class CoolingTower:
    def __init__(self, context, state, tower_top_air_temp, tower_basin_temp, entering_water_temp, fan_speed, basin_water_level):

        self.context = context
        self.state = state
        self.tower_top_air_temp = tower_top_air_temp
        self.tower_basin_temp = tower_basin_temp
        self.entering_water_temp = entering_water_temp
        self.fan_speed = fan_speed
        self.basin_water_level = basin_water_level

        field_names = [
            "state",
            "tower_top_air_temp",
            "tower_basin_temp",
            "entering_water_temp",
            "fan_speed",
            "basin_water_level",
        ]
        addresses = [0, 4, 6, 8, 10, 12]
        self.field_addresses = dict(zip(field_names, addresses))

    def _float_to_regs(self, value, byteorder=">"):
        """
        Convert float to two 16-bit registers using IEEE754 single precision.
        :param byteorder: '>' big-endian (Modbus standard), '<' little-endian
        """
        packed = struct.pack(f'{byteorder}f', value)  # 4 bytes
        return list(struct.unpack(f'{byteorder}HH', packed))
    
    def _str_to_regs(self, text: str, max_regs=4):
        """
        Convert string to Modbus register list.
        :param text: The string to encode.
        :param max_regs: Optional maximum number of registers (truncate if longer).
        :return: list of integers (each is 0..65535).
        """
        # Convert to bytes (ASCII or UTF-8)
        b = text.encode("ascii")
        if len(b) % 2 == 1:
            b += b'\x00'
        regs = []
        for i in range(0, len(b), 2):
            regs.append((b[i] << 8) | b[i+1])
        if max_regs is not None:
            regs = regs[:max_regs]
        return regs    

    def _store_value(self, address, value):
        if isinstance(value, float):
            regs = self._float_to_regs(value)
        elif isinstance(value, int):
            regs = [value]
        elif isinstance(value, str):
            regs = self._str_to_regs(value)  # 最多占4个寄存器=8字节
        else:
            raise TypeError(f"Unsupported type: {type(value)}")
        self.context[1].setValues(3, address, regs)

    def store_all(self):
        for _, (addr, val) in self.field_addresses.items():
            self._store_value(addr, val)
           
    def store(self, key):
        # Store one field by key name.
        if key in self.field_addresses:
            addr = self.field_addresses[key]
            val = getattr(self, key)
            self._store_value(addr, val)

    def update_value(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"No such key: {key}")

    def report(self):
        return {
            "state": self.state,
            "tower_top_air_temp (°C)": self.tower_top_air_temp,
            "tower_basin_temp (°C)": self.tower_basin_temp,
            "entering_water_temp (°C)": self.entering_water_temp,
            "fan_speed (%)": self.fan_speed,
            "basin_water_level (%)": self.basin_water_level,
        }

# 冷凝水泵
class Pump:
    def __init__(self, state, flow_rate, discharge_pressure, power_consumption):
        self.state = state
        self.flow_rate = flow_rate
        self.discharge_pressure = discharge_pressure
        self.power_consumption = power_consumption

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
