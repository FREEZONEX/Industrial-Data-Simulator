import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getOrders } from "../api";
import { Form, Input, Select, Button, List, Card, Descriptions } from "antd";

const { Option } = Select;

function OrderList() {
  const [orders, setOrders] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();
  const customer_id = searchParams.get("customer_id") || "";
  const status = searchParams.get("status") || "";

  const [form] = Form.useForm();

  useEffect(() => {
    const params = {};
    if (customer_id) params.customer_id = customer_id;
    if (status) params.status = status;
    getOrders(params).then((res) => setOrders(res.data));
    form.setFieldsValue({ customer_id, status });
  }, [customer_id, status]);

  const handleFinish = (values) => {
    const params = {};
    if (values.customer_id) params.customer_id = values.customer_id;
    if (values.status) params.status = values.status;
    setSearchParams(params);
  };

  return (
    <div>
      <h2>历史订单</h2>
      <Form form={form} layout="inline" onFinish={handleFinish} style={{ marginBottom: 16 }}>
        <Form.Item name="customer_id">
          <Input placeholder="客户ID" />
        </Form.Item>
        <Form.Item name="status">
          <Select placeholder="全部状态" style={{ width: 150 }}>
            <Option value="">全部状态</Option>
            <Option value="Active">Active</Option>
            <Option value="Processing">Processing</Option>
            <Option value="Completed">Completed</Option>
          </Select>
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">筛选</Button>
        </Form.Item>
      </Form>

      <List
        grid={{ gutter: 16, column: 1 }}
        dataSource={orders}
        pagination={{ pageSize: 5 }}
        renderItem={(o) => (
          <List.Item>
            <Card>
              <Descriptions title={`订单 ${o.order_id}`} bordered column={1}>
                <Descriptions.Item label="客户ID">{o.customer_id}</Descriptions.Item>
                <Descriptions.Item label="状态">{o.status}</Descriptions.Item>
                <Descriptions.Item label="创建时间">{o.created_at}</Descriptions.Item>
                <Descriptions.Item label="激活时间">{o.activated_at}</Descriptions.Item>
                <Descriptions.Item label="租用时长（月）">{o.duration_months}</Descriptions.Item>
                <Descriptions.Item label="CPU 核数">{o.requested_resources.cpu_cores}</Descriptions.Item>
                <Descriptions.Item label="内存 GB">{o.requested_resources.memory_gb}</Descriptions.Item>
                <Descriptions.Item label="存储 TB">{o.requested_resources.storage_tb}</Descriptions.Item>
              </Descriptions>
            </Card>
          </List.Item>
        )}
      />
    </div>
  );
}

export default OrderList;
