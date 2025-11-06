import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getOrders } from "../api";
import { Form, Input, Select, Button, List, Card, Descriptions } from "antd";
import { useTranslation } from "react-i18next";

const { Option } = Select;

function OrderList() {
  const [orders, setOrders] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();
  const customer_id = searchParams.get("customer_id") || "";
  const status = searchParams.get("status") || "";
  const [form] = Form.useForm();
  const { t } = useTranslation();

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
      <h2>{t("orderList.title")}</h2>

      <Form form={form} layout="inline" onFinish={handleFinish} style={{ marginBottom: 16 }}>
        <Form.Item name="customer_id">
          <Input placeholder={t("orderList.customer_id_placeholder")} />
        </Form.Item>

        <Form.Item name="status">
          <Select placeholder={t("orderList.status_all")} style={{ width: 150 }}>
            <Option value="">{t("orderList.status_all")}</Option>
            <Option value="Active">{t("orderList.status_active")}</Option>
            <Option value="Processing">{t("orderList.status_processing")}</Option>
            <Option value="Completed">{t("orderList.status_completed")}</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit">
            {t("orderList.filter")}
          </Button>
        </Form.Item>
      </Form>

      <List
        grid={{ gutter: 16, column: 1 }}
        dataSource={orders}
        pagination={{ pageSize: 5 }}
        renderItem={(o) => (
          <List.Item>
            <Card>
              <Descriptions title={`${t("orderList.order")} ${o.order_id}`} bordered column={1}>
                <Descriptions.Item label={t("orderList.customer_id")}>{o.customer_id}</Descriptions.Item>
                <Descriptions.Item label={t("orderList.status")}>{t(`order.status_${o.status.toLowerCase()}`)}</Descriptions.Item>
                <Descriptions.Item label={t("orderList.created_at")}>{o.created_at}</Descriptions.Item>
                <Descriptions.Item label={t("orderList.activated_at")}>{o.activated_at}</Descriptions.Item>
                <Descriptions.Item label={t("orderList.duration_months")}>{o.duration_months}</Descriptions.Item>
                <Descriptions.Item label={t("orderList.cpu_cores")}>{o.requested_resources.cpu_cores}</Descriptions.Item>
                <Descriptions.Item label={t("orderList.memory_gb")}>{o.requested_resources.memory_gb}</Descriptions.Item>
                <Descriptions.Item label={t("orderList.storage_tb")}>{o.requested_resources.storage_tb}</Descriptions.Item>
              </Descriptions>
            </Card>
          </List.Item>
        )}
      />
    </div>
  );
}

export default OrderList;
