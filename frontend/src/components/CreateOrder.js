import React from "react";
import { Form, Input, InputNumber, Button, message } from "antd";
import { createOrder } from "../api";

function CreateOrder() {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage(); // 获取 message 实例

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
      messageApi.success("订单创建成功！"); // 使用实例显示
      form.resetFields();
    } catch (err) {
      console.error(err);
      messageApi.error("创建失败"); // 使用实例显示
    }
  };

  return (
    <>
      {contextHolder} {/* 必须渲染在组件里 */}
      <Form form={form} layout="vertical" onFinish={handleFinish}>
        <Form.Item label="客户ID" name="customer_id" rules={[{ required: true }]}>
          <Input />
        </Form.Item>

        <Form.Item label="CPU 核数" name="cpu_cores" rules={[{ required: true }]}>
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item label="内存GB" name="memory_gb" rules={[{ required: true }]}>
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item label="存储TB" name="storage_tb" rules={[{ required: true }]}>
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item label="租用时长（月）" name="duration_months" rules={[{ required: true }]}>
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Button type="primary" htmlType="submit">
          创建订单
        </Button>
      </Form>
    </>
  );
}

export default CreateOrder;
