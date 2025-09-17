import React from "react";
import { Form, Input, InputNumber, Button, message } from "antd";
import { updateMqtt } from "../api";

function MqttForm() {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage(); // 获取 message 实例

  const handleFinish = async (values) => {
    try {
      await updateMqtt(values);
      messageApi.success("MQTT Broker 更新成功"); // 使用实例显示
      form.resetFields();
    } catch (err) {
      console.error(err);
      messageApi.error("更新失败，请重试"); // 使用实例显示
    }
  };

  return (
    <>
      {contextHolder} {/* 必须渲染在组件里 */}
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{ broker: "", port: 1883 }}
      >
        <Form.Item label="Broker 地址" name="broker" rules={[{ required: true }]}>
          <Input />
        </Form.Item>

        <Form.Item label="端口" name="port" rules={[{ required: true }]}>
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Button type="primary" htmlType="submit">
          更新MQTT
        </Button>
      </Form>
    </>
  );
}

export default MqttForm;
