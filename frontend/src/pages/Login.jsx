import React, { useState } from 'react'
import { Card, Form, Input, Button, Select, Tabs, message, Typography } from 'antd'
import { UserOutlined, LockOutlined, SmileOutlined } from '@ant-design/icons'
import { register, login, setCurrentUser } from '../api'

const { Title, Text } = Typography

const GRADES = [
  '一年级', '二年级', '三年级', '四年级', '五年级', '六年级',
  '七年级', '八年级', '九年级',
]

export default function Login({ onLogin }) {
  const [loading, setLoading] = useState(false)
  const [loginForm] = Form.useForm()
  const [registerForm] = Form.useForm()

  const handleLogin = async (values) => {
    setLoading(true)
    try {
      const res = await login(values)
      setCurrentUser(res.data)
      message.success(`欢迎回来，${res.data.name}！`)
      onLogin(res.data)
    } catch (e) {
      message.error(e.response?.data?.detail || '登录失败')
    }
    setLoading(false)
  }

  const handleRegister = async (values) => {
    setLoading(true)
    try {
      const res = await register(values)
      setCurrentUser(res.data)
      message.success('注册成功，欢迎！')
      onLogin(res.data)
    } catch (e) {
      message.error(e.response?.data?.detail || '注册失败')
    }
    setLoading(false)
  }

  const items = [
    {
      key: 'login',
      label: '登录',
      children: (
        <Form form={loginForm} onFinish={handleLogin} size="large" style={{ marginTop: 8 }}>
          <Form.Item name="username" rules={[{ required: true, message: '请输入账号' }]}>
            <Input prefix={<UserOutlined />} placeholder="账号" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登录
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'register',
      label: '注册',
      children: (
        <Form form={registerForm} onFinish={handleRegister} size="large" style={{ marginTop: 8 }}>
          <Form.Item name="name" rules={[{ required: true, message: '请输入昵称' }]}>
            <Input prefix={<SmileOutlined />} placeholder="昵称" />
          </Form.Item>
          <Form.Item name="username" rules={[{ required: true, message: '请输入账号' }]}>
            <Input prefix={<UserOutlined />} placeholder="账号" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, min: 4, message: '密码至少4位' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item name="grade" initialValue="三年级">
            <Select options={GRADES.map((g) => ({ label: g, value: g }))} placeholder="年级" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              注册
            </Button>
          </Form.Item>
        </Form>
      ),
    },
  ]

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card style={{
        width: 420,
        borderRadius: 20,
        boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>📚</div>
          <Title level={3} style={{ margin: 0 }}>学习小助手</Title>
          <Text type="secondary">记录学习，发现不足，快速进步</Text>
        </div>
        <Tabs items={items} centered />
      </Card>
    </div>
  )
}
