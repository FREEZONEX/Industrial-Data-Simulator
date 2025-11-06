import React from "react";
import { Form, Input, InputNumber, Button, message } from "antd";
import { createOrder } from "../api";
import { useTranslation } from "react-i18next";

function CreateOrder() {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const { t } = useTranslation();

  const handleFinish = async (values) => {
    try {
      const payload = {
        customer_id: values.customer_id,
        requested_resources: {
          cpu_cores: values.cpu_cores,
          memory_gb: values.memory_gb,
          storage_tb: values.storage_tb,
        },
        duration_months: values.duration_months,
      };
      await createOrder(payload);
      messageApi.success(t("order.createSuccess"));
      form.resetFields();
    } catch (err) {
      console.error(err);
      messageApi.error(t("order.createFail"));
    }
  };

  return (
    <>
      {contextHolder}
      <Form form={form} layout="vertical" onFinish={handleFinish}>
        <Form.Item
          label={t("order.customerId")}
          name="customer_id"
          rules={[{ required: true, message: t("order.required") }]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          label={t("order.cpuCores")}
          name="cpu_cores"
          rules={[{ required: true, message: t("order.required") }]}
        >
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          label={t("order.memoryGb")}
          name="memory_gb"
          rules={[{ required: true, message: t("order.required") }]}
        >
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          label={t("order.storageTb")}
          name="storage_tb"
          rules={[{ required: true, message: t("order.required") }]}
        >
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          label={t("order.durationMonths")}
          name="duration_months"
          rules={[{ required: true, message: t("order.required") }]}
        >
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Button type="primary" htmlType="submit">
          {t("order.createButton")}
        </Button>
      </Form>
    </>
  );
}

export default CreateOrder;
