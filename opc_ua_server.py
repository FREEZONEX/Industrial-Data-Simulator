from opcua import Server, ua
from devices import Pump
import threading
import time

class PumpOPCUAServer:
    def __init__(self, server, endpoint="opc.tcp://0.0.0.0:4840/"):
        self.server = server
        self.server.set_endpoint(endpoint)
        self.server.set_server_name("OPC UA Server")

        self.uri = "http://example.com/pump"
        self.idx = self.server.register_namespace(self.uri)  # idx will be 2
        self.obj = self.server.get_objects_node()

        self.pumps = {}
        self.pump_vars = {}

    def add_pump(self, name, pump: Pump):
        this_pump = self.obj.add_object(ua.NodeId(name, self.idx), name)
        edge = this_pump.add_folder(self.idx, f"{name}.edge")

        vars = {}  # 维护变量对象
        vars["state"] = this_pump.add_variable(ua.NodeId(f"{name}.state", self.idx), "state", pump.state)
        vars["flow_rate"] = edge.add_variable(ua.NodeId(f"{name}.edge.flow_rate", self.idx), "flow_rate", pump.flow_rate)
        vars["discharge_pressure"] = edge.add_variable(ua.NodeId(f"{name}.edge.discharge_pressure", self.idx), "discharge_pressure", pump.discharge_pressure)
        vars["power_consumption"] = edge.add_variable(ua.NodeId(f"{name}.edge.powerconsumption", self.idx), "powerconsumption", pump.powerconsumption)

        self.pumps[name] = pump
        self.pump_vars[name] = vars

        self._set_unit(vars["flow_rate"], "kg/s", "kilogram per second", 440)
        self._set_unit(vars["discharge_pressure"], "bar", "bar", 103)
        self._set_unit(vars["power_consumption"], "kW", "kilowatt", 169)

    def _set_unit(self, variable, display_name, description, unit_id):
        unit = ua.EUInformation()
        unit.NamespaceUri = "http://www.opcfoundation.org/UA/units/un/cefact"
        unit.UnitId = unit_id  # OPC UA标准单位编码
        unit.DisplayName = ua.LocalizedText(display_name)
        unit.Description = ua.LocalizedText(description)

        variable.add_property(
            self.idx,
            "EngineeringUnits",
            unit,
            datatype=ua.NodeId(887, 0)  # 887 = EUInformation, standard type
        )
        
    def run(self):
        self.server.start()
        try:
            while True:
                for name, pump in self.pumps.items():
                    vars = self.pump_vars[name]
                    vars["state"].set_value(pump.state)
                    vars["flow_rate"].set_value(pump.flow_rate)
                    vars["discharge_pressure"].set_value(pump.discharge_pressure)
                    vars["power_consumption"].set_value(pump.powerconsumption)
                time.sleep(1)
                pass
        except KeyboardInterrupt:
            print("shutting down")
        finally:
            server.stop()

# init Pump instance
server = Server()
cdwp_301 = Pump("Running", 150.5, 3.2, 22.7)
chwp_201 = Pump("Running", 120.8, 4.1, 35.2)

my_server = PumpOPCUAServer(server)
my_server.add_pump("CDWP-301", cdwp_301)
my_server.add_pump("CHWP-201", chwp_201)

server_thread = threading.Thread(target=my_server.run, daemon=True)
server_thread.start()

print("OPC UA Server is running in background thread.")

# 主线程继续执行其他任务，保持程序不退出
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Main thread interrupted, exiting.")
