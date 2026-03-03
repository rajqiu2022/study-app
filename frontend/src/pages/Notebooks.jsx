import React, { useState, useEffect, useRef } from 'react'
import {
  Card, Button, Typography, Input, Select, Tag, Empty, Spin, Modal,
  Upload, message, Image, Tooltip, Popconfirm, Badge,
} from 'antd'
import {
  PlusOutlined, SearchOutlined, StarOutlined, StarFilled,
  DeleteOutlined, PictureOutlined, AudioOutlined, AudioMutedOutlined,
  FileTextOutlined, TagOutlined, BookOutlined, EyeOutlined,
  CameraOutlined,
} from '@ant-design/icons'
import {
  getNotebooks, createNotebook, updateNotebook, deleteNotebook,
  uploadNoteImage, getSubjects, getImageUrl, getCurrentUser, getCurrentUserId,
} from '../api'

const { Title, Text, Paragraph } = Typography

const CATEGORY_COLORS = {
  '课堂笔记': 'blue',
  '复习总结': 'green',
  '错题整理': 'red',
  '公式定理': 'purple',
  '读书笔记': 'orange',
  '实验记录': 'cyan',
  '词汇积累': 'magenta',
  '作文素材': 'gold',
  '其他': 'default',
}

const SUBJECT_ICONS = {
  math: '🔢', chinese: '📖', english: '🔤', science: '🔬',
}

