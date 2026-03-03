import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Dropdown, Button, Modal, Form, Input, Select, message, Avatar, Typography } from 'antd'
import {
  DashboardOutlined,
  BookOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  MessageOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  ApiOutlined,
  NodeIndexOutlined,
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import LearningRecords from './pages/LearningRecords'
import WrongQuestions from './pages/WrongQuestions'
import Practice from './pages/Practice'
import Chat from './pages/Chat'
import Login from './pages/Login'
import Settings from './pages/Settings'
import KnowledgeGraph from './pages/KnowledgeGraph'
import { getCurrentUser, setCurrentUser, clearCurrentUser, updateUser } from './api'

const { Sider, Content } = Layout
const { Text } = Typography

const GRADES = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '七年级', '八年级', '九年级']

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '学习仪表盘' },
  { key: '/records', icon: <BookOutlined />, label: '学习记录' },
  { key: '/wrong', icon: <CloseCircleOutlined />, label: '错题本' },
  { key: '/practice', icon: <ThunderboltOutlined />, label: '智能练习' },
  { key: '/knowledge', icon: <NodeIndexOutlined />, label: '知识图谱' },
  { key: '/chat', icon: <MessageOutlined />, label: 'AI小助手' },
]

const adminMenuItems = [
  { key: '/settings', icon: <SettingOutlined />, label: '大模型设置' },
]

// 移动端底部Tab配置
const mobileTabItems = [
  { key: '/', icon: <DashboardOutlined />, label: '首页' },
  { key: '/records', icon: <BookOutlined />, label: '记录' },
  { key: '/chat', icon: <MessageOutlined />, label: '助手' },
  { key: '/knowledge', icon: <NodeIndexOutlined />, label: '图谱' },
  { key: '/practice', icon: <ThunderboltOutlined />, label: '练习' },
]

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768)
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth <= 768)
    window.addEventListener('resize', handler)
    return () => window.removeEventListener('resize', handler)
  }, [])
  return isMobile
}

