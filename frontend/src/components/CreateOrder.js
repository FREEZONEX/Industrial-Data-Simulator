import React, { useState } from "react";
import { createOrder } from "../api";

function CreateOrder() {
  const [form, setForm] = useState({
    customer_id: "",
    requested_resources: { cpu_cores: 0, memory_gb: 0, storage_tb: 0 },
    duration_months: 0
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name in form.requested_resources) {
      setForm({
        ...form,
        requested_resources: { ...form.requested_resources, [name]: Number(value) }
      });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await createOrder(form);
      alert("订单创建成功！");
      console.log(res.data);
    } catch (err) {
      console.error(err);
      alert("创建失败");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="customer_id" placeholder="客户ID" onChange={handleChange} />
      <input name="cpu_cores" type="number" placeholder="CPU 核数" onChange={handleChange} />
      <input name="memory_gb" type="number" placeholder="内存GB" onChange={handleChange} />
      <input name="storage_tb" type="number" placeholder="存储TB" onChange={handleChange} />
      <input name="duration_months" type="number" placeholder="租用时长（月）" onChange={handleChange} />
      <button type="submit">创建订单</button>
    </form>
  );
}

export default CreateOrder;
