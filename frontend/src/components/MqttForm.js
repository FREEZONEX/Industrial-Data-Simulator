import React, { useState } from "react";
import { updateMqtt } from "../api";

function MqttForm() {
  const [form, setForm] = useState({ broker: "", port: 1883 });

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.name === "port" ? Number(e.target.value) : e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await updateMqtt(form);
    alert("MQTT Broker 更新成功");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="broker" placeholder="Broker地址" onChange={handleChange} />
      <input name="port" type="number" placeholder="端口" onChange={handleChange} />
      <button type="submit">更新MQTT</button>
    </form>
  );
}

export default MqttForm;
