// frontend/src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import CreateOrder from "./components/CreateOrder";
import OrderList from "./components/OrderList";
import ConfigForm from "./components/ConfigForm";
import MqttForm from "./components/MqttForm";

function App() {
  return (
    <Router>
      <div>
        <h1>计算资源管理系统</h1>
        <nav>
          <Link to="/orders">订单列表</Link> |{" "}
          <Link to="/create">创建订单</Link> |{" "}
          <Link to="/config">配置</Link> |{" "}
          <Link to="/mqtt">MQTT</Link>
        </nav>
        <Routes>
          <Route path="/orders" element={<OrderList />} />
          <Route path="/create" element={<CreateOrder />} />
          <Route path="/config" element={<ConfigForm />} />
          <Route path="/mqtt" element={<MqttForm />} />
          <Route path="/" element={<OrderList />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
