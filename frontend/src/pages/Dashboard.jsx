import React, { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Tag, List, Progress, Empty, Spin, Typography } from 'antd'
import {
  BookOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  CheckCircleOutlined,
  StarOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import { getDashboard } from '../api'

const { Title, Text } = Typography

const MASTERY_MAP = {
  1: { text: '未掌握', color: '#ef4444' },
  2: { text: '需加强', color: '#f97316' },
  3: { text: '一般', color: '#eab308' },
  4: { text: '熟练', color: '#22c55e' },
  5: { text: '精通', color: '#6366f1' },
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '120px auto' }} />

  if (!data) {
    return (
      <div style={{ textAlign: 'center', marginTop: 100 }}>
        <Empty description="无法连接服务器，请先启动后端服务" />
        <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
          运行: cd backend && uvicorn app.main:app --reload
        </Text>
      </div>
    )
  }

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        👋 你好，{data.user.name}！
      </Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card className="stat-card hover-card">
            <Statistic
              title="学习天数"
              value={data.total_study_days}
              suffix="天"
              prefix={<ClockCircleOutlined style={{ color: '#6366f1' }} />}
              valueStyle={{ color: '#6366f1' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="stat-card hover-card">
            <Statistic
              title="学习时长"
              value={data.total_study_minutes}
              suffix="分钟"
              prefix={<BookOutlined style={{ color: '#8b5cf6' }} />}
              valueStyle={{ color: '#8b5cf6' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="stat-card hover-card">
            <Statistic
              title="错题总数"
              value={data.total_wrong_questions}
              suffix="道"
              prefix={<CloseCircleOutlined style={{ color: '#ef4444' }} />}
              valueStyle={{ color: '#ef4444' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card className="stat-card hover-card">
            <Statistic
              title="已解决"
              value={data.resolved_wrong_questions}
              suffix="道"
              prefix={<CheckCircleOutlined style={{ color: '#22c55e' }} />}
              valueStyle={{ color: '#22c55e' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 各科进度 */}
        <Col xs={24} md={14}>
          <Card title={<><StarOutlined /> 各科学习进度</>} style={{ borderRadius: 16 }}>
            {data.subject_progress.length === 0 ? (
              <Empty description="还没有学习记录，快去记录吧！" />
            ) : (
              data.subject_progress.map((sp) => (
                <div key={sp.subject_id} style={{ marginBottom: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <Text strong>{sp.icon} {sp.subject_name}</Text>
                    <Text type="secondary">{sp.total_records} 条记录 | 错题 {sp.wrong_count} 道</Text>
                  </div>
                  <Progress
                    percent={Math.round(sp.avg_mastery * 20)}
                    strokeColor={{
                      '0%': '#6366f1',
                      '100%': '#a78bfa',
                    }}
                    format={() => `掌握度 ${sp.avg_mastery}/5`}
                  />
                  {sp.weak_points.length > 0 && (
                    <div style={{ marginTop: 4 }}>
                      {sp.weak_points.map((wp) => (
                        <Tag key={wp} color="orange" style={{ marginBottom: 4 }}>⚠️ {wp}</Tag>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </Card>
        </Col>

        {/* 薄弱知识点 + 最近记录 */}
        <Col xs={24} md={10}>
          {data.weak_knowledge_points.length > 0 && (
            <Card
              title={<><WarningOutlined style={{ color: '#f97316' }} /> 薄弱知识点</>}
              style={{ borderRadius: 16, marginBottom: 16 }}
            >
              {data.weak_knowledge_points.map((kp) => (
                <Tag key={kp} color="red" style={{ marginBottom: 6, fontSize: 13, padding: '4px 10px' }}>
                  {kp}
                </Tag>
              ))}
            </Card>
          )}

          <Card title={<><ClockCircleOutlined /> 最近学习</>} style={{ borderRadius: 16 }}>
            {data.recent_records.length === 0 ? (
              <Empty description="暂无记录" />
            ) : (
              <List
                size="small"
                dataSource={data.recent_records.slice(0, 8)}
                renderItem={(r) => (
                  <List.Item>
                    <div style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text ellipsis style={{ maxWidth: 180 }}>{r.knowledge_point}</Text>
                        <Tag color={MASTERY_MAP[r.mastery_level]?.color}>
                          {MASTERY_MAP[r.mastery_level]?.text}
                        </Tag>
                      </div>
                      <Text type="secondary" style={{ fontSize: 12 }}>{r.study_date}</Text>
                    </div>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}
