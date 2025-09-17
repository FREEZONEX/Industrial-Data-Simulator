// frontend/src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import { Layout, Menu, Typography } from "antd";
import {
  UnorderedListOutlined,
  PlusOutlined,
  SettingOutlined,
  CloudServerOutlined,
} from "@ant-design/icons";

import CreateOrder from "./components/CreateOrder";
import OrderList from "./components/OrderList";
import ConfigForm from "./components/ConfigForm";
import MqttForm from "./components/MqttForm";

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

// 菜单组件
const NavigationMenu = () => {
  const location = useLocation();
  const selectedKey = location.pathname === "/" ? "/orders" : location.pathname;

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[selectedKey]}
      items={[
        {
          key: "/orders",
          icon: <UnorderedListOutlined />,
          label: <Link to="/orders">订单列表</Link>,
        },
        {
          key: "/create",
          icon: <PlusOutlined />,
          label: <Link to="/create">创建订单</Link>,
        },
        {
          key: "/config",
          icon: <SettingOutlined />,
          label: <Link to="/config">配置</Link>,
        },
        {
          key: "/mqtt",
          icon: <CloudServerOutlined />,
          label: <Link to="/mqtt">MQTT</Link>,
        },
      ]}
    />
  );
};

function App() {
  return (
    <Router>
      <Layout style={{ minHeight: "100vh" }}>
        {/* 侧边导航 */}
        <Sider collapsible>
          <div
            style={{
              height: 64,
              margin: 16,
              color: "#fff",
              fontWeight: "bold",
              textAlign: "center",
              lineHeight: "64px",
              fontSize: 16,
            }}
          >
            计算资源管理
          </div>
          <NavigationMenu />
        </Sider>

        <Layout>
          {/* 顶部 */}
          <Header style={{ background: "#fff", paddingLeft: 25, display: "flex", alignItems: "center",}}>
            <Title level={3} style={{ margin: 0 }}>
              测试系统控制台
            </Title>
          </Header>

          {/* 内容区 */}
          <Content style={{ margin: "16px" }}>
            <div
              style={{
                padding: 24,
                minHeight: 360,
                background: "#fff",
                borderRadius: 8,
              }}
            >
              <Routes>
                <Route path="/orders" element={<OrderList />} />
                <Route path="/create" element={<CreateOrder />} />
                <Route path="/config" element={<ConfigForm />} />
                <Route path="/mqtt" element={<MqttForm />} />
                <Route path="/" element={<OrderList />} />
              </Routes>
            </div>
          </Content>

          {/* 底部 */}
          <Footer style={{ textAlign: "center" }}>
            计算资源管理系统
          </Footer>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;
