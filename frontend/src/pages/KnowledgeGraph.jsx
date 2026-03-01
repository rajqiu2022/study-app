import React, { useEffect, useState } from 'react'
import {
  Card, Select, Button, Typography, Spin, Empty, Tag, Alert, Space, Progress, Divider, List,
} from 'antd'
import {
  NodeIndexOutlined, ReloadOutlined, BulbOutlined, WarningOutlined,
  CheckCircleOutlined, RobotOutlined, StarOutlined,
} from '@ant-design/icons'
import { getKnowledgeGraph, getSubjects } from '../api'

const { Title, Text, Paragraph } = Typography

const MASTERY_COLOR = {
  1: '#ef4444',
  2: '#f97316',
  3: '#eab308',
  4: '#22c55e',
  5: '#6366f1',
}
const MASTERY_TEXT = {
  1: '未掌握',
  2: '需加强',
  3: '一般',
  4: '熟练',
  5: '精通',
}

const IMPORTANCE_CONFIG = {
  high: { color: '#ef4444', text: '重点', bg: '#fef2f2' },
  medium: { color: '#f97316', text: '中等', bg: '#fff7ed' },
  low: { color: '#22c55e', text: '已掌握', bg: '#f0fdf4' },
}

export default function KnowledgeGraph() {
  const [subjects, setSubjects] = useState([])
  const [subjectId, setSubjectId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [graphData, setGraphData] = useState(null)
  const [hasData, setHasData] = useState(true)
  const [message, setMessage] = useState('')
  const [aiGenerated, setAiGenerated] = useState(false)

  useEffect(() => {
    getSubjects().then((res) => setSubjects(res.data)).catch(() => {})
  }, [])

  const handleGenerate = async () => {
    setLoading(true)
    setGraphData(null)
    try {
      const res = await getKnowledgeGraph(subjectId)
      if (res.data.has_data) {
        setGraphData(res.data.graph)
        setAiGenerated(res.data.ai_generated || false)
        setHasData(true)
      } else {
        setHasData(false)
        setMessage(res.data.message || '暂无数据')
      }
    } catch {
      setHasData(false)
      setMessage('生成失败，请检查网络或大模型配置')
    }
    setLoading(false)
  }

  // 按分类分组节点
  const groupedNodes = {}
  if (graphData?.nodes) {
    graphData.nodes.forEach((node) => {
      const cat = node.category || '其他'
      if (!groupedNodes[cat]) groupedNodes[cat] = []
      groupedNodes[cat].push(node)
    })
  }

  // 统计数据
  const stats = graphData?.nodes ? {
    total: graphData.nodes.length,
    mastered: graphData.nodes.filter((n) => n.mastery >= 4).length,
    weak: graphData.nodes.filter((n) => n.mastery <= 2).length,
    withErrors: graphData.nodes.filter((n) => n.related_wrong_count > 0).length,
  } : null

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        <NodeIndexOutlined /> 知识图谱
      </Title>

      <Card style={{ borderRadius: 16, marginBottom: 24 }}>
        <Space wrap>
          <Text>选择学科：</Text>
          <Select
            value={subjectId}
            onChange={setSubjectId}
            placeholder="全部学科"
            allowClear
            style={{ width: 160 }}
          >
            {subjects.map((s) => (
              <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>
            ))}
          </Select>
          <Button type="primary" icon={<ReloadOutlined />} onClick={handleGenerate} loading={loading}>
            {loading ? 'AI 分析中...' : '生成知识图谱'}
          </Button>
        </Space>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">AI 正在分析你的学习数据，请稍候...</Text>
          </div>
        </div>
      )}

      {!loading && !graphData && hasData && (
        <Card style={{ borderRadius: 16, textAlign: 'center', padding: '60px 0' }}>
          <NodeIndexOutlined style={{ fontSize: 48, color: '#d1d5db', marginBottom: 16 }} />
          <div>
            <Text type="secondary" style={{ fontSize: 16 }}>点击「生成知识图谱」，AI 会分析你的学习记录和错题，整理出知识点关系</Text>
          </div>
        </Card>
      )}

      {!loading && !hasData && (
        <Card style={{ borderRadius: 16 }}>
          <Empty description={message || '暂无学习数据'} />
        </Card>
      )}

      {!loading && graphData && (
        <>
          {/* AI 标识 */}
          {aiGenerated && (
            <Alert
              type="success"
              icon={<RobotOutlined />}
              showIcon
              message="AI 智能分析"
              description="此知识图谱由 AI 根据你的学习记录和错题智能生成"
              style={{ marginBottom: 16, borderRadius: 12 }}
            />
          )}

          {/* 总览 */}
          {graphData.summary && (
            <Card style={{ borderRadius: 16, marginBottom: 16, background: 'linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%)' }}>
              <Text style={{ fontSize: 15 }}>{graphData.summary}</Text>
            </Card>
          )}

          {/* 统计 */}
          {stats && (
            <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
              <Card size="small" style={{ flex: 1, minWidth: 120, borderRadius: 12, textAlign: 'center' }}>
                <div style={{ fontSize: 24, fontWeight: 700, color: '#6366f1' }}>{stats.total}</div>
                <Text type="secondary">知识点</Text>
              </Card>
              <Card size="small" style={{ flex: 1, minWidth: 120, borderRadius: 12, textAlign: 'center' }}>
                <div style={{ fontSize: 24, fontWeight: 700, color: '#22c55e' }}>{stats.mastered}</div>
                <Text type="secondary">已掌握</Text>
              </Card>
              <Card size="small" style={{ flex: 1, minWidth: 120, borderRadius: 12, textAlign: 'center' }}>
                <div style={{ fontSize: 24, fontWeight: 700, color: '#ef4444' }}>{stats.weak}</div>
                <Text type="secondary">需加强</Text>
              </Card>
              <Card size="small" style={{ flex: 1, minWidth: 120, borderRadius: 12, textAlign: 'center' }}>
                <div style={{ fontSize: 24, fontWeight: 700, color: '#f97316' }}>{stats.withErrors}</div>
                <Text type="secondary">有错题</Text>
              </Card>
            </div>
          )}

          {/* 知识点分类展示 */}
          {Object.entries(groupedNodes).map(([category, nodes]) => (
            <Card
              key={category}
              title={<><StarOutlined style={{ color: '#6366f1' }} /> {category}</>}
              style={{ borderRadius: 16, marginBottom: 16 }}
              size="small"
            >
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
                {nodes.map((node) => {
                  const imp = IMPORTANCE_CONFIG[node.importance] || IMPORTANCE_CONFIG.medium
                  return (
                    <div
                      key={node.id}
                      style={{
                        background: imp.bg,
                        border: `1px solid ${imp.color}20`,
                        borderRadius: 12,
                        padding: '12px 16px',
                        minWidth: 180,
                        flex: '0 0 auto',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                        <Text strong style={{ fontSize: 14 }}>{node.name}</Text>
                        <Tag color={imp.color} style={{ marginLeft: 8, borderRadius: 8 }}>{imp.text}</Tag>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Progress
                          percent={node.mastery * 20}
                          size="small"
                          strokeColor={MASTERY_COLOR[node.mastery]}
                          format={() => MASTERY_TEXT[node.mastery]}
                          style={{ flex: 1 }}
                        />
                      </div>
                      {node.related_wrong_count > 0 && (
                        <div style={{ marginTop: 6 }}>
                          <Text type="danger" style={{ fontSize: 12 }}>
                            <WarningOutlined /> {node.related_wrong_count} 道错题
                          </Text>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </Card>
          ))}

          {/* 知识关联 */}
          {graphData.links && graphData.links.length > 0 && (
            <Card
              title="知识关联"
              style={{ borderRadius: 16, marginBottom: 16 }}
              size="small"
            >
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {graphData.links.map((link, i) => {
                  const sourceNode = graphData.nodes.find((n) => n.id === link.source)
                  const targetNode = graphData.nodes.find((n) => n.id === link.target)
                  if (!sourceNode || !targetNode) return null
                  return (
                    <Tag key={i} style={{ borderRadius: 8, padding: '4px 10px', fontSize: 12 }}>
                      {sourceNode.name} → {targetNode.name}
                      <Text type="secondary" style={{ marginLeft: 4, fontSize: 11 }}>({link.relation})</Text>
                    </Tag>
                  )
                })}
              </div>
            </Card>
          )}

          {/* 学习建议 */}
          {graphData.suggestions && graphData.suggestions.length > 0 && (
            <Card
              title={<><BulbOutlined style={{ color: '#faad14' }} /> 学习建议</>}
              style={{ borderRadius: 16 }}
              size="small"
            >
              <List
                dataSource={graphData.suggestions}
                renderItem={(item, index) => (
                  <List.Item style={{ padding: '8px 0' }}>
                    <Text>
                      <CheckCircleOutlined style={{ color: '#6366f1', marginRight: 8 }} />
                      {item}
                    </Text>
                  </List.Item>
                )}
              />
            </Card>
          )}
        </>
      )}
    </div>
  )
}
