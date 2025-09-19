// frontend/src/components/Dashboard.js
import React, { useEffect, useState } from "react";
import { getDashboardData } from "../api";
import { Card, Row, Col, Switch } from "antd";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from "recharts";

const Dashboard = () => {
  const [cdwpData, setCdwpData] = useState([]);
  const [chwpData, setChwpData] = useState([]);
  const [crahData, setCrahData] = useState([]);
  const [ctData, setCtData] = useState([]);
  const [powerData, setPowerData] = useState([]);
  const [chillerData, setChillerData] = useState([]);
  const [collecting, setCollecting] = useState(false);

  useEffect(() => {
    let interval;
    if (collecting) {
      interval = setInterval(async () => {
        try {
          const res = await getDashboardData();
          const d = res.data;
          const timestamp = new Date().toLocaleTimeString();

          // CDWP 301
          setCdwpData((prev) => [
            ...prev.slice(-19),
            { time: timestamp, ...d.cdwp_301 },
          ]);

          // CHWP 201
          setChwpData((prev) => [
            ...prev.slice(-19),
            { time: timestamp, ...d.chwp_201 },
          ]);

          // CRAH 101
          setCrahData((prev) => [
            ...prev.slice(-19),
            { time: timestamp, ...d.crah_101 },
          ]);

          // CT 301
          setCtData((prev) => [
            ...prev.slice(-19),
            { time: timestamp, ...d.ct_301 },
          ]);

          // Power Aggregator + RACK-A01~A06
          const rackData = {};
          ["RACK-A01","RACK-A02","RACK-A03","RACK-A04","RACK-A05","RACK-A06"].forEach(rack => {
            rackData[rack] = d[rack]?.power ?? 0;  // 展开到顶层
          });
          setPowerData((prev) => [
            ...prev.slice(-19),
            { time: timestamp, total: d.power_aggregator.total, ...rackData }
          ]);

          // CHILLER 201
          setChillerData((prev) => [
            ...prev.slice(-19),
            { time: timestamp, ...d.chiller_201 },
          ]);
        } catch (err) {
          console.error(err);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [collecting]);

  return (
    <div>
      <Row justify="space-between" style={{ marginBottom: 16 }}>
        <Col>
          <Switch
            checked={collecting}
            onChange={() => setCollecting(!collecting)}
            checkedChildren="采集中"
            unCheckedChildren="停止采集"
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* CDWP + CHWP */}
        <Col span={24}>
          <Card title="CDWP 301 / CHWP 201">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={cdwpData.map((item, idx) => ({
                ...item,
                ...chwpData[idx],
                time: item.time,
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                {/* CDWP */}
                <Line type="monotone" dataKey="discharge_pressure" stroke="#8884d8" name="CDWP 压力" />
                <Line type="monotone" dataKey="flow_rate" stroke="#82ca9d" name="CDWP 流量" />
                <Line type="monotone" dataKey="power_consumption" stroke="#ff7300" name="CDWP 功耗" />
                {/* CHWP */}
                <Line type="monotone" dataKey="discharge_pressure" stroke="#0000ff" name="CHWP 压力" />
                <Line type="monotone" dataKey="flow_rate" stroke="#00ff00" name="CHWP 流量" />
                <Line type="monotone" dataKey="power_consumption" stroke="#ff00ff" name="CHWP 功耗" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* CRAH 101 */}
        <Col span={24}>
          <Card title="CRAH 101">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={crahData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="chilled_water_valve_position" stroke="#8884d8" name="阀门位置" />
                <Line type="monotone" dataKey="fan_speed" stroke="#82ca9d" name="风扇转速" />
                <Line type="monotone" dataKey="return_air_temp" stroke="#ff7300" name="回风温度" />
                <Line type="monotone" dataKey="supply_air_temp" stroke="#ff0000" name="送风温度" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* CT 301 */}
        <Col span={24}>
          <Card title="CT 301">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={ctData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="basin_water_level" stroke="#8884d8" name="水池水位" />
                <Line type="monotone" dataKey="entering_water_temp" stroke="#82ca9d" name="进水温度" />
                <Line type="monotone" dataKey="fan_speed" stroke="#ff7300" name="风扇转速" />
                <Line type="monotone" dataKey="tower_basin_temp" stroke="#ff0000" name="水池温度" />
                <Line type="monotone" dataKey="tower_top_air_temp" stroke="#00ff00" name="塔顶空气温度" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* Power Aggregator */}
        <Col span={24}>
          <Card title="Power Aggregator">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={powerData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                {/* 总功耗 */}
                <Line type="monotone" dataKey="total" stroke="#8884d8" name="总功耗" />
                {/* RACK-A01 ~ RACK-A06 */}
                {["RACK-A01","RACK-A02","RACK-A03","RACK-A04","RACK-A05","RACK-A06"].map((rack, idx) => (
                  <Line
                    key={rack}
                    type="monotone"
                    dataKey={rack}   // 展开后顶层字段
                    stroke={["#ff7300","#82ca9d","#ff0000","#00ff00","#0000ff","#aa00ff"][idx]}
                    name={`${rack} 功率`}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* CHILLER 201 - 温度类 */}
        <Col span={24}>
          <Card title="CHILLER 201 - 温度类">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chillerData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="chilled_water_entering_temp" stroke="#8884d8" name="进水温度" />
                <Line type="monotone" dataKey="chilled_water_leaving_temp" stroke="#82ca9d" name="出水温度" />
                <Line type="monotone" dataKey="condenser_entering_water_temp" stroke="#ff0000" name="冷凝器进水温度" />
                <Line type="monotone" dataKey="condenser_leaving_water_temp" stroke="#00ff00" name="冷凝器出水温度" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        {/* CHILLER 201 - 压力 & 功耗 */}
        <Col span={24}>
          <Card title="CHILLER 201 - 压力 / 功耗">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chillerData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="refrigerant_condensing_pressure" stroke="#0000ff" name="冷媒冷凝压力" />
                <Line type="monotone" dataKey="refrigerant_evaporating_pressure" stroke="#aaaa00" name="冷媒蒸发压力" />
                <Line type="monotone" dataKey="compressor_load" stroke="#ff7300" name="压缩机负载" />
                <Line type="monotone" dataKey="total_power_consumption" stroke="#ff00ff" name="总功耗" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
