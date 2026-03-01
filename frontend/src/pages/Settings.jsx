import React, { useEffect, useState } from 'react'
import {
  Card, Form, Input, Select, Switch, Button, message, Typography, Space, Tag, Alert, Divider, Spin,
} from 'antd'
import {
  ApiOutlined, RocketOutlined, CheckCircleOutlined, CloseCircleOutlined,
  InfoCircleOutlined, ThunderboltOutlined, BulbOutlined,
} from '@ant-design/icons'
import { getLLMConfig, saveLLMConfig, testLLMConnection, getCurrentUser } from '../api'

const { Title, Text, Paragraph } = Typography

const PRESETS = [
  {
    label: '智谱 GLM（推荐）',
    provider: 'openai',
    api_url: 'https://open.bigmodel.cn/api/paas/v4',
    api_key: '',
    model_name: 'glm-4-flash',
    desc: '智谱 AI，glm-4-flash 免费使用，注册即可获取 API Key',
  },
  {
    label: 'DeepSeek',
    provider: 'openai',
    api_url: 'https://api.deepseek.com/v1',
    api_key: '',
    model_name: 'deepseek-chat',
    desc: '国产大模型，性价比高，需注册获取 API Key',
  },
  {
    label: '通义千问（阿里）',
    provider: 'openai',
    api_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key: '',
    model_name: 'qwen-plus',
    desc: '阿里云大模型，兼容 OpenAI 接口',
  },
  {
    label: 'OpenAI',
    provider: 'openai',
    api_url: 'https://api.openai.com/v1',
    api_key: '',
    model_name: 'gpt-4o-mini',
    desc: '需要 OpenAI 账号和 API Key',
  },
  {
    label: 'Moonshot（月之暗面）',
    provider: 'openai',
    api_url: 'https://api.moonshot.cn/v1',
    api_key: '',
    model_name: 'moonshot-v1-8k',
    desc: '国产大模型，需注册获取 API Key',
  },
  {
    label: '自定义接口',
    provider: 'openai',
    api_url: '',
    api_key: '',
    model_name: '',
    desc: '填写兼容 OpenAI 格式的任意接口地址',
  },
]