function AppLayout({ user, onLogout, onUserUpdate }) {
  const navigate = useNavigate()
  const location = useLocation()
  const isMobile = useIsMobile()
  const [profileOpen, setProfileOpen] = useState(false)
  const [form] = Form.useForm()

  const handleOpenProfile = () => {
    form.setFieldsValue({ name: user.name, grade: user.grade, password: '' })
    setProfileOpen(true)
  }

  const handleSaveProfile = async () => {
    try {
      const values = await form.validateFields()
      const payload = {}
      if (values.name && values.name !== user.name) payload.name = values.name
      if (values.grade && values.grade !== user.grade) payload.grade = values.grade
      if (values.password) payload.password = values.password

      if (Object.keys(payload).length === 0) {
        setProfileOpen(false)
        return
      }

      const res = await updateUser(user.id, payload)
      setCurrentUser(res.data)
      onUserUpdate(res.data)
      message.success('修改成功')
      setProfileOpen(false)
    } catch (e) {
      message.error('修改失败')
    }
  }

  const isAdmin = user.is_admin || false
  const sideMenuItems = isAdmin ? [...menuItems, ...adminMenuItems] : menuItems

  const dropdownItems = {
    items: [
      { key: 'profile', icon: <SettingOutlined />, label: '修改资料' },
      ...(isAdmin ? [{ key: 'llm-settings', icon: <ApiOutlined />, label: '大模型设置' }] : []),
      { type: 'divider' },
      { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
    ],
    onClick: ({ key }) => {
      if (key === 'logout') {
        clearCurrentUser()
        onLogout()
      } else if (key === 'profile') {
        handleOpenProfile()
      } else if (key === 'llm-settings') {
        navigate('/settings')
      }
    },
  }

  // 移动端布局
  if (isMobile) {
    return (
      <div className="mobile-layout">
        {/* 顶部栏 */}
        <div className="mobile-header">
          <span style={{ fontSize: 18, fontWeight: 700 }}>📚 学习小助手</span>
          <Dropdown menu={dropdownItems} trigger={['click']}>
            <Avatar size="small" style={{ background: '#e0e7ff', color: '#6366f1', cursor: 'pointer' }} icon={<UserOutlined />} />
          </Dropdown>
        </div>

        {/* 内容区 */}
        <div className="mobile-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/records" element={<LearningRecords />} />
            <Route path="/wrong" element={<WrongQuestions />} />
            <Route path="/practice" element={<Practice />} />
            <Route path="/knowledge" element={<KnowledgeGraph />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>

        {/* 底部Tab */}
        <div className="mobile-tab-bar">
          {mobileTabItems.map((item) => (
            <div
              key={item.key}
              className={`mobile-tab-item ${location.pathname === item.key ? 'active' : ''}`}
              onClick={() => navigate(item.key)}
            >
              <div className="mobile-tab-icon">{item.icon}</div>
              <div className="mobile-tab-label">{item.label}</div>
            </div>
          ))}
        </div>

        {/* 修改资料弹窗 */}
        <Modal
          title="修改资料" open={profileOpen}
          onOk={handleSaveProfile} onCancel={() => setProfileOpen(false)}
          okText="保存" cancelText="取消"
        >
          <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
            <Form.Item label="账号"><Input value={user.username} disabled /></Form.Item>
            <Form.Item name="name" label="昵称" rules={[{ required: true, message: '请输入昵称' }]}>
              <Input placeholder="昵称" />
            </Form.Item>
            <Form.Item name="grade" label="年级">
              <Select options={GRADES.map((g) => ({ label: g, value: g }))} />
            </Form.Item>
            <Form.Item name="password" label="新密码（留空则不修改）">
              <Input.Password placeholder="输入新密码" />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    )
  }

  // 桌面端布局（保持不变）
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={200}
        style={{
          background: 'linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%)',
          boxShadow: '2px 0 12px rgba(99, 102, 241, 0.3)',
        }}
      >
        <div style={{
          height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'white', fontSize: 20, fontWeight: 700,
          borderBottom: '1px solid rgba(255,255,255,0.15)',
        }}>
          📚 学习小助手
        </div>
        <Menu
          mode="inline" selectedKeys={[location.pathname]}
          items={sideMenuItems} onClick={({ key }) => navigate(key)}
          style={{ background: 'transparent', border: 'none', color: 'rgba(255,255,255,0.85)', marginTop: 8 }}
          theme="dark"
        />
        <div style={{ position: 'absolute', bottom: 0, width: '100%', padding: '16px', borderTop: '1px solid rgba(255,255,255,0.15)' }}>
          <Dropdown menu={dropdownItems} trigger={['click']} placement="topLeft">
            <div style={{
              display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', color: 'white', padding: '8px', borderRadius: 8, transition: 'background 0.2s',
            }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <Avatar style={{ background: '#e0e7ff', color: '#6366f1' }} icon={<UserOutlined />} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.name}</div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>{user.grade}</div>
              </div>
            </div>
          </Dropdown>
        </div>
      </Sider>
      <Content style={{ overflow: 'auto' }}>
        <div className="page-container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/records" element={<LearningRecords />} />
            <Route path="/wrong" element={<WrongQuestions />} />
            <Route path="/practice" element={<Practice />} />
            <Route path="/knowledge" element={<KnowledgeGraph />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </Content>

      <Modal
        title="修改资料" open={profileOpen}
        onOk={handleSaveProfile} onCancel={() => setProfileOpen(false)}
        okText="保存" cancelText="取消"
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item label="账号"><Input value={user.username} disabled /></Form.Item>
          <Form.Item name="name" label="昵称" rules={[{ required: true, message: '请输入昵称' }]}>
            <Input placeholder="昵称" />
          </Form.Item>
          <Form.Item name="grade" label="年级">
            <Select options={GRADES.map((g) => ({ label: g, value: g }))} />
          </Form.Item>
          <Form.Item name="password" label="新密码（留空则不修改）">
            <Input.Password placeholder="输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  )
}

export default function App() {
  const [user, setUser] = useState(getCurrentUser())

  if (!user) {
    return <Login onLogin={(u) => setUser(u)} />
  }

  return (
    <BrowserRouter>
      <AppLayout
        user={user}
        onLogout={() => setUser(null)}
        onUserUpdate={(u) => setUser(u)}
      />
    </BrowserRouter>
  )
}
