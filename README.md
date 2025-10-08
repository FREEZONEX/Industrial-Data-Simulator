# Industrial-Data-Simulator
A versatile industrial data source simulator for UNS. Emulates OPC UA, Modbus, REST APIs，etc...
---

## 🚀 快速启动  
```bash
docker-compose up -d
```
前台管理界面访问 http://localhost:5000 
## 📈 数据变化  

数据变化由 **波动** ， **模拟** 和 **采集** 三部分组成：  
### 1. **数据模拟**：
- 每秒执行一次 (`step=1`)，使数据变化贴近真实情况。   
### 2. **波动**：
- 在当前数据的基础上进行小范围内随机变化。  
- 每次变化范围为 ±2%。  
- 默认变化频率为 **每 10 秒一次**，可通过接口动态调整。  
### 3. **采集**：
- 表示系统对模拟数据的采样频率，即数据输出到服务器的周期。  
- 默认采集频率为 **每 5 秒一次**，同样可通过接口动态修改。   

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
- 设备：`CT-301`, `Chiller-201`  
所有数据均存储在Holding Register中，地址映射如下：

| Unit ID | 设备名称      | 数据点名称                        | FC(功能码)| Address(起始寄存器地址)| Quantity(寄存器数量)| 说明           |
| ------- | ----------- | -------------------------------- | -------- | ----------------- | ---------------- | ----------------        |
| **1**   | **CT-301**  | state                            | 03       | 0                 | 4                | 状态字符串(string)     |
|         |             | tower_top_air_temp               | 03       | 4                 | 2                | 冷却塔顶部空气温度(float) |
|         |             | tower_basin_temp                 | 03       | 6                 | 2                | 冷却塔水盆温度(float)    |
|         |             | entering_water_temp              | 03       | 8                 | 2                | 冷却水入口温度(float)    |
|         |             | fan_speed                        | 03       | 10                | 2                | 风扇转速(float)         |
|         |             | basin_water_level                | 03       | 12                | 2                | 水盆水位(float)         |
| **2**   | **Chiller-201** | condenser_entering_water_temp    | 03       | 0                 | 2                | 冷凝器进水温度(float)    |
|         |             | condenser_leaving_water_temp     | 03       | 2                 | 2                | 冷凝器出水温度(float)    |
|         |             | refrigerant_condensing_pressure  | 03       | 4                 | 2                | 冷媒冷凝压力(float)      |
|         |             | state                            | 03       | 6                 | 4                | 状态字符串(string)     |
|         |             | chilled_water_leaving_temp       | 03       | 10                | 2                | 冷冻水出水温度(float)    |
|         |             | chilled_water_entering_temp      | 03       | 12                | 2                | 冷冻水进水温度(float)    |
|         |             | refrigerant_evaporating_pressure | 03       | 14                | 2                | 冷媒蒸发压力(float)      |
|         |             | compressor_load                  | 03       | 16                | 2                | 压缩机负载(float)        |
|         |             | total_power_consumption          | 03       | 18                | 2                | 总功耗(float)           |

### 🔹 OPC UA (`opc.tcp://localhost:4840/`)  
- 设备：`CDWP-301`, `CHWP-201`  
节点标识符如下：

| 设备名称                 | 数据点名称           | Node ID                                   | 说明                  |
| ----------------------- | ------------------ | ----------------------------------------- | -------------------- |
| **CDWP-301**            | state              | `ns=2;s=CDWP-301.state`                   | 泵的运行状态(string)  |
|                         | flow_rate          | `ns=2;s=CDWP-301.edge.flow_rate`          | 流量（m³/h）(float)  |
|                         | discharge_pressure | `ns=2;s=CDWP-301.edge.discharge_pressure` | 出口压力（kPa）(float) |
|                         | power_consumption  | `ns=2;s=CDWP-301.edge.powerconsumption`   | 功率消耗（kW）(float)  |
| **CHWP-201**            | state              | `ns=2;s=CHWP-201.state`                   | 泵的运行状态(string)  |
|                         | flow_rate          | `ns=2;s=CHWP-201.edge.flow_rate`          | 流量（m³/h）(float)   |
|                         | discharge_pressure | `ns=2;s=CHWP-201.edge.discharge_pressure` | 出口压力（kPa）(float) |
|                         | power_consumption  | `ns=2;s=CHWP-201.edge.powerconsumption`   | 功率消耗（kW）(float)  |