export default function Settings() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null) // { success, reply/error }
  const [selectedPreset, setSelectedPreset] = useState(null)

  const currentUser = getCurrentUser()
  const isAdmin = currentUser?.is_admin || false

  useEffect(() => {
    if (!isAdmin) {
      setLoading(false)
      return
    }
    getLLMConfig()
      .then((res) => {
        if (res.data) {
          form.setFieldsValue(res.data)
          // 匹配预设
          const preset = PRESETS.find(
            (p) => p.api_url === res.data.api_url && p.provider === res.data.provider
          )
          if (preset) setSelectedPreset(preset.label)
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handlePresetSelect = (presetLabel) => {
    const preset = PRESETS.find((p) => p.label === presetLabel)
    if (preset) {
      setSelectedPreset(presetLabel)
      setTestResult(null)
      const currentKey = form.getFieldValue('api_key')
      form.setFieldsValue({
        provider: preset.provider,
        api_url: preset.api_url,
        model_name: preset.model_name,
        api_key: preset.api_key || currentKey || '',
      })
    }
  }

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const values = form.getFieldsValue()
      const res = await testLLMConnection({
        provider: values.provider,
        api_url: values.api_url,
        api_key: values.api_key,
        model_name: values.model_name,
      })
      setTestResult(res.data)
    } catch (e) {
      setTestResult({ success: false, error: e.message || '请求失败' })
    }
    setTesting(false)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const values = await form.validateFields()
      await saveLLMConfig(values)
      message.success('保存成功')
    } catch (e) {
      message.error('保存失败')
    }
    setSaving(false)
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', paddingTop: 100 }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!isAdmin) {
    return (
      <div style={{ textAlign: 'center', paddingTop: 100 }}>
        <Alert
          type="warning"
          showIcon
          message="无权访问"
          description="大模型设置仅管理员可操作。如需修改配置，请联系管理员。"
          style={{ maxWidth: 400, margin: '0 auto', borderRadius: 12 }}
        />
      </div>
    )
  }

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        <ApiOutlined /> 大模型设置
      </Title>

      <Alert
        type="info"
        showIcon
        icon={<InfoCircleOutlined />}
        message="配置大模型后，智能练习的出题将由 AI 动态生成，题目更丰富、更贴合知识点"
        description="支持 Ollama 本地模型和所有兼容 OpenAI 接口的云服务。未配置或连接失败时自动使用内置题库。"
        style={{ marginBottom: 24, borderRadius: 12 }}
      />

      {/* 快速选择预设 */}
      <Card title="快速选择" style={{ borderRadius: 16, marginBottom: 24 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          {PRESETS.map((preset) => (
            <Card
              key={preset.label}
              size="small"
              hoverable
              style={{
                width: 200,
                borderRadius: 12,
                cursor: 'pointer',
                border: selectedPreset === preset.label ? '2px solid #6366f1' : '1px solid #e5e7eb',
                background: selectedPreset === preset.label ? '#f0f0ff' : 'white',
              }}
              onClick={() => handlePresetSelect(preset.label)}
            >
              <div style={{ fontWeight: 600, marginBottom: 4 }}>
                {preset.provider === 'ollama' ? <RocketOutlined /> : <ThunderboltOutlined />}{' '}
                {preset.label}
              </div>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {preset.desc}
              </Text>
            </Card>
          ))}
        </div>
      </Card>

      {/* 详细配置 */}
      <Card title="接口配置" style={{ borderRadius: 16, marginBottom: 24 }}>
        <Form form={form} layout="vertical" initialValues={{ provider: 'openai', enabled: false, deep_thinking: false }}>
          <Form.Item name="provider" label="接口类型">
            <Select
              options={[
                { label: 'OpenAI 兼容接口（OpenAI / DeepSeek / 通义千问等）', value: 'openai' },
                { label: 'Ollama（本地部署）', value: 'ollama' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="api_url"
            label="接口地址"
            rules={[{ required: true, message: '请输入接口地址' }]}
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                智谱GLM: https://open.bigmodel.cn/api/paas/v4 | OpenAI: https://api.openai.com/v1
              </Text>
            }
          >
            <Input placeholder="如：http://localhost:11434 或 https://api.deepseek.com/v1" />
          </Form.Item>

          <Form.Item
            name="api_key"
            label="API Key"
            extra={<Text type="secondary" style={{ fontSize: 12 }}>Ollama 本地部署不需要填写</Text>}
          >
            <Input.Password placeholder="sk-xxxx（Ollama 可留空）" />
          </Form.Item>

          <Form.Item
            name="model_name"
            label="模型名称"
            rules={[{ required: true, message: '请输入模型名称' }]}
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                智谱GLM: glm-4-flash(免费) | DeepSeek: deepseek-chat | OpenAI: gpt-4o-mini
              </Text>
            }
          >
            <Input placeholder="模型名称" />
          </Form.Item>

          <Divider />

          <Form.Item name="enabled" label="启用 AI 出题" valuePropName="checked">
            <Switch checkedChildren="已启用" unCheckedChildren="未启用" />
          </Form.Item>

          <Form.Item
            name="deep_thinking"
            label={
              <Space>
                <BulbOutlined style={{ color: '#faad14' }} />
                <span>深度思考</span>
              </Space>
            }
            valuePropName="checked"
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                开启后 AI 会更深入地思考题目质量和答案准确性，出题更严谨但耗时可能更长
              </Text>
            }
          >
            <Switch checkedChildren="已开启" unCheckedChildren="未开启" />
          </Form.Item>
        </Form>

        {/* 测试结果 */}
        {testResult && (
          <Alert
            type={testResult.success ? 'success' : 'error'}
            icon={testResult.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            showIcon
            message={testResult.success ? '连接成功！' : '连接失败'}
            description={
              testResult.success
                ? `模型回复：${testResult.reply}`
                : `错误信息：${testResult.error}`
            }
            style={{ marginBottom: 16, borderRadius: 8 }}
          />
        )}

        <Space>
          <Button onClick={handleTest} loading={testing} icon={<ApiOutlined />}>
            测试连接
          </Button>
          <Button type="primary" onClick={handleSave} loading={saving}>
            保存配置
          </Button>
        </Space>
      </Card>

      {/* 说明 */}
      <Card
        title="使用说明"
        style={{ borderRadius: 16 }}
        size="small"
      >
        <Paragraph style={{ marginBottom: 8 }}>
          <Text strong>智谱 GLM（推荐，免费）：</Text>
        </Paragraph>
        <Paragraph style={{ paddingLeft: 16, fontSize: 13 }}>
          1. 访问 <Text code>https://open.bigmodel.cn</Text> 注册账号<br />
          2. 在控制台获取 API Key<br />
          3. 选择「智谱 GLM」预设，填入 API Key 即可<br />
          4. glm-4-flash 模型免费使用，速度快，中文能力优秀
        </Paragraph>
        <Paragraph style={{ marginBottom: 8 }}>
          <Text strong>其他云端模型：</Text>
        </Paragraph>
        <Paragraph style={{ paddingLeft: 16, fontSize: 13 }}>
          支持所有兼容 OpenAI Chat Completions 格式的接口，包括 DeepSeek、通义千问、Moonshot 等。
          填入对应的接口地址、API Key 和模型名称即可。
        </Paragraph>
      </Card>
    </div>
  )
}
