import React, { useState } from "react";
import { updateConfig } from "../api";

function ConfigForm() {
  const [form, setForm] = useState({ SERVER_UPDATE_INTERNAL: 1, RANDOM_UPDATE_INTERVAL: 1 });

  const handleChange = (e) => setForm({ ...form, [e.target.name]: parseFloat(e.target.value) });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await updateConfig(form);
    alert("配置更新成功");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="SERVER_UPDATE_INTERNAL" type="number" step="0.1" placeholder="服务器更新间隔" onChange={handleChange} />
      <input name="RANDOM_UPDATE_INTERVAL" type="number" step="0.1" placeholder="数据波动间隔" onChange={handleChange} />
      <button type="submit">更新配置</button>
    </form>
  );
}

export default ConfigForm;
