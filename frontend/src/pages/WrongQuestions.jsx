import React, { useEffect, useState } from 'react'
import {
  Card, Table, Button, Modal, Form, Input, Select, DatePicker, InputNumber, Tag,
  Space, Popconfirm, message, Typography, Segmented, Badge, Tooltip,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckOutlined, EyeOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import {
  getWrongQuestions, createWrongQuestion, updateWrongQuestion,
  reviewWrongQuestion, deleteWrongQuestion, getSubjects,
} from '../api'

const { Title, Paragraph } = Typography
const { TextArea } = Input

const ERROR_TYPES = ['计算错误', '概念不清', '粗心大意', '方法错误', '审题不清', '其他']
const DIFFICULTY_MAP = { 1: { text: '简单', color: 'green' }, 2: { text: '中等', color: 'orange' }, 3: { text: '困难', color: 'red' } }

export default function WrongQuestions() {
  const [list, setList] = useState([])
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [detail, setDetail] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [filterSubject, setFilterSubject] = useState(null)
  const [filterResolved, setFilterResolved] = useState(null)
  const [form] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterSubject) params.subject_id = filterSubject
      if (filterResolved !== null) params.is_resolved = filterResolved
      const [wqRes, subRes] = await Promise.all([getWrongQuestions(params), getSubjects()])
      setList(wqRes.data)
      setSubjects(subRes.data)
    } catch { message.error('加载失败') }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [filterSubject, filterResolved])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const payload = { ...values, mistake_date: values.mistake_date?.format('YYYY-MM-DD') }
      if (editingId) {
        await updateWrongQuestion(editingId, payload)
        message.success('更新成功')
      } else {
        await createWrongQuestion(payload)
        message.success('添加成功')
      }
      setModalOpen(false)
      setEditingId(null)
      form.resetFields()
      fetchData()
    } catch {}
  }

  const handleReview = async (id) => {
    await reviewWrongQuestion(id)
    message.success('已复习+1')
    fetchData()
  }

  const handleResolve = async (id) => {
    await updateWrongQuestion(id, { is_resolved: true })
    message.success('已标记为已解决')
    fetchData()
  }

  const subjectName = (id) => subjects.find((s) => s.id === id)?.name || id

  const columns = [
    { title: '学科', dataIndex: 'subject_id', width: 80, render: (id) => subjectName(id) },
    { title: '题目内容', dataIndex: 'question_content', ellipsis: true },
    { title: '知识点', dataIndex: 'knowledge_point', width: 120, ellipsis: true },
    {
      title: '错误类型', dataIndex: 'error_type', width: 100,
      render: (t) => <Tag>{t}</Tag>,
    },
    {
      title: '难度', dataIndex: 'difficulty', width: 70,
      render: (d) => <Tag color={DIFFICULTY_MAP[d]?.color}>{DIFFICULTY_MAP[d]?.text}</Tag>,
    },
    {
      title: '状态', dataIndex: 'is_resolved', width: 80,
      render: (v) => v ? <Badge status="success" text="已解决" /> : <Badge status="error" text="未解决" />,
    },
    { title: '复习', dataIndex: 'review_count', width: 60, render: (v) => `${v}次` },
    {
      title: '操作', width: 180,
      render: (_, r) => (
        <Space>
          <Tooltip title="查看详情"><Button type="link" size="small" icon={<EyeOutlined />} onClick={() => { setDetail(r); setDetailOpen(true) }} /></Tooltip>
          <Tooltip title="复习一次"><Button type="link" size="small" icon={<CheckOutlined />} onClick={() => handleReview(r.id)} /></Tooltip>
          <Tooltip title="编辑"><Button type="link" size="small" icon={<EditOutlined />} onClick={() => {
            setEditingId(r.id)
            form.setFieldsValue({ ...r, mistake_date: r.mistake_date ? dayjs(r.mistake_date) : null })
            setModalOpen(true)
          }} /></Tooltip>
          <Popconfirm title="确认删除？" onConfirm={() => deleteWrongQuestion(r.id).then(fetchData)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>❌ 错题本</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => {
          setEditingId(null); form.resetFields()
          form.setFieldsValue({ difficulty: 2, error_type: '概念不清', mistake_date: dayjs() })
          setModalOpen(true)
        }}>添加错题</Button>
      </div>

      <Card style={{ borderRadius: 16 }}>
        <Space style={{ marginBottom: 16 }} wrap>
          <Segmented
            options={[{ label: '全部', value: '' }, ...subjects.map((s) => ({ label: `${s.icon} ${s.name}`, value: s.id }))]}
            value={filterSubject || ''}
            onChange={(v) => setFilterSubject(v || null)}
          />
          <Segmented
            options={[{ label: '全部', value: 'all' }, { label: '未解决', value: 'false' }, { label: '已解决', value: 'true' }]}
            value={filterResolved === null ? 'all' : String(filterResolved)}
            onChange={(v) => setFilterResolved(v === 'all' ? null : v === 'true')}
          />
        </Space>
        <Table columns={columns} dataSource={list} rowKey="id" loading={loading}
          pagination={{ pageSize: 10, showTotal: (t) => `共 ${t} 条` }} size="middle" />
      </Card>

      {/* 添加/编辑弹窗 */}
      <Modal title={editingId ? '编辑错题' : '添加错题'} open={modalOpen}
        onOk={handleSave} onCancel={() => { setModalOpen(false); setEditingId(null) }}
        okText="保存" cancelText="取消" width={560}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="subject_id" label="学科" rules={[{ required: true }]}>
            <Select placeholder="选择学科">
              {subjects.map((s) => <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="question_content" label="题目内容" rules={[{ required: true }]}>
            <TextArea rows={3} placeholder="把做错的题目写在这里..." />
          </Form.Item>
          <Form.Item name="knowledge_point" label="相关知识点">
            <Input placeholder="如：分数加减法" />
          </Form.Item>
          <Form.Item name="my_answer" label="我的答案">
            <Input placeholder="我当时写的答案" />
          </Form.Item>
          <Form.Item name="correct_answer" label="正确答案">
            <Input placeholder="正确答案是什么" />
          </Form.Item>
          <Form.Item name="error_type" label="错误原因">
            <Select options={ERROR_TYPES.map((t) => ({ label: t, value: t }))} />
          </Form.Item>
          <Form.Item name="analysis" label="解题分析">
            <TextArea rows={2} placeholder="为什么会做错？正确的思路是..." />
          </Form.Item>
          <Form.Item name="difficulty" label="难度">
            <Select options={[{ label: '简单', value: 1 }, { label: '中等', value: 2 }, { label: '困难', value: 3 }]} />
          </Form.Item>
          <Form.Item name="mistake_date" label="做错日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情弹窗 */}
      <Modal title="错题详情" open={detailOpen} onCancel={() => setDetailOpen(false)} footer={
        detail && !detail.is_resolved ? (
          <Button type="primary" onClick={() => { handleResolve(detail.id); setDetailOpen(false) }}>
            标记为已解决
          </Button>
        ) : null
      }>
        {detail && (
          <div>
            <Paragraph><strong>学科：</strong>{subjectName(detail.subject_id)}</Paragraph>
            <Paragraph><strong>题目：</strong>{detail.question_content}</Paragraph>
            <Paragraph><strong>知识点：</strong>{detail.knowledge_point || '未标注'}</Paragraph>
            <Paragraph><strong>我的答案：</strong>{detail.my_answer || '未填写'}</Paragraph>
            <Paragraph><strong>正确答案：</strong>{detail.correct_answer || '未填写'}</Paragraph>
            <Paragraph><strong>错误原因：</strong><Tag>{detail.error_type}</Tag></Paragraph>
            <Paragraph><strong>解题分析：</strong>{detail.analysis || '未填写'}</Paragraph>
            <Paragraph><strong>复习次数：</strong>{detail.review_count} 次</Paragraph>
          </div>
        )}
      </Modal>
    </div>
  )
}
