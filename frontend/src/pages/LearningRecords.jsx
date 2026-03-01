import React, { useEffect, useState } from 'react'
import {
  Card, Table, Button, Modal, Form, Input, Select, DatePicker, InputNumber, Switch,
  Tag, Space, Popconfirm, message, Typography, Segmented, Image,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { getRecords, createRecord, updateRecord, deleteRecord, getSubjects } from '../api'

const { Title } = Typography
const { TextArea } = Input

const MASTERY_OPTIONS = [
  { value: 1, label: '⛔ 未掌握' },
  { value: 2, label: '⚠️ 需加强' },
  { value: 3, label: '😐 一般' },
  { value: 4, label: '👍 熟练' },
  { value: 5, label: '🌟 精通' },
]

const MASTERY_TAG = {
  1: { text: '未掌握', color: 'red' },
  2: { text: '需加强', color: 'orange' },
  3: { text: '一般', color: 'gold' },
  4: { text: '熟练', color: 'green' },
  5: { text: '精通', color: 'purple' },
}

export default function LearningRecords() {
  const [records, setRecords] = useState([])
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [filterSubject, setFilterSubject] = useState(null)
  const [form] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
      const [recRes, subRes] = await Promise.all([
        getRecords(filterSubject),
        getSubjects(),
      ])
      setRecords(recRes.data)
      setSubjects(subRes.data)
    } catch (e) {
      message.error('加载失败')
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [filterSubject])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const payload = {
        ...values,
        study_date: values.study_date?.format('YYYY-MM-DD'),
      }
      if (editingId) {
        await updateRecord(editingId, payload)
        message.success('更新成功')
      } else {
        await createRecord(payload)
        message.success('添加成功')
      }
      setModalOpen(false)
      setEditingId(null)
      form.resetFields()
      fetchData()
    } catch (e) { /* validation */ }
  }

  const handleEdit = (record) => {
    setEditingId(record.id)
    form.setFieldsValue({
      ...record,
      study_date: record.study_date ? dayjs(record.study_date) : null,
    })
    setModalOpen(true)
  }

  const handleDelete = async (id) => {
    await deleteRecord(id)
    message.success('已删除')
    fetchData()
  }

  const subjectName = (id) => subjects.find((s) => s.id === id)?.name || id

  const columns = [
    {
      title: '学科', dataIndex: 'subject_id', width: 80,
      render: (id) => subjectName(id),
    },
    { title: '知识点', dataIndex: 'knowledge_point', ellipsis: true,
      render: (text, r) => (
        <Space>
          {r.image_url && <Image src={r.image_url} width={32} height={32} style={{ borderRadius: 4, objectFit: 'cover' }} preview={{ mask: '🖼️' }} />}
          <span>{text}</span>
        </Space>
      ),
    },
    { title: '日期', dataIndex: 'study_date', width: 110 },
    { title: '时长(分)', dataIndex: 'duration_minutes', width: 80 },
    {
      title: '掌握程度', dataIndex: 'mastery_level', width: 100,
      render: (v) => <Tag color={MASTERY_TAG[v]?.color}>{MASTERY_TAG[v]?.text}</Tag>,
    },
    {
      title: '重点', dataIndex: 'is_important', width: 60,
      render: (v) => v ? <Tag color="red">★</Tag> : null,
    },
    {
      title: '操作', width: 120,
      render: (_, r) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(r)} />
          <Popconfirm title="确认删除？" onConfirm={() => handleDelete(r.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>📖 学习记录</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => {
          setEditingId(null)
          form.resetFields()
          form.setFieldsValue({ mastery_level: 3, study_date: dayjs(), duration_minutes: 30 })
          setModalOpen(true)
        }}>
          添加记录
        </Button>
      </div>

      <Card style={{ borderRadius: 16 }}>
        <div style={{ marginBottom: 16 }}>
          <Segmented
            options={[
              { label: '全部', value: '' },
              ...subjects.map((s) => ({ label: `${s.icon} ${s.name}`, value: s.id })),
            ]}
            value={filterSubject || ''}
            onChange={(v) => setFilterSubject(v || null)}
          />
        </div>
        <Table
          columns={columns}
          dataSource={records}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 15, showTotal: (t) => `共 ${t} 条` }}
          size="middle"
        />
      </Card>

      <Modal
        title={editingId ? '编辑记录' : '添加学习记录'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditingId(null) }}
        okText="保存"
        cancelText="取消"
        width={520}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="subject_id" label="学科" rules={[{ required: true, message: '请选择学科' }]}>
            <Select placeholder="选择学科">
              {subjects.map((s) => <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="knowledge_point" label="知识点" rules={[{ required: true, message: '请输入知识点' }]}>
            <Input placeholder="如：乘法口诀表、分数的加减法" />
          </Form.Item>
          <Form.Item name="study_date" label="学习日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="duration_minutes" label="学习时长(分钟)">
            <InputNumber min={0} max={300} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="mastery_level" label="掌握程度">
            <Select options={MASTERY_OPTIONS} />
          </Form.Item>
          <Form.Item name="is_important" label="标记为重点" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <TextArea rows={2} placeholder="学习心得或笔记..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
