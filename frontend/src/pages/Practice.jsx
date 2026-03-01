import React, { useEffect, useState } from 'react'
import {
  Card, Button, Select, InputNumber, Input, Radio, Tag, Space, message,
  Typography, Result, Progress, Divider, Empty, Spin, Alert,
} from 'antd'
import { ThunderboltOutlined, CheckCircleOutlined, CloseCircleOutlined, RobotOutlined } from '@ant-design/icons'
import { generatePractice, submitPractice, getSubjects, getLLMConfig } from '../api'

const { Title, Text, Paragraph } = Typography

export default function Practice() {
  const [subjects, setSubjects] = useState([])
  const [subjectId, setSubjectId] = useState('math')
  const [knowledgePoint, setKnowledgePoint] = useState('')
  const [count, setCount] = useState(5)
  const [session, setSession] = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(false)

  useEffect(() => {
    getSubjects().then((res) => setSubjects(res.data)).catch(() => {})
    getLLMConfig().then((res) => {
      if (res.data && res.data.enabled) setAiEnabled(true)
    }).catch(() => {})
  }, [])

  const handleGenerate = async () => {
    setLoading(true)
    setResult(null)
    setAnswers({})
    try {
      const res = await generatePractice({
        subject_id: subjectId,
        knowledge_point: knowledgePoint,
        total_questions: count,
      })
      setSession(res.data)
      const qs = JSON.parse(res.data.questions_json)
      setQuestions(qs)
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
    } catch {
      message.error('提交失败')
    }
  }

  const handleReset = () => {
    setSession(null)
    setQuestions([])
    setAnswers({})
    setResult(null)
  }

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>🎯 智能练习</Title>

      {/* 出题设置 */}
      {!session && (
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
              <Text>学科：</Text>
              <Select value={subjectId} onChange={setSubjectId} style={{ width: 200, marginLeft: 8 }}>
                {subjects.map((s) => <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>)}
              </Select>
            </div>
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

      {/* 答题区 */}
      {session && !result && (
        <div>
          <Card style={{ borderRadius: 16, marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Space>
                <Text type="secondary">共 {questions.length} 道题</Text>
                {session.question_type === 'AI出题' && (
                  <Tag color="purple" icon={<RobotOutlined />}>AI出题</Tag>
                )}
                {session.question_type !== 'AI出题' && (
                  <Tag color="blue">内置题库</Tag>
                )}
              </Space>
              <Space>
                <Button onClick={handleReset}>重新出题</Button>
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
      {result && (
        <div>
          <Card style={{ borderRadius: 16, textAlign: 'center', marginBottom: 24 }}>
            <Result
              status={result.score >= 60 ? 'success' : 'warning'}
              title={`得分：${result.score}分`}
              subTitle={`答对 ${result.correct} / ${result.total} 题`}
              extra={[
                <Button type="primary" key="retry" onClick={handleReset}>再练一次</Button>,
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