### 🔹 BACnet (`localhost:47808`)  
- 设备：`CRAH-101`  
对象的类型，实例号和属性如下：  

| 设备名称      | 数据点名称                     | Object Type           | Type      | Instance | Property Id | 说明               |
| ------------ | ---------------------------- | --------------------- | --------- | -------- | ----------- | -------           |
| **CRAH-101** | return_air_temp              | Analog Input          | 0         | 0        | 85          | 回风温度(float)    |
|              | supply_air_temp              | Analog Input          | 0         | 1        | 85          | 送风温度(float)    |
|              | chilled_water_valve_position | Analog Input          | 0         | 2        | 85          | 冷冻水阀门开度(float) |
|              | fan_speed                    | Analog Input          | 0         | 3        | 85          | 风机转速(float)    |
|              | status                       | Characterstring Value | 40        | 0        | 85          | 运行状态字符串(string) |

### 🔹 MQTT (`default Broker: localhost:1883`)  
- 发布 7 个 Topic  

| 主题路径 (Topic Path)                    | 数据类型  | 说明                |
| ------------------------------------ | ----- | ----------------- |
| `IT/DataHall-1/kpi/totalITLoad`      | Float | 数据大厅总 IT 负载功率（kW） |
| `datacenter/Rack-A01/edge/powerDraw` | Float | 机架 A01 实时功率（kW）   |
| `datacenter/Rack-A02/edge/powerDraw` | Float | 机架 A02 实时功率（kW）   |
| `datacenter/Rack-A03/edge/powerDraw` | Float | 机架 A03 实时功率（kW）   |
| `datacenter/Rack-A04/edge/powerDraw` | Float | 机架 A04 实时功率（kW）   |
| `datacenter/Rack-A05/edge/powerDraw` | Float | 机架 A05 实时功率（kW）   |
| `datacenter/Rack-A06/edge/powerDraw` | Float | 机架 A06 实时功率（kW）   |

## 📈 数据模拟流程  
### **1. 业务请求:** 
客户通过 REST API 提交一份算力订单。  
### **2. IT逻辑处理:** 
订单系统处理该订单，并将计算出的新增功耗“部署”到特定的服务器机柜 (Rack-A01)，当前机柜和数据大厅总 IT 负载功率提高。  
### **3. 系统自适应调节:** 
基于主冷却回路，冷水机组和次冷却回路对负载的升高作出响应。  
- 主冷却回路（空气 ↔ 水）  
核心作用：热量从空气转移到冷冻水，是数据中心内部热交换的起点。  
主要逻辑：  
  - returnAirTemp 由 IT 负载（totalITLoad）决定，并具有热惯性。
  - CRAH 通过调节 fanSpeed 与 chilledWaterValvePosition 来控制出风温度（supplyAirTemp）。
  - 当回风温度升高，系统自动增加风速与阀门开度，实现自调节冷却。

- 冷水机组（水 ↔ 水）  
核心作用： 连接次冷却回路与主冷却回路，将热量从冷冻水传递到冷凝水。  
主要逻辑：  
  - chilledWaterEnteringTemp 反映次冷却回路的热负荷。
  - 压缩机负载（compressorLoad）与热负荷成正比，带动能耗（totalPowerConsumption）变化。
  - 出水温度（chilledWaterLeavingTemp）由冷负荷与压缩机性能共同决定，体现制冷效果。

- 主冷却回路（水 ↔ 环境）  
核心作用： 将热量最终排放至外部环境。  
主要逻辑：  
  - 冷凝器出水温度（condenserLeavingWaterTemp）高于进水温度，热量传递至冷却塔。
  - 冷却塔通过 fanSpeed 调节散热效率，towerBasinTemp 受外界温度与湿度影响。
  - 冷凝水泵（CDWP-301）保证循环流动，其功耗与系统负载成正比。
