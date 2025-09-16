// frontend/src/components/OrderList.js
import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getOrders } from "../api";

function OrderList() {
  const [orders, setOrders] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();

  // 从 URL 获取参数
  const customer_id = searchParams.get("customer_id") || "";
  const status = searchParams.get("status") || "";

  // 本地表单状态
  const [filters, setFilters] = useState({
    customer_id,
    status,
  });

  // 每次 URL 参数变化时加载数据
  useEffect(() => {
    const params = {};
    if (customer_id) params.customer_id = customer_id;
    if (status) params.status = status;
    getOrders(params).then((res) => setOrders(res.data));
  }, [customer_id, status]);

  // 输入变化
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters({ ...filters, [name]: value });
  };

  // 点击筛选更新 URL
  const handleSearch = (e) => {
    e.preventDefault();
    const params = {};
    if (filters.customer_id) params.customer_id = filters.customer_id;
    if (filters.status) params.status = filters.status;
    setSearchParams(params); // 这会触发 useEffect 自动重新加载
  };

  return (
    <div>
      <h2>历史订单</h2>
      <form onSubmit={handleSearch} style={{ marginBottom: "10px" }}>
        <input
          name="customer_id"
          placeholder="客户ID"
          value={filters.customer_id}
          onChange={handleChange}
        />
        <select name="status" value={filters.status} onChange={handleChange}>
          <option value="">全部状态</option>
          <option value="Active">Active</option>
          <option value="Processing">Processing</option>
          <option value="Completed">Completed</option>
        </select>
        <button type="submit">筛选</button>
      </form>

      <ul>
        {orders.map((o) => (
          <li key={o.id}>
            <pre>{JSON.stringify(o, null, 2)}</pre>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default OrderList;
