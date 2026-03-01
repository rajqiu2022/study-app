import React, { useEffect, useState } from 'react'
import {
  Card, Button, Select, InputNumber, Input, Radio, Tag, Space, message,
  Typography, Result, Progress, Divider, Spin, Alert, Table, Popconfirm, Segmented,
} from 'antd'
import {
  ThunderboltOutlined, CheckCircleOutlined, CloseCircleOutlined, RobotOutlined,
  HistoryOutlined, DeleteOutlined, EyeOutlined, PlayCircleOutlined, PlusOutlined,
} from '@ant-design/icons'
import { generatePractice, submitPractice, abandonPractice, getPracticeSession, getPracticeSessions, getSubjects, getLLMConfig } from '../api'

const { Title, Text } = Typography

const PRACTICE_MODES = [
  { label: '📝 错题练习', value: 'wrong_review' },
  { label: '⭐ 重点知识练习', value: 'important_review' },
  { label: '✏️ 自定义练习', value: 'custom' },
]

const STATUS_MAP = {
  generating: { text: '出题中', color: 'processing' },
  practicing: { text: '练习中', color: 'warning' },
  completed: { text: '已完成', color: 'success' },
  abandoned: { text: '已废弃', color: 'default' },
}

const MODE_MAP = {
  wrong_review: '错题练习',
  important_review: '重点知识',
  custom: '自定义',
}