export default function Notebooks() {
  const [notebooks, setNotebooks] = useState([])
  const [loading, setLoading] = useState(false)
  const [subjects, setSubjects] = useState([])
  const [filterSubject, setFilterSubject] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterStarred, setFilterStarred] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectedNote, setSelectedNote] = useState(null)
  const [creating, setCreating] = useState(false)

  // 创建笔记状态
  const [noteContent, setNoteContent] = useState('')
  const [noteImages, setNoteImages] = useState([]) // [{file, preview, filename}]
  const [audioText, setAudioText] = useState('')
  const [recording, setRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)
  const cameraInputRef = useRef(null)

  useEffect(() => {
    getSubjects().then((res) => setSubjects(res.data)).catch(() => {})
    loadNotebooks()
  }, [])

  const loadNotebooks = async (params = {}) => {
    setLoading(true)
    try {
      const res = await getNotebooks(params)
      setNotebooks(res.data)
    } catch {
      message.error('加载笔记失败')
    }
    setLoading(false)
  }

  useEffect(() => {
    const params = {}
    if (filterSubject) params.subject_id = filterSubject
    if (filterCategory) params.category = filterCategory
    if (filterStarred) params.is_starred = true
    if (keyword) params.keyword = keyword
    loadNotebooks(params)
  }, [filterSubject, filterCategory, filterStarred, keyword])

  // 录音功能
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
      }

      mediaRecorder.start()
      setRecording(true)
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime((t) => t + 1)
      }, 1000)
    } catch {
      message.error('无法访问麦克风，请检查权限设置')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    setRecording(false)
    clearInterval(timerRef.current)

    // 语音转文字提示
    message.info('语音已录制，请在下方文字框中手动输入语音内容（或等待AI识别）')
  }

  // 图片上传
  const handleImageUpload = async (file) => {
    try {
      const preview = URL.createObjectURL(file)
      const res = await uploadNoteImage(file)
      setNoteImages((prev) => [...prev, {
        file,
        preview,
        filename: res.data.filename,
        url: res.data.url,
      }])
    } catch {
      message.error('图片上传失败')
    }
    return false
  }

  const removeImage = (index) => {
    setNoteImages((prev) => prev.filter((_, i) => i !== index))
  }

  // 创建笔记
  const handleCreate = async () => {
    if (!noteContent && !audioText && noteImages.length === 0) {
      message.warning('请输入笔记内容（文字、图片或语音）')
      return
    }

    setCreating(true)
    try {
      const formData = new FormData()
      formData.append('user_id', getCurrentUserId())
      formData.append('content', noteContent)
      formData.append('audio_text', audioText)
      formData.append('image_filenames', JSON.stringify(noteImages.map((i) => i.filename)))

      const res = await createNotebook(formData)
      message.success('笔记创建成功，AI已自动归类！')
      setCreateOpen(false)
      resetCreateForm()
      loadNotebooks()
    } catch {
      message.error('创建笔记失败')
    }
    setCreating(false)
  }

  const resetCreateForm = () => {
    setNoteContent('')
    setNoteImages([])
    setAudioText('')
    setRecordingTime(0)
  }

  // 收藏/取消收藏
  const toggleStar = async (nb, e) => {
    e?.stopPropagation()
    try {
      await updateNotebook(nb.id, { is_starred: !nb.is_starred })
      setNotebooks((prev) => prev.map((n) =>
        n.id === nb.id ? { ...n, is_starred: !n.is_starred } : n
      ))
    } catch {
      message.error('操作失败')
    }
  }

  // 删除笔记
  const handleDelete = async (id, e) => {
    e?.stopPropagation()
    try {
      await deleteNotebook(id)
      setNotebooks((prev) => prev.filter((n) => n.id !== id))
      message.success('已删除')
    } catch {
      message.error('删除失败')
    }
  }

  const viewDetail = (nb) => {
    setSelectedNote(nb)
    setDetailOpen(true)
  }

  const parseJSON = (str, fallback = []) => {
    try { return JSON.parse(str) } catch { return fallback }
  }

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  const user = getCurrentUser()

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <Title level={3} style={{ margin: 0 }}>📓 笔记本</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setCreateOpen(true)}
          size="large"
          style={{ borderRadius: 12 }}
        >
          记笔记
        </Button>
      </div>

      {/* 筛选区 */}
      <Card style={{ borderRadius: 16, marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <Input
            prefix={<SearchOutlined />}
            placeholder="搜索笔记..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            style={{ width: 200, borderRadius: 8 }}
            allowClear
          />
          <Select
            value={filterSubject}
            onChange={setFilterSubject}
            style={{ width: 130 }}
            placeholder="全部学科"
            allowClear
          >
            <Select.Option value="">全部学科</Select.Option>
            {subjects.map((s) => (
              <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>
            ))}
          </Select>
          <Select
            value={filterCategory}
            onChange={setFilterCategory}
            style={{ width: 130 }}
            placeholder="全部类型"
            allowClear
          >
            <Select.Option value="">全部类型</Select.Option>
            {Object.keys(CATEGORY_COLORS).map((c) => (
              <Select.Option key={c} value={c}>{c}</Select.Option>
            ))}
          </Select>
          <Button
            icon={filterStarred ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
            onClick={() => setFilterStarred(!filterStarred)}
            type={filterStarred ? 'primary' : 'default'}
            ghost={filterStarred}
          >
            收藏
          </Button>
          <Text type="secondary" style={{ marginLeft: 'auto' }}>共 {notebooks.length} 条笔记</Text>
        </div>
      </Card>

      {/* 笔记列表 */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}><Spin size="large" /></div>
      ) : notebooks.length === 0 ? (
        <Card style={{ borderRadius: 16 }}>
          <Empty description="还没有笔记，点击「记笔记」开始吧！" />
        </Card>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16 }}>
          {notebooks.map((nb) => {
            const images = parseJSON(nb.image_urls)
            const knowledgePoints = parseJSON(nb.ai_knowledge_points)
            const tags = parseJSON(nb.tags)
            const subjectName = nb.subject_id ? (subjects.find((s) => s.id === nb.subject_id)?.name || '') : ''
            const subjectIcon = SUBJECT_ICONS[nb.subject_id] || '📝'

            return (
              <Card
                key={nb.id}
                hoverable
                onClick={() => viewDetail(nb)}
                style={{ borderRadius: 16, overflow: 'hidden' }}
                styles={{ body: { padding: '16px 20px' } }}
              >
                {/* 头部 */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <Text strong style={{ fontSize: 16 }}>{subjectIcon} {nb.title}</Text>
                  </div>
                  <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
                    <Button
                      type="text" size="small"
                      icon={nb.is_starred ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
                      onClick={(e) => toggleStar(nb, e)}
                    />
                    <Popconfirm title="确定删除？" onConfirm={(e) => handleDelete(nb.id, e)} onCancel={(e) => e?.stopPropagation()}>
                      <Button type="text" size="small" danger icon={<DeleteOutlined />} onClick={(e) => e.stopPropagation()} />
                    </Popconfirm>
                  </div>
                </div>

                {/* AI摘要 */}
                {nb.ai_summary && (
                  <Paragraph ellipsis={{ rows: 2 }} style={{ color: '#6b7280', fontSize: 13, marginBottom: 8 }}>
                    {nb.ai_summary}
                  </Paragraph>
                )}

                {/* 图片预览 */}
                {images.length > 0 && (
                  <div style={{ display: 'flex', gap: 6, marginBottom: 8, overflow: 'hidden' }}>
                    {images.slice(0, 3).map((url, i) => (
                      <div key={i} style={{ width: 60, height: 60, borderRadius: 8, overflow: 'hidden', flexShrink: 0, background: '#f5f5f5' }}>
                        <img
                          src={getImageUrl(url.split('/').pop())}
                          alt=""
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                    ))}
                    {images.length > 3 && (
                      <div style={{ width: 60, height: 60, borderRadius: 8, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999', fontSize: 12 }}>
                        +{images.length - 3}
                      </div>
                    )}
                  </div>
                )}

                {/* 语音标识 */}
                {nb.audio_text && (
                  <div style={{ marginBottom: 8, fontSize: 12, color: '#8b5cf6' }}>
                    🎙️ 含语音内容
                  </div>
                )}

                {/* 标签区 */}
                <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 8 }}>
                  {subjectName && <Tag color="blue">{subjectName}</Tag>}
                  {nb.ai_category && <Tag color={CATEGORY_COLORS[nb.ai_category] || 'default'}>{nb.ai_category}</Tag>}
                  {knowledgePoints.slice(0, 2).map((kp, i) => (
                    <Tag key={i} style={{ fontSize: 11 }}>{kp}</Tag>
                  ))}
                </div>

                {/* 底部时间 */}
                <div style={{ fontSize: 11, color: '#999' }}>
                  {nb.created_at ? new Date(nb.created_at).toLocaleString('zh-CN') : ''}
                </div>
              </Card>
            )
          })}
        </div>
      )}

      {/* 创建笔记弹窗 */}
      <Modal
        title="📝 记笔记"
        open={createOpen}
        onCancel={() => { setCreateOpen(false); resetCreateForm() }}
        width={560}
        footer={[
          <Button key="cancel" onClick={() => { setCreateOpen(false); resetCreateForm() }}>取消</Button>,
          <Button key="create" type="primary" loading={creating} onClick={handleCreate}>
            {creating ? 'AI分析中...' : '保存笔记'}
          </Button>,
        ]}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 16 }}>
          {/* 文字输入 */}
          <div>
            <Text style={{ fontSize: 13, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6 }}>
              <FileTextOutlined /> 文字内容
            </Text>
            <Input.TextArea
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              placeholder="输入笔记内容，支持课堂笔记、知识点记录、学习心得等..."
              rows={4}
              style={{ borderRadius: 8 }}
              maxLength={5000}
              showCount
            />
          </div>

          {/* 图片上传 */}
          <div>
            <Text style={{ fontSize: 13, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6 }}>
              <PictureOutlined /> 图片（可拍照或选择）
            </Text>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {noteImages.map((img, i) => (
                <div key={i} style={{ position: 'relative', width: 80, height: 80 }}>
                  <img
                    src={img.preview}
                    alt=""
                    style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 8, border: '1px solid #e5e7eb' }}
                  />
                  <Button
                    type="primary" danger size="small" shape="circle"
                    icon={<DeleteOutlined style={{ fontSize: 10 }} />}
                    style={{ position: 'absolute', top: -6, right: -6, width: 20, height: 20, minWidth: 20 }}
                    onClick={() => removeImage(i)}
                  />
                </div>
              ))}
              {/* 拍照按钮 */}
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                style={{ display: 'none' }}
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleImageUpload(file)
                  e.target.value = ''
                }}
              />
              <div
                onClick={() => cameraInputRef.current?.click()}
                style={{
                  width: 80, height: 80, borderRadius: 8, border: '2px dashed #d9d9d9',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  cursor: 'pointer', color: '#999', fontSize: 11, gap: 2,
                }}
              >
                <CameraOutlined style={{ fontSize: 20 }} />
                拍照
              </div>
              {/* 相册选择 */}
              <Upload
                accept="image/*"
                showUploadList={false}
                beforeUpload={handleImageUpload}
              >
                <div style={{
                  width: 80, height: 80, borderRadius: 8, border: '2px dashed #d9d9d9',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  cursor: 'pointer', color: '#999', fontSize: 11, gap: 2,
                }}>
                  <PictureOutlined style={{ fontSize: 20 }} />
                  相册
                </div>
              </Upload>
            </div>
          </div>

          {/* 语音输入 */}
          <div>
            <Text style={{ fontSize: 13, color: '#6b7280', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 6 }}>
              <AudioOutlined /> 语音内容
            </Text>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
              {recording ? (
                <Button
                  danger type="primary" shape="round"
                  icon={<AudioMutedOutlined />}
                  onClick={stopRecording}
                >
                  停止录音 {formatTime(recordingTime)}
                </Button>
              ) : (
                <Button
                  shape="round"
                  icon={<AudioOutlined />}
                  onClick={startRecording}
                  style={{ borderColor: '#8b5cf6', color: '#8b5cf6' }}
                >
                  开始录音
                </Button>
              )}
              {recording && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div style={{
                    width: 8, height: 8, borderRadius: '50%', background: '#ef4444',
                    animation: 'pulse 1s infinite',
                  }} />
                  <Text type="secondary" style={{ fontSize: 12 }}>录音中...</Text>
                </div>
              )}
            </div>
            <Input.TextArea
              value={audioText}
              onChange={(e) => setAudioText(e.target.value)}
              placeholder="录音后请在这里输入语音内容，或直接手动输入..."
              rows={2}
              style={{ borderRadius: 8 }}
            />
          </div>

          {/* 提示 */}
          <div style={{
            padding: '10px 14px', background: 'linear-gradient(135deg, #f0f5ff, #f5f0ff)',
            borderRadius: 10, fontSize: 12, color: '#6366f1',
          }}>
            💡 保存后 AI 将自动识别笔记内容，为你归类学科、提取知识点、生成摘要和标签
          </div>
        </div>
      </Modal>

      {/* 笔记详情弹窗 */}
      <Modal
        title={selectedNote ? `${SUBJECT_ICONS[selectedNote.subject_id] || '📝'} ${selectedNote.title}` : '笔记详情'}
        open={detailOpen}
        onCancel={() => { setDetailOpen(false); setSelectedNote(null) }}
        footer={null}
        width={600}
      >
        {selectedNote && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 12 }}>
            {/* AI分析卡片 */}
            {selectedNote.ai_summary && (
              <div style={{
                padding: 14, background: 'linear-gradient(135deg, #f0f5ff, #f5f0ff)',
                borderRadius: 12, border: '1px solid #e0e7ff',
              }}>
                <Text strong style={{ fontSize: 13, color: '#6366f1' }}>🤖 AI 智能分析</Text>
                <div style={{ marginTop: 8, fontSize: 13, color: '#374151' }}>{selectedNote.ai_summary}</div>
                {(() => {
                  const kps = parseJSON(selectedNote.ai_knowledge_points)
                  return kps.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      <Text style={{ fontSize: 12, color: '#6b7280' }}>知识点：</Text>
                      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
                        {kps.map((kp, i) => <Tag key={i} color="purple">{kp}</Tag>)}
                      </div>
                    </div>
                  )
                })()}
              </div>
            )}

            {/* 标签 */}
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {selectedNote.subject_id && (
                <Tag color="blue" icon={<BookOutlined />}>
                  {subjects.find((s) => s.id === selectedNote.subject_id)?.name || selectedNote.subject_id}
                </Tag>
              )}
              {selectedNote.ai_category && (
                <Tag color={CATEGORY_COLORS[selectedNote.ai_category] || 'default'}>
                  {selectedNote.ai_category}
                </Tag>
              )}
              {selectedNote.grade && <Tag>{selectedNote.grade}</Tag>}
              {parseJSON(selectedNote.tags).map((t, i) => (
                <Tag key={i} icon={<TagOutlined />}>{t}</Tag>
              ))}
            </div>

            {/* 文字内容 */}
            {selectedNote.content && (
              <div>
                <Text strong style={{ fontSize: 13 }}>📝 笔记内容</Text>
                <div style={{
                  marginTop: 6, padding: 12, background: '#f9fafb', borderRadius: 8,
                  whiteSpace: 'pre-wrap', lineHeight: 1.8, fontSize: 14,
                }}>
                  {selectedNote.content}
                </div>
              </div>
            )}

            {/* 语音转写内容 */}
            {selectedNote.audio_text && (
              <div>
                <Text strong style={{ fontSize: 13 }}>🎙️ 语音内容</Text>
                <div style={{
                  marginTop: 6, padding: 12, background: '#faf5ff', borderRadius: 8,
                  whiteSpace: 'pre-wrap', lineHeight: 1.8, fontSize: 14,
                  borderLeft: '3px solid #8b5cf6',
                }}>
                  {selectedNote.audio_text}
                </div>
              </div>
            )}

            {/* 图片 */}
            {(() => {
              const images = parseJSON(selectedNote.image_urls)
              return images.length > 0 && (
                <div>
                  <Text strong style={{ fontSize: 13 }}>📸 图片</Text>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 6 }}>
                    <Image.PreviewGroup>
                      {images.map((url, i) => (
                        <Image
                          key={i}
                          src={getImageUrl(url.split('/').pop())}
                          width={120}
                          height={120}
                          style={{ objectFit: 'cover', borderRadius: 8 }}
                        />
                      ))}
                    </Image.PreviewGroup>
                  </div>
                </div>
              )
            })()}

            {/* 创建时间 */}
            <div style={{ fontSize: 12, color: '#999', textAlign: 'right' }}>
              创建于 {selectedNote.created_at ? new Date(selectedNote.created_at).toLocaleString('zh-CN') : ''}
            </div>
          </div>
        )}
      </Modal>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  )
}
