import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import { Layout, Menu, Typography, Button } from "antd";
import {
  UnorderedListOutlined,
  PlusOutlined,
  SettingOutlined,
  CloudServerOutlined,
  AreaChartOutlined
} from "@ant-design/icons";
import { useTranslation } from 'react-i18next';

import CreateOrder from "./components/CreateOrder";
import OrderList from "./components/OrderList";
import ConfigForm from "./components/ConfigForm";
import MqttForm from "./components/MqttForm";
import Dashboard from "./components/Dashboard";

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const NavigationMenu = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const selectedKey = location.pathname === "/" ? "/orders" : location.pathname;

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[selectedKey]}
      items={[
        { key: "/orders", icon: <UnorderedListOutlined />, label: <Link to="/orders">{t('menu.orderList')}</Link> },
        { key: "/create", icon: <PlusOutlined />, label: <Link to="/create">{t('menu.createOrder')}</Link> },
        { key: "/config", icon: <SettingOutlined />, label: <Link to="/config">{t('menu.config')}</Link> },
        { key: "/mqtt", icon: <CloudServerOutlined />, label: <Link to="/mqtt">{t('menu.mqtt')}</Link> },
        { key: "/dashboard", icon: <AreaChartOutlined />, label: <Link to="/dashboard">{t('menu.dashboard')}</Link> },
      ]}
    />
  );
};

function App() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng); // 切换语言
  };

  return (
    <Router>
      <Layout style={{ minHeight: "100vh" }}>
        <Sider collapsible>
          <div style={{
            height: 64, margin: 16, color: "#fff", fontWeight: "bold",
            textAlign: "center", lineHeight: "64px", fontSize: 16
          }}>
            {t('app.siderTitle')}
          </div>
          <NavigationMenu />
        </Sider>

        <Layout>
          <Header style={{
            background: "#fff", paddingLeft: 25, display: "flex",
            alignItems: "center", justifyContent: "space-between"
          }}>
            <Title level={3} style={{ margin: 0 }}>{t('app.headerTitle')}</Title>
            <div>
              <Button size="small" onClick={() => changeLanguage('zh')} style={{ marginRight: 8 }}>中文</Button>
              <Button size="small" onClick={() => changeLanguage('en')}>EN</Button>
            </div>
          </Header>

          <Content style={{ margin: "16px" }}>
            <div style={{ padding: 24, minHeight: 360, background: "#fff", borderRadius: 8 }}>
              <Routes>
                <Route path="/orders" element={<OrderList />} />
                <Route path="/create" element={<CreateOrder />} />
                <Route path="/config" element={<ConfigForm />} />
                <Route path="/mqtt" element={<MqttForm />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/" element={<OrderList />} />
              </Routes>
            </div>
          </Content>

          <Footer style={{ textAlign: "center" }}>{t('app.footer')}</Footer>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;
