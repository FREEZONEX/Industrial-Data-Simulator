# Industrial-Data-Simulator
A versatile industrial data source simulator for UNS. Emulates OPC UA, Modbus, REST APIs，etc...
---

## 🚀 快速启动  
```bash
docker-compose up -d
```
前台管理界面访问 http://localhost:5000 
## 📈 数据变化  

数据变化由 **波动** 和 **模拟** 两部分组成：  

- **数据模拟**：每秒执行一次 (`step=1`)，使数据变化贴近真实情况。  
- **波动**：每次变化范围为 ±2%，默认变化频率为 **每 5 秒一次**。  
- 可以通过接口动态修改波动频率和模拟速率。  

---

## 🛠 接口文档  

### 1. 创建计算资源租用订单  
**Endpoint:** `POST /api/v1/orders`  
**描述:** 创建新的计算资源租用订单。  
**请求体 (Request Body, application/json):**  
```json
{
  "customer_id": "string",
  "requested_resources": {
    "cpu_cores": "integer",
    "memory_gb": "integer",
    "storage_tb": "integer"
  },
  "duration_months": "integer"
}
```
⚠️ 注意：**只有在第一次创建订单后，数据模拟任务才会启动。**

---

### 2. 查询历史订单
**Endpoint:** `GET /api/v1/orders`  
**描述:** 查询历史计算资源租用订单。  
**查询参数 (Query Parameters):**  
- `customer_id` (string, optional)：按客户 ID 筛选  
- `status` (string, optional)：按订单状态筛选 (e.g., `'Active'`, `'Completed'`, `'Processing'`)  

**成功响应:** `200 OK`  

---

### 3. 更新数据变化速率
**Endpoint:** `POST /api/v1/config`  
**描述:** 更新数据模拟与波动的速率。  
**请求体 (Request Body, application/json):**  
```json
{
  "SERVER_UPDATE_INTERNAL": "float",   // 服务器数据更新间隔（秒）
  "RANDOM_UPDATE_INTERVAL": "float"    // 数据波动更新间隔（秒）
}
```

### 4. MQTT Broker选择
**Endpoint:** `POST /api/v1/mqtt`  
**描述:** 支持mqtt设备选择broker。  
**请求体 (Request Body): application/json**  
```json
{
    "broker": "string",
    "port": "interger",
}
```

### 5. 查询当前数据
**Endpoint:** `POST /api/v1/dashboard`  
**描述:** 查询当前所有数据点的值。  
**查询参数 (Query Parameters):** 无  
**成功响应:** `200 OK`  
  
## 📡 支持协议与映射  

### 🔹 Modbus TCP (`localhost:5020`)  
- **Unit 1 → CT-301**  
- **Unit 2 → Chiller-201**  

所有数据均存储在Holding Register中，地址映射如下：  
```yaml
CT-301:
  state: 0  # string, 4 regs
  tower_top_air_temp: 4  # float, 2 regs
  tower_basin_temp: 6
  entering_water_temp: 8
  fan_speed: 10
  basin_water_level: 12

Chiller-201:
  condenser_entering_water_temp: 0
  condenser_leaving_water_temp: 2
  refrigerant_condensing_pressure: 4
  state: 6  # string, 4 regs
  chilled_water_leaving_temp: 10
  chilled_water_entering_temp: 12
  refrigerant_evaporating_pressure: 14
  compressor_load: 16
  total_power_consumption: 18
```
### 🔹 OPC UA (`opc.tcp://localhost:4840/`)  
- 设备：`CDWP-301`, `CHWP-201`  

节点标识符如下：

```yaml
CDWP-301 / CHWP-201: # pump_name
  state: ns=2;s=pump_name.state # string
  flow_rate: ns=2;s=pump_name.edge.flow_rate
  discharge_pressure: ns=2;s=pump_name.edge.discharge_pressure
  power_consumption: ns=2;s=pump_name.edge.powerconsumption
```

### 🔹 BACnet (`localhost:47808`)  
- 设备：`CRAH-101`  

对象的类型，实例号和属性如下：
```yaml
CRAH-101:
  return_air_temp: analogInput 0 presentValue
  supply_air_temp: analogInput 1 presentValue
  chilled_water_valve_position: analogInput 2 presentValue
  fan_speed: analogInput 3 presentValue
  status: characterstringValue 0 presentValue
```
### 🔹 MQTT (`default Broker: localhost:1883`)  
- 发布 7 个 Topic  

```yaml
IT/DataHall-1/kpi/totalITLoad
datacenter/Rack-A01/edge/powerDraw
datacenter/Rack-A02/edge/powerDraw
datacenter/Rack-A03/edge/powerDraw
datacenter/Rack-A04/edge/powerDraw
datacenter/Rack-A05/edge/powerDraw
datacenter/Rack-A06/edge/powerDraw
```
