import React from "react";
import { updateConfig } from "../api";
import { Form, InputNumber, Button, message } from "antd";
import { useTranslation } from "react-i18next";

function ConfigForm() {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const { t } = useTranslation(); // i18n

  const handleFinish = async (values) => {
    try {
      await updateConfig(values);
      messageApi.success(t('config.updateSuccess')); // 国际化提示
    } catch (err) {
      console.error(err);
      messageApi.error(t('config.updateFail'));
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
          label={t('config.serverUpdateInterval')}
          name="SERVER_UPDATE_INTERNAL"
          rules={[{ required: true, message: t('config.required') }]}
        >
          <InputNumber step={0.1} style={{ width: "100%" }} />
        </Form.Item>

        <Form.Item
          label={t('config.randomUpdateInterval')}
          name="RANDOM_UPDATE_INTERVAL"
          rules={[{ required: true, message: t('config.required') }]}
        >
          <InputNumber step={0.1} style={{ width: "100%" }} />
        </Form.Item>

        <Button type="primary" htmlType="submit">
          {t('config.updateButton')}
        </Button>
      </Form>
    </>
  );
}

export default ConfigForm;
