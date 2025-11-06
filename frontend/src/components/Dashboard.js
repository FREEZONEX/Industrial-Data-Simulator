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
import { useTranslation } from "react-i18next";

const Dashboard = () => {
  const [cdwpData, setCdwpData] = useState([]);
  const [chwpData, setChwpData] = useState([]);
  const [crahData, setCrahData] = useState([]);
  const [ctData, setCtData] = useState([]);
  const [powerData, setPowerData] = useState([]);
  const [chillerData, setChillerData] = useState([]);
  const [collecting, setCollecting] = useState(false);

  const { t } = useTranslation();

  useEffect(() => {
    let interval;
    if (collecting) {
      interval = setInterval(async () => {
        try {
          const res = await getDashboardData();
          const d = res.data;
          const timestamp = new Date().toLocaleTimeString();

          setCdwpData((prev) => [...prev.slice(-19), { time: timestamp, ...d.cdwp_301 }]);
          setChwpData((prev) => [...prev.slice(-19), { time: timestamp, ...d.chwp_201 }]);
          setCrahData((prev) => [...prev.slice(-19), { time: timestamp, ...d.crah_101 }]);
          setCtData((prev) => [...prev.slice(-19), { time: timestamp, ...d.ct_301 }]);

          const rackData = {};
          ["RACK-A01", "RACK-A02", "RACK-A03", "RACK-A04", "RACK-A05", "RACK-A06"].forEach(rack => {
            rackData[rack] = d[rack]?.power ?? 0;
          });
          setPowerData((prev) => [
            ...prev.slice(-19),
            { time: timestamp, total: d.power_aggregator.total, ...rackData },
          ]);

          setChillerData((prev) => [...prev.slice(-19), { time: timestamp, ...d.chiller_201 }]);
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
            checkedChildren={t("dashboard.collecting")}
            unCheckedChildren={t("dashboard.stopCollecting")}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* CDWP + CHWP */}
        <Col span={24}>
          <Card title={t("dashboard.cdwp_chwp_title")}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={cdwpData.map((item, idx) => ({
                  ...item,
                  ...chwpData[idx],
                  time: item.time,
                }))}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="discharge_pressure" stroke="#8884d8" name={t("dashboard.cdwpPressure")} />
                <Line type="monotone" dataKey="flow_rate" stroke="#82ca9d" name={t("dashboard.cdwpFlow")} />
                <Line type="monotone" dataKey="power_consumption" stroke="#ff7300" name={t("dashboard.cdwpPower")} />
                <Line type="monotone" dataKey="discharge_pressure" stroke="#0000ff" name={t("dashboard.chwpPressure")} />
                <Line type="monotone" dataKey="flow_rate" stroke="#00ff00" name={t("dashboard.chwpFlow")} />
                <Line type="monotone" dataKey="power_consumption" stroke="#ff00ff" name={t("dashboard.chwpPower")} />
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
                <Line type="monotone" dataKey="chilled_water_valve_position" stroke="#8884d8" name={t("dashboard.valvePosition")} />
                <Line type="monotone" dataKey="fan_speed" stroke="#82ca9d" name={t("dashboard.fanSpeed")} />
                <Line type="monotone" dataKey="return_air_temp" stroke="#ff7300" name={t("dashboard.returnAirTemp")} />
                <Line type="monotone" dataKey="supply_air_temp" stroke="#ff0000" name={t("dashboard.supplyAirTemp")} />
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
                <Line type="monotone" dataKey="basin_water_level" stroke="#8884d8" name={t("dashboard.basinWaterLevel")} />
                <Line type="monotone" dataKey="entering_water_temp" stroke="#82ca9d" name={t("dashboard.enteringWaterTemp")} />
                <Line type="monotone" dataKey="fan_speed" stroke="#ff7300" name={t("dashboard.fanSpeed")} />
                <Line type="monotone" dataKey="tower_basin_temp" stroke="#ff0000" name={t("dashboard.towerBasinTemp")} />
                <Line type="monotone" dataKey="tower_top_air_temp" stroke="#00ff00" name={t("dashboard.towerTopAirTemp")} />
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
                <Line type="monotone" dataKey="total" stroke="#8884d8" name={t("dashboard.totalPower")} />
                {["RACK-A01", "RACK-A02", "RACK-A03", "RACK-A04", "RACK-A05", "RACK-A06"].map((rack, idx) => (
                  <Line
                    key={rack}
                    type="monotone"
                    dataKey={rack}
                    stroke={["#ff7300", "#82ca9d", "#ff0000", "#00ff00", "#0000ff", "#aa00ff"][idx]}
                    name={`${rack} ${t("dashboard.rackPower")}`}
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
                <Line type="monotone" dataKey="chilled_water_entering_temp" stroke="#8884d8" name={t("dashboard.enteringWaterTemp")} />
                <Line type="monotone" dataKey="chilled_water_leaving_temp" stroke="#82ca9d" name={t("dashboard.leavingWaterTemp")} />
                <Line type="monotone" dataKey="condenser_entering_water_temp" stroke="#ff0000" name={t("dashboard.condenserEnterTemp")} />
                <Line type="monotone" dataKey="condenser_leaving_water_temp" stroke="#00ff00" name={t("dashboard.condenserLeaveTemp")} />
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
                <Line type="monotone" dataKey="refrigerant_condensing_pressure" stroke="#0000ff" name={t("dashboard.condensingPressure")} />
                <Line type="monotone" dataKey="refrigerant_evaporating_pressure" stroke="#aaaa00" name={t("dashboard.evaporatingPressure")} />
                <Line type="monotone" dataKey="compressor_load" stroke="#ff7300" name={t("dashboard.compressorLoad")} />
                <Line type="monotone" dataKey="total_power_consumption" stroke="#ff00ff" name={t("dashboard.totalPower")} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
