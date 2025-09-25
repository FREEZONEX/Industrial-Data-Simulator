import React from "react";
import { updateConfig } from "../api";
import { Form, InputNumber, Button, message } from "antd";

function ConfigForm() {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();

  const handleFinish = async (values) => {
    try {
      await updateConfig(values);
      messageApi.success("配置更新成功"); // 使用实例显示
    } catch (err) {
      console.error(err);
      messageApi.error("配置更新失败，请重试");
    }
  };

  return (
    <>
      {contextHolder}
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{ SERVER_UPDATE_INTERNAL: 1, RANDOM_UPDATE_INTERVAL: 1 }}
      >
        <Form.Item
          label="服务器更新间隔"
          name="SERVER_UPDATE_INTERNAL"
          rules={[{ required: true }]}
        >
          <InputNumber step={0.1} style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          label="数据波动间隔"
          name="RANDOM_UPDATE_INTERVAL"
          rules={[{ required: true }]}
        >
          <InputNumber step={0.1} style={{ width: "100%" }} />
        </Form.Item>

        <Button type="primary" htmlType="submit">
          更新配置
        </Button>
      </Form>
    </>
  );
}

export default ConfigForm;