export default function Practice() {
  const [subjects, setSubjects] = useState([])
  const [subjectId, setSubjectId] = useState('math')
  const [knowledgePoint, setKnowledgePoint] = useState('')
  const [count, setCount] = useState(5)
  const [practiceMode, setPracticeMode] = useState('custom')
  const [session, setSession] = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(false)
  const [view, setView] = useState('new') // new / history / practice / result
  const [sessions, setSessions] = useState([])
  const [sessionsLoading, setSessionsLoading] = useState(false)

  useEffect(() => {
    getSubjects().then((res) => setSubjects(res.data)).catch(() => {})
    getLLMConfig().then((res) => {
      if (res.data && res.data.enabled) setAiEnabled(true)
    }).catch(() => {})
  }, [])

  const loadSessions = async () => {
    setSessionsLoading(true)
    try {
      const res = await getPracticeSessions()
      setSessions(res.data)
    } catch { /* ignore */ }
    setSessionsLoading(false)
  }

  useEffect(() => {
    loadSessions()
  }, [])

  const handleGenerate = async () => {
    setLoading(true)
    setResult(null)
    setAnswers({})
    try {
      const res = await generatePractice({
        subject_id: subjectId,
        knowledge_point: practiceMode === 'custom' ? knowledgePoint : '',
        total_questions: count,
        practice_mode: practiceMode,
      })
      setSession(res.data)
      const qs = JSON.parse(res.data.questions_json)
      setQuestions(qs)
      setView('practice')
      loadSessions()
    } catch {
      message.error('生成失败')
    }
    setLoading(false)
  }

  const handleSubmit = async () => {
    if (Object.keys(answers).length === 0) {
      message.warning('请至少回答一道题')
      return
    }
    try {
      const res = await submitPractice(session.id, answers)
      setResult(res.data)
      setQuestions(res.data.details)
      setView('result')
      loadSessions()
    } catch {
      message.error('提交失败')
    }
  }

  const handleAbandon = async () => {
    if (!session) return
    try {
      await abandonPractice(session.id)
      message.success('已废弃该练习')
      handleReset()
      loadSessions()
    } catch {
      message.error('操作失败')
    }
  }

  const handleReset = () => {
    setSession(null)
    setQuestions([])
    setAnswers({})
    setResult(null)
    setView('new')
  }

  // 继续/查看某个历史练习
  const handleResumeSession = async (record) => {
    try {
      const res = await getPracticeSession(record.id)
      const s = res.data
      setSession(s)
      const qs = JSON.parse(s.questions_json)
      setQuestions(qs)
      if (s.status === 'completed') {
        // 重建结果
        const correct = qs.filter(q => q.is_correct === true).length
        setResult({
          total: qs.length,
          correct,
          score: qs.length > 0 ? Math.round(correct / qs.length * 100) : 0,
          details: qs,
        })
        // 恢复用户答案
        const savedAnswers = {}
        qs.forEach(q => { if (q.user_answer) savedAnswers[String(q.index)] = q.user_answer })
        setAnswers(savedAnswers)
        setView('result')
      } else if (s.status === 'practicing') {
        // 恢复已填答案
        const savedAnswers = {}
        qs.forEach(q => { if (q.user_answer) savedAnswers[String(q.index)] = q.user_answer })
        setAnswers(savedAnswers)
        setView('practice')
      }
    } catch {
      message.error('加载练习失败')
    }
  }

  const handleAbandonFromHistory = async (record) => {
    try {
      await abandonPractice(record.id)
      message.success('已废弃')
      loadSessions()
    } catch {
      message.error('操作失败')
    }
  }

  const subjectName = (id) => {
    const s = subjects.find(s => s.id === id)
    return s ? `${s.icon} ${s.name}` : id
  }

  const columns = [
    {
      title: '时间', dataIndex: 'created_at', width: 150,
      render: (v) => new Date(v).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }),
    },
    { title: '学科', dataIndex: 'subject_id', width: 80, render: (id) => subjectName(id) },
    {
      title: '类型', dataIndex: 'practice_mode', width: 100,
      render: (v) => <Tag>{MODE_MAP[v] || '自定义'}</Tag>,
    },
    { title: '知识点', dataIndex: 'knowledge_point', ellipsis: true },
    { title: '题数', dataIndex: 'total_questions', width: 60 },
    {
      title: '状态', dataIndex: 'status', width: 90,
      render: (s) => {
        const info = STATUS_MAP[s] || { text: s, color: 'default' }
        return <Tag color={info.color}>{info.text}</Tag>
      },
    },
    {
      title: '得分', width: 80,
      render: (_, r) => r.status === 'completed' && r.total_questions > 0
        ? `${Math.round(r.correct_count / r.total_questions * 100)}分`
        : '-',
    },
    {
      title: '操作', width: 120,
      render: (_, r) => (
        <Space size="small">
          {r.status === 'practicing' && (
            <Button type="link" size="small" icon={<PlayCircleOutlined />} onClick={() => handleResumeSession(r)}>继续</Button>
          )}
          {r.status === 'completed' && (
            <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleResumeSession(r)}>查看</Button>
          )}
          {r.status === 'practicing' && (
            <Popconfirm title="确定废弃此练习？" onConfirm={() => handleAbandonFromHistory(r)}>
              <Button type="link" size="small" danger icon={<DeleteOutlined />}>废弃</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>🎯 智能练习</Title>
        {(view === 'new' || view === 'history') && (
          <Segmented
            value={view}
            onChange={setView}
            options={[
              { label: '新建练习', value: 'new', icon: <PlusOutlined /> },
              { label: '练习记录', value: 'history', icon: <HistoryOutlined /> },
            ]}
          />
        )}
      </div>

      {/* 新建练习 */}
      {view === 'new' && (
        <Card style={{ borderRadius: 16, maxWidth: 600 }}>
          <Title level={5}>生成练习题</Title>
          {aiEnabled && (
            <Alert
              type="success"
              icon={<RobotOutlined />}
              showIcon
              message="AI 出题已启用"
              description="题目将由大模型动态生成，更丰富更智能"
              style={{ marginBottom: 16, borderRadius: 8 }}
            />
          )}
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Text>练习类型：</Text>
              <div style={{ marginTop: 8 }}>
                <Radio.Group value={practiceMode} onChange={(e) => setPracticeMode(e.target.value)}>
                  {PRACTICE_MODES.map(m => (
                    <Radio.Button key={m.value} value={m.value} style={{ borderRadius: 8, marginRight: 8 }}>
                      {m.label}
                    </Radio.Button>
                  ))}
                </Radio.Group>
              </div>
              {practiceMode === 'wrong_review' && (
                <div style={{ marginTop: 8, padding: '8px 12px', background: '#fff7e6', borderRadius: 8, fontSize: 13, color: '#d48806' }}>
                  💡 将从你的错题本中提取题目，生成相似的变式题来帮助巩固
                </div>
              )}
              {practiceMode === 'important_review' && (
                <div style={{ marginTop: 8, padding: '8px 12px', background: '#e6f7ff', borderRadius: 8, fontSize: 13, color: '#096dd9' }}>
                  💡 将从你的学习记录中提取重点和薄弱知识点，针对性出题
                </div>
              )}
            </div>
            <div>
              <Text>学科：</Text>
              <Select value={subjectId} onChange={setSubjectId} style={{ width: 200, marginLeft: 8 }}>
                {subjects.map((s) => <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>)}
              </Select>
            </div>
            {practiceMode === 'custom' && (
              <div>
                <Text>知识点：</Text>
                <Input
                  value={knowledgePoint}
                  onChange={(e) => setKnowledgePoint(e.target.value)}
                  placeholder={
                    subjectId === 'math' ? '如：加减法、乘法、除法、分数' :
                    subjectId === 'english' ? '如：单词、动物、颜色、语法、句子翻译' :
                    subjectId === 'chinese' ? '如：拼音、成语、古诗' :
                    subjectId === 'science' ? '如：天文、生物、物理、人体' :
                    '输入知识点（可选）'
                  }
                  style={{ width: 280, marginLeft: 8 }}
                />
              </div>
            )}
            <div>
              <Text>题目数量：</Text>
              <InputNumber value={count} onChange={setCount} min={1} max={20} style={{ marginLeft: 8 }} />
            </div>
            <Button type="primary" icon={<ThunderboltOutlined />} onClick={handleGenerate} loading={loading}
              size="large" style={{ marginTop: 8 }}>
              开始出题
            </Button>
          </Space>
        </Card>
      )}

      {/* 练习记录 */}
      {view === 'history' && (
        <Card style={{ borderRadius: 16 }}>
          <Table
            dataSource={sessions}
            columns={columns}
            rowKey="id"
            loading={sessionsLoading}
            pagination={{ pageSize: 10 }}
            size="small"
          />
        </Card>
      )}

      {/* 答题区 */}
      {view === 'practice' && session && (
        <div>
          <Card style={{ borderRadius: 16, marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                <Text type="secondary">共 {questions.length} 道题</Text>
                <Tag>{MODE_MAP[session.practice_mode] || '自定义'}</Tag>
                {session.question_type === 'AI出题' && (
                  <Tag color="purple" icon={<RobotOutlined />}>AI出题</Tag>
                )}
                {session.question_type !== 'AI出题' && (
                  <Tag color="blue">内置题库</Tag>
                )}
              </Space>
              <Space>
                <Popconfirm title="确定废弃此练习？" onConfirm={handleAbandon}>
                  <Button danger>废弃练习</Button>
                </Popconfirm>
                <Button type="primary" onClick={handleSubmit}>提交答案</Button>
              </Space>
            </div>
          </Card>

          {questions.map((q, i) => (
            <Card key={i} style={{ borderRadius: 12, marginBottom: 12 }}>
              <div style={{ marginBottom: 12 }}>
                <Tag color="blue">{q.type}</Tag>
                <Text strong style={{ fontSize: 16 }}>第{q.index}题：{q.question}</Text>
              </div>

              {q.options ? (
                <Radio.Group
                  value={answers[String(q.index)]}
                  onChange={(e) => setAnswers({ ...answers, [String(q.index)]: e.target.value })}
                >
                  <Space direction="vertical">
                    {q.options.map((opt, j) => {
                      const cleanOpt = opt.replace(/^[A-Da-d][.、.\s)\]】]+\s*/, '')
                      return (
                        <Radio key={j} value={opt}>{String.fromCharCode(65 + j)}. {cleanOpt}</Radio>
                      )
                    })}
                  </Space>
                </Radio.Group>
              ) : q.type === '判断题' ? (
                <Radio.Group
                  value={answers[String(q.index)]}
                  onChange={(e) => setAnswers({ ...answers, [String(q.index)]: e.target.value })}
                >
                  <Space>
                    <Radio value="对">✅ 对</Radio>
                    <Radio value="错">❌ 错</Radio>
                  </Space>
                </Radio.Group>
              ) : (
                <Input
                  placeholder="输入你的答案"
                  value={answers[String(q.index)] || ''}
                  onChange={(e) => setAnswers({ ...answers, [String(q.index)]: e.target.value })}
                  style={{ maxWidth: 300 }}
                />
              )}
            </Card>
          ))}

          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Button type="primary" size="large" onClick={handleSubmit}>提交答案</Button>
          </div>
        </div>
      )}

      {/* 结果展示 */}
      {view === 'result' && result && (
        <div>
          <Card style={{ borderRadius: 16, textAlign: 'center', marginBottom: 24 }}>
            <Result
              status={result.score >= 60 ? 'success' : 'warning'}
              title={`得分：${result.score}分`}
              subTitle={`答对 ${result.correct} / ${result.total} 题`}
              extra={[
                <Button type="primary" key="retry" onClick={handleReset}>再练一次</Button>,
                <Button key="history" onClick={() => { handleReset(); setView('history') }}>查看记录</Button>,
              ]}
            />
            <Progress
              percent={result.score}
              strokeColor={result.score >= 80 ? '#22c55e' : result.score >= 60 ? '#eab308' : '#ef4444'}
              style={{ maxWidth: 400, margin: '0 auto' }}
            />
          </Card>

          <Divider>答题详情</Divider>

          {questions.map((q, i) => (
            <Card
              key={i}
              style={{
                borderRadius: 12,
                marginBottom: 12,
                borderLeft: `4px solid ${q.is_correct ? '#22c55e' : '#ef4444'}`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <Text strong>第{q.index}题：{q.question}</Text>
                  <div style={{ marginTop: 8 }}>
                    <Text>你的答案：</Text>
                    <Text type={q.is_correct ? 'success' : 'danger'} strong>{q.user_answer || '未作答'}</Text>
                    {!q.is_correct && (
                      <>
                        <Text style={{ marginLeft: 16 }}>正确答案：</Text>
                        <Text type="success" strong>{q.answer}</Text>
                      </>
                    )}
                  </div>
                </div>
                {q.is_correct
                  ? <CheckCircleOutlined style={{ fontSize: 24, color: '#22c55e' }} />
                  : <CloseCircleOutlined style={{ fontSize: 24, color: '#ef4444' }} />}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
