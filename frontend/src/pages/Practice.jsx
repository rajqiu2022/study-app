import React, { useEffect, useState, useRef } from 'react'
import {
  Card, Button, Select, InputNumber, Input, Radio, Tag, Space, message,
  Typography, Result, Progress, Divider, Spin, Alert, Table, Popconfirm, Segmented,
} from 'antd'
import {
  ThunderboltOutlined, CheckCircleOutlined, CloseCircleOutlined, RobotOutlined,
  HistoryOutlined, DeleteOutlined, EyeOutlined, PlayCircleOutlined, PlusOutlined,
  SoundOutlined, LoadingOutlined, FileTextOutlined,
} from '@ant-design/icons'
import { generatePractice, submitPractice, abandonPractice, getPracticeSession, getPracticeSessions, getSubjects, getLLMConfig, generateTTS, getCurriculum, getCurrentUser } from '../api'

const { Title, Text, Paragraph } = Typography

const PRACTICE_MODES = [
  { label: '📝 错题练习', value: 'wrong_review' },
  { label: '⭐ 重点知识练习', value: 'important_review' },
  { label: '📋 综合练习', value: 'exam' },
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
  exam: '综合练习',
}

// 听力播放组件
function ListeningPlayer({ text }) {
  const [audioUrl, setAudioUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [playCount, setPlayCount] = useState(0)
  const audioRef = useRef(null)
  const maxPlays = 3

  const handlePlay = async () => {
    if (playCount >= maxPlays) {
      message.warning('本题听力已播放3次')
      return
    }
    if (!audioUrl) {
      setLoading(true)
      try {
        const res = await generateTTS(text, 'en-US-JennyNeural')
        const url = res.data.url
        setAudioUrl(url)
        setLoading(false)
        setTimeout(() => {
          if (audioRef.current) {
            audioRef.current.play()
            setPlayCount(c => c + 1)
          }
        }, 100)
      } catch {
        message.error('语音生成失败')
        setLoading(false)
      }
    } else {
      if (audioRef.current) {
        audioRef.current.currentTime = 0
        audioRef.current.play()
        setPlayCount(c => c + 1)
      }
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
      <Button
        icon={loading ? <LoadingOutlined /> : <SoundOutlined />}
        onClick={handlePlay}
        disabled={loading || playCount >= maxPlays}
        type="primary"
        ghost
      >
        {loading ? '生成中...' : `播放听力`}
      </Button>
      <Text type="secondary" style={{ fontSize: 12 }}>
        （已播放 {playCount}/{maxPlays} 次）
      </Text>
      {audioUrl && <audio ref={audioRef} src={audioUrl} />}
    </div>
  )
}

export default function Practice() {
  const [subjects, setSubjects] = useState([])
  const [subjectId, setSubjectId] = useState('math')
  const [knowledgePoint, setKnowledgePoint] = useState('')
  const [count, setCount] = useState(5)
  const [practiceMode, setPracticeMode] = useState('exam')
  const [session, setSession] = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(false)
  const [view, setView] = useState('new') // new / history / practice / result
  const [sessions, setSessions] = useState([])
  const [sessionsLoading, setSessionsLoading] = useState(false)
  const [semester, setSemester] = useState(null) // 上册/下册
  const [units, setUnits] = useState([]) // 单元列表
  const [selectedUnit, setSelectedUnit] = useState(null) // 选中的单元

  useEffect(() => {
    getSubjects().then((res) => setSubjects(res.data)).catch(() => {})
    getLLMConfig().then((res) => {
      if (res.data && res.data.enabled) setAiEnabled(true)
    }).catch(() => {})
  }, [])

  // 加载课本大纲单元列表
  useEffect(() => {
    if (!semester) {
      setUnits([])
      setSelectedUnit(null)
      return
    }
    const user = getCurrentUser()
    const grade = user?.grade || '三年级'
    getCurriculum(grade, subjectId, semester).then((res) => {
      const data = res.data
      const semesterUnits = data[semester] || []
      setUnits(semesterUnits)
      setSelectedUnit(null)
    }).catch(() => {
      setUnits([])
      setSelectedUnit(null)
    })
  }, [semester, subjectId])

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

  const isExamMode = practiceMode === 'exam'

  const handleGenerate = async () => {
    setLoading(true)
    setResult(null)
    setAnswers({})
    try {
      const res = await generatePractice({
        subject_id: subjectId,
        knowledge_point: '',
        total_questions: isExamMode ? 25 : count,
        practice_mode: practiceMode,
        semester: semester || undefined,
        unit: selectedUnit || undefined,
      })
      setSession(res.data)
      const qs = JSON.parse(res.data.questions_json)
      setQuestions(qs)
      setView('practice')
      loadSessions()
    } catch {
      message.error('生成失败，请重试')
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

  const handleResumeSession = async (record) => {
    try {
      const res = await getPracticeSession(record.id)
      const s = res.data
      setSession(s)
      const qs = JSON.parse(s.questions_json)
      setQuestions(qs)
      if (s.status === 'completed') {
        const correct = qs.filter(q => q.is_correct === true).length
        const totalScore = qs.reduce((sum, q) => sum + (q.score || 0), 0)
        const earnedScore = qs.filter(q => q.is_correct).reduce((sum, q) => sum + (q.score || 0), 0)
        setResult({
          total: qs.length,
          correct,
          score: totalScore > 0 ? earnedScore : Math.round(correct / qs.length * 100),
          total_score: totalScore || 100,
          earned_score: earnedScore,
          details: qs,
        })
        const savedAnswers = {}
        qs.forEach(q => { if (q.user_answer) savedAnswers[String(q.index)] = q.user_answer })
        setAnswers(savedAnswers)
        setView('result')
      } else if (s.status === 'practicing') {
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

  // 将题目按 section 分组
  const groupBySection = (qs) => {
    const groups = []
    let currentSection = null
    let currentGroup = null
    for (const q of qs) {
      const sec = q.section || ''
      if (sec !== currentSection) {
        currentSection = sec
        currentGroup = { section: sec, questions: [], readingPassage: null }
        groups.push(currentGroup)
      }
      if (q.reading_passage && !currentGroup.readingPassage) {
        currentGroup.readingPassage = q.reading_passage
      }
      currentGroup.questions.push(q)
    }
    return groups
  }

  // 获取大题标题
  const getSectionTitle = (section, qs) => {
    if (!qs || qs.length === 0) return section
    const type = qs[0].type || ''
    const totalScore = qs.reduce((s, q) => s + (q.score || 0), 0)
    return `${section}、${type}（共${qs.length}题，共${totalScore}分）`
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

  // 渲染单题答题区
  const renderQuestionInput = (q) => {
    if (q.options) {
      return (
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
      )
    }
    if (q.type === '判断题') {
      return (
        <Radio.Group
          value={answers[String(q.index)]}
          onChange={(e) => setAnswers({ ...answers, [String(q.index)]: e.target.value })}
        >
          <Space>
            <Radio value="对">✅ 对</Radio>
            <Radio value="错">❌ 错</Radio>
          </Space>
        </Radio.Group>
      )
    }
    // 应用题/计算题/简答题/实验题用多行输入
    const multiLineTypes = ['应用题', '计算题', '简答题', '实验题']
    if (multiLineTypes.includes(q.type)) {
      return (
        <Input.TextArea
          placeholder="请写出解题过程和答案"
          value={answers[String(q.index)] || ''}
          onChange={(e) => setAnswers({ ...answers, [String(q.index)]: e.target.value })}
          autoSize={{ minRows: 2, maxRows: 6 }}
          style={{ maxWidth: 500 }}
        />
      )
    }
    return (
      <Input
        placeholder="输入你的答案"
        value={answers[String(q.index)] || ''}
        onChange={(e) => setAnswers({ ...answers, [String(q.index)]: e.target.value })}
        style={{ maxWidth: 300 }}
      />
    )
  }

  // 计算已答题数
  const answeredCount = Object.keys(answers).filter(k => answers[k] && answers[k].trim()).length

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
              {isExamMode && (
                <div style={{ marginTop: 8, padding: '8px 12px', background: '#f6ffed', borderRadius: 8, fontSize: 13, color: '#389e0d' }}>
                  📋 模拟正式考试，满分100分。
                  {subjectId === 'math' && '包括填空题、选择题、判断题、计算题、应用题'}
                  {subjectId === 'english' && '包括听力、选择题、判断题、填空题、阅读理解'}
                  {subjectId === 'chinese' && '包括填空题、选择题、判断题、古诗词填空、阅读理解'}
                  {subjectId === 'science' && '包括填空题、选择题、判断题、简答题、实验题'}
                </div>
              )}
            </div>
            <div>
              <Text>学科：</Text>
              <Select value={subjectId} onChange={(v) => { setSubjectId(v); setSemester(null); setSelectedUnit(null) }} style={{ width: 200, marginLeft: 8 }}>
                {subjects.map((s) => <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>)}
              </Select>
            </div>
            {practiceMode !== 'wrong_review' && practiceMode !== 'important_review' && (
              <div>
                <Text>课本范围：</Text>
                <Select
                  value={semester}
                  onChange={(v) => { setSemester(v); setSelectedUnit(null) }}
                  style={{ width: 120, marginLeft: 8 }}
                  allowClear
                  placeholder="不限"
                >
                  <Select.Option value="上册">上册</Select.Option>
                  <Select.Option value="下册">下册</Select.Option>
                </Select>
                {semester && units.length > 0 && (
                  <Select
                    value={selectedUnit}
                    onChange={setSelectedUnit}
                    style={{ width: 280, marginLeft: 8 }}
                    allowClear
                    placeholder="全部单元"
                  >
                    {units.map((u) => (
                      <Select.Option key={u.unit} value={u.unit}>{u.unit}</Select.Option>
                    ))}
                  </Select>
                )}
                {semester && (
                  <div style={{ marginTop: 6, padding: '6px 12px', background: '#f0f5ff', borderRadius: 8, fontSize: 12, color: '#1677ff' }}>
                    📖 将按照 {getCurrentUser()?.grade || '三年级'}{semester}
                    {selectedUnit ? `「${selectedUnit}」` : '全部单元'}的课本内容出题
                  </div>
                )}
              </div>
            )}
            {!isExamMode && practiceMode !== 'wrong_review' && practiceMode !== 'important_review' && (
              <div>
                <Text>题目数量：</Text>
                <InputNumber value={count} onChange={setCount} min={1} max={20} style={{ marginLeft: 8 }} />
              </div>
            )}
            <Button type="primary" icon={<ThunderboltOutlined />} onClick={handleGenerate} loading={loading}
              size="large" style={{ marginTop: 8 }}>
              {loading ? (isExamMode ? '正在生成试卷...' : '正在出题...') : (isExamMode ? '开始考试' : '开始出题')}
            </Button>
            {loading && isExamMode && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                综合试卷生成需要较长时间，请耐心等待...
              </Text>
            )}
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
                {session.practice_mode === 'exam' && (
                  <Tag color="red">满分100分</Tag>
                )}
                {session.question_type === 'AI出题' && (
                  <Tag color="purple" icon={<RobotOutlined />}>AI出题</Tag>
                )}
                <Text type="secondary">已答 {answeredCount}/{questions.length}</Text>
              </Space>
              <Space>
                <Popconfirm title="确定废弃此练习？" onConfirm={handleAbandon}>
                  <Button danger>废弃练习</Button>
                </Popconfirm>
                <Button type="primary" onClick={handleSubmit}>提交答案</Button>
              </Space>
            </div>
            {session.practice_mode === 'exam' && (
              <Progress
                percent={Math.round(answeredCount / questions.length * 100)}
                size="small"
                style={{ marginTop: 8 }}
                format={() => `${answeredCount}/${questions.length}`}
              />
            )}
          </Card>

          {/* 按大题分组展示 */}
          {session.practice_mode === 'exam' ? (
            groupBySection(questions).map((group, gi) => (
              <div key={gi} style={{ marginBottom: 24 }}>
                <Title level={5} style={{
                  background: '#f0f5ff', padding: '8px 16px', borderRadius: 8,
                  borderLeft: '4px solid #1677ff', marginBottom: 12,
                }}>
                  {getSectionTitle(group.section, group.questions)}
                </Title>

                {/* 阅读理解短文 */}
                {group.readingPassage && (
                  <Card style={{ borderRadius: 12, marginBottom: 12, background: '#fafafa' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                      <FileTextOutlined style={{ fontSize: 18, color: '#1677ff', marginTop: 2 }} />
                      <div>
                        <Text strong style={{ color: '#1677ff' }}>阅读短文：</Text>
                        <Paragraph style={{ marginTop: 8, whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                          {group.readingPassage}
                        </Paragraph>
                      </div>
                    </div>
                  </Card>
                )}

                {group.questions.map((q) => (
                  <Card key={q.index} style={{ borderRadius: 12, marginBottom: 8 }}>
                    <div style={{ marginBottom: 12 }}>
                      <Space>
                        <Tag color="blue">{q.type}</Tag>
                        <Tag color="orange">{q.score}分</Tag>
                      </Space>
                      <div style={{ marginTop: 8 }}>
                        <Text strong style={{ fontSize: 15 }}>第{q.index}题：{q.question}</Text>
                      </div>
                    </div>
                    {/* 听力题播放按钮 */}
                    {q.listening_text && <ListeningPlayer text={q.listening_text} />}
                    {renderQuestionInput(q)}
                  </Card>
                ))}
              </div>
            ))
          ) : (
            /* 普通模式（非考试） */
            questions.map((q) => (
              <Card key={q.index} style={{ borderRadius: 12, marginBottom: 12 }}>
                <div style={{ marginBottom: 12 }}>
                  <Tag color="blue">{q.type}</Tag>
                  {q.score > 0 && <Tag color="orange">{q.score}分</Tag>}
                  <Text strong style={{ fontSize: 16 }}>第{q.index}题：{q.question}</Text>
                </div>
                {q.listening_text && <ListeningPlayer text={q.listening_text} />}
                {renderQuestionInput(q)}
              </Card>
            ))
          )}

          <div style={{ textAlign: 'center', marginTop: 16, paddingBottom: 24 }}>
            <Space>
              <Popconfirm title="确定废弃此练习？" onConfirm={handleAbandon}>
                <Button danger size="large">废弃练习</Button>
              </Popconfirm>
              <Button type="primary" size="large" onClick={handleSubmit}>
                提交答案 ({answeredCount}/{questions.length})
              </Button>
            </Space>
          </div>
        </div>
      )}

      {/* 结果展示 */}
      {view === 'result' && result && (
        <div>
          <Card style={{ borderRadius: 16, textAlign: 'center', marginBottom: 24 }}>
            <Result
              status={result.all_correct || result.correct === result.total ? 'success' : result.score >= 60 ? 'success' : 'warning'}
              title={
                result.all_correct || result.correct === result.total
                  ? '🎉 全部答对！太棒了！'
                  : result.total_score && result.total_score > 0
                    ? `得分：${result.score} / ${result.total_score} 分`
                    : `得分：${result.score}分`
              }
              subTitle={
                result.all_correct || result.correct === result.total
                  ? `答对 ${result.correct} / ${result.total} 题，满分 ${result.total_score || 100} 分`
                  : `答对 ${result.correct} / ${result.total} 题`
              }
              extra={[
                <Button type="primary" key="retry" onClick={handleReset}>再练一次</Button>,
                <Button key="history" onClick={() => { handleReset(); setView('history') }}>查看记录</Button>,
              ]}
            />
            <Progress
              percent={result.total_score > 0 ? Math.round(result.score / result.total_score * 100) : result.score}
              strokeColor={result.score >= 80 ? '#22c55e' : result.score >= 60 ? '#eab308' : '#ef4444'}
              style={{ maxWidth: 400, margin: '0 auto' }}
            />
          </Card>

          <Divider>答题详情</Divider>

          {/* 按大题分组展示结果 */}
          {session?.practice_mode === 'exam' ? (
            groupBySection(questions).map((group, gi) => (
              <div key={gi} style={{ marginBottom: 24 }}>
                <Title level={5} style={{
                  background: '#f0f5ff', padding: '8px 16px', borderRadius: 8,
                  borderLeft: '4px solid #1677ff', marginBottom: 12,
                }}>
                  {getSectionTitle(group.section, group.questions)}
                  <span style={{ float: 'right', fontSize: 14 }}>
                    得分：{group.questions.filter(q => q.is_correct).reduce((s, q) => s + (q.score || 0), 0)}/{group.questions.reduce((s, q) => s + (q.score || 0), 0)}
                  </span>
                </Title>

                {group.readingPassage && (
                  <Card style={{ borderRadius: 12, marginBottom: 12, background: '#fafafa' }}>
                    <Text strong style={{ color: '#1677ff' }}>阅读短文：</Text>
                    <Paragraph style={{ marginTop: 8, whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                      {group.readingPassage}
                    </Paragraph>
                  </Card>
                )}

                {group.questions.map((q) => (
                  <Card
                    key={q.index}
                    style={{
                      borderRadius: 12, marginBottom: 8,
                      borderLeft: `4px solid ${q.is_correct ? '#22c55e' : '#ef4444'}`,
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <Space style={{ marginBottom: 4 }}>
                          <Tag color="blue">{q.type}</Tag>
                          <Tag color="orange">{q.score}分</Tag>
                          {q.is_correct
                            ? <Tag color="success">✅ 正确</Tag>
                            : <Tag color="error">❌ 错误</Tag>}
                        </Space>
                        <div style={{ marginTop: 4 }}>
                          <Text strong>第{q.index}题：{q.question}</Text>
                        </div>
                        {q.listening_text && (
                          <div style={{ marginTop: 4 }}>
                            <Text type="secondary" style={{ fontSize: 12 }}>听力原文：{q.listening_text}</Text>
                          </div>
                        )}
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
            ))
          ) : (
            questions.map((q, i) => (
              <Card
                key={i}
                style={{
                  borderRadius: 12, marginBottom: 12,
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
            ))
          )}
        </div>
      )}
    </div>
  )
}
