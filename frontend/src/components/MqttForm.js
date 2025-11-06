import React from "react";
import { Form, Input, InputNumber, Button, message } from "antd";
import { useTranslation } from "react-i18next";
import { updateMqtt } from "../api";

function MqttForm() {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const { t } = useTranslation(); // 引入国际化钩子

  const handleFinish = async (values) => {
    try {
      await updateMqtt(values);
      messageApi.success(t("mqtt.update_success"));
      form.resetFields();
    } catch (err) {
      console.error(err);
      messageApi.error(t("mqtt.update_fail"));
    }
  };

  return (
    <>
      {contextHolder}
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{ broker: "", port: 1883 }}
      >
        <Form.Item
          label={t("mqtt.broker_address")}
          name="broker"
          rules={[{ required: true, message: t("mqtt.broker_required") }]}
        >
          <Input placeholder={t("mqtt.broker_placeholder")} />
        </Form.Item>

        <Form.Item
          label={t("mqtt.port")}
          name="port"
          rules={[{ required: true, message: t("mqtt.port_required") }]}
        >
          <InputNumber style={{ width: "100%" }} />
        </Form.Item>

        <Button type="primary" htmlType="submit">
          {t("mqtt.update_button")}
        </Button>
      </Form>
    </>
  );
}

export default MqttForm;
