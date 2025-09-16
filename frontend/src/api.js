import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1", // Flask接口
});

// 创建订单
export const createOrder = (data) => api.post("/orders", data);

// 更新数据变化速率
export const updateConfig = (data) => api.post("/config", data);

// 查询历史订单
export const getOrders = (params) => api.get("/orders", { params });

// 更新MQTT Broker
export const updateMqtt = (data) => api.post("/mqtt", data);
