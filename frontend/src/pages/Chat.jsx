import React, { useState, useRef, useEffect } from 'react'
import { Card, Input, Button, Typography, Spin, Upload, Modal, Select, message, Image, Switch, Tooltip } from 'antd'
import {
  SendOutlined, RobotOutlined, UserOutlined, CameraOutlined,
  PictureOutlined, CloseOutlined, GlobalOutlined, ReadOutlined, AudioOutlined,
} from '@ant-design/icons'
import { sendChat, uploadImage, recognizeAndSave, getImageUrl, getSubjects, createNotebook, getCurrentUserId, speechToText } from '../api'

const { Title, Text } = Typography

const ACTION_OPTIONS = [
  { label: '📝 记录错题', value: 'wrong_question' },
  { label: '📚 记录重点知识', value: 'learning_record' },
  { label: '📓 保存为笔记', value: 'notebook' },
]

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: '你好！我是你的学习小助手 🤖\n\n你可以：\n📚 输入「我今天学了XXX」- 记录学习\n❌ 输入「XX题做错了」- 添加错题\n📓 输入「记笔记」- 创建学习笔记\n🎯 输入「帮我出5道XX题」- 生成练习\n📸 发送图片 - 识别题目并记录\n🎤 点击麦克风 - 语音输入（普通话）\n📊 输入「分析薄弱点」- 查看分析',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [subjects, setSubjects] = useState([])

  // 图片上传相关状态
  const [pendingImage, setPendingImage] = useState(null) // {file, preview, filename, ocrText}
  const [imageAction, setImageAction] = useState('wrong_question')
  const [imageSubject, setImageSubject] = useState('math')
  const [imageNote, setImageNote] = useState('')
  const [imageModalOpen, setImageModalOpen] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [webSearch, setWebSearch] = useState(false)
  const [subjectAutoDetected, setSubjectAutoDetected] = useState(false)

  // 语音录音相关状态（使用 MediaRecorder，和笔记本一样）
  const [isListening, setIsListening] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [transcribing, setTranscribing] = useState(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)

  const bottomRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    getSubjects().then((res) => setSubjects(res.data)).catch(() => {})
  }, [])

  // 组件卸载时停止录音
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
      clearInterval(timerRef.current)
    }
  }, [])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setInput('')
    setLoading(true)

    try {
      const res = await sendChat(text, webSearch)
      setMessages((prev) => [...prev, { role: 'bot', content: res.data.reply, action: res.data.action }])
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', content: '抱歉，我遇到了问题。请检查后端服务是否正常运行。' }])
    }
    setLoading(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 语音录音 + 后端转文字
  const toggleListening = async () => {
    if (transcribing) return

    if (isListening) {
      // 停止录音
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
      return
    }

    // 开始录音
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        setIsListening(false)
        clearInterval(timerRef.current)

        // 将录音发送到后端转文字
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        if (audioBlob.size < 1000) {
          message.warning('录音时间太短，请重试')
          return
        }

        setTranscribing(true)
        try {
          const res = await speechToText(audioBlob)
          const text = res.data.text?.trim()
          if (text) {
            setInput((prev) => (prev ? prev + ' ' + text : text))
            message.success('语音识别完成')
          } else {
            message.warning('未识别到有效内容，请重试')
          }
        } catch (err) {
          const errMsg = err?.response?.data?.detail || '语音识别失败'
          message.error(errMsg)
        }
        setTranscribing(false)
      }

      mediaRecorder.start()
      setIsListening(true)
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime((t) => t + 1)
      }, 1000)
      message.info('🎤 开始录音，请说话...')
    } catch (err) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        message.error('麦克风权限被拒绝，请在浏览器设置中允许')
      } else if (err.name === 'NotFoundError') {
        message.error('未检测到麦克风设备')
      } else {
        message.error('无法访问麦克风：' + err.message)
      }
    }
  }

  // 处理图片选择（拍照或相册）
  const handleImageSelect = async (file) => {
    const preview = URL.createObjectURL(file)
    setPendingImage({ file, preview, filename: '', ocrText: '' })
    setImageNote('')
    setSubjectAutoDetected(false)
    setUploading(true)
    setImageModalOpen(true) // 立即打开弹窗，显示图片预览和"识别中"

    // 异步上传获取 OCR 结果
    try {
      const res = await uploadImage(file)
      setPendingImage((prev) => ({
        ...prev,
        filename: res.data.filename,
        ocrText: res.data.ocr_text || '',
        aiUsed: res.data.ai_used || false,
      }))
      // 自动识别学科
      if (res.data.detected_subject_id) {
        setImageSubject(res.data.detected_subject_id)
        setSubjectAutoDetected(true)
      }
    } catch (err) {
      console.error('上传图片失败:', err)
      message.error('图片上传失败，请重试')
      setPendingImage((prev) => ({ ...prev, filename: '', ocrText: '' }))
    }
    setUploading(false)
    return false // 阻止 antd 默认上传
  }

  // 确认保存图片识别结果
  const handleImageSave = async () => {
    if (!pendingImage) return
    setLoading(true)

    // 先在聊天中显示图片消息
    setMessages((prev) => [...prev, {
      role: 'user',
      content: imageNote || '（发送了一张图片）',
      image: pendingImage.preview,
    }])

    try {
      // 如果选择保存为笔记
      if (imageAction === 'notebook') {
        const formData = new FormData()
        formData.append('user_id', getCurrentUserId())
        formData.append('content', imageNote || '')
        formData.append('audio_text', '')
        formData.append('image_filenames', JSON.stringify([pendingImage.filename]))
        await createNotebook(formData)
        setMessages((prev) => [...prev, {
          role: 'bot',
          content: '📓 已保存为笔记！AI正在自动分析归类，你可以到「笔记本」页面查看。',
          action: 'created_notebook',
        }])
      } else {
        const res = await recognizeAndSave({
          action: imageAction,
          subject_id: imageSubject,
          content: imageNote,
          image_filename: pendingImage.filename,
          ocr_text: pendingImage.ocrText,
        })

        let reply = res.data.message
        if (res.data.ocr_text && !res.data.ai_analysis) {
          reply += `\n\n📋 识别到的内容：\n${res.data.ocr_text.substring(0, 200)}`
        }
        if (!res.data.ai_analysis) {
          reply += imageAction === 'wrong_question'
            ? '\n\n已添加到错题本，记得定期复习哦！📝'
            : '\n\n已记录为重点知识，加油学习！💪'
        }

        setMessages((prev) => [...prev, {
          role: 'bot',
          content: reply,
          action: res.data.action === 'wrong_question' ? 'created_wrong_question' : 'created_learning_record',
        }])
      }
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', content: '保存失败，请重试。' }])
    }

    setImageModalOpen(false)
    setPendingImage(null)
    setLoading(false)
  }

  const actionText = (action) => {
    const map = {
      created_learning_record: '已添加学习记录',
      created_wrong_question: '已添加错题',
      created_notebook: '已保存笔记',
      redirect_practice: '请前往智能练习页面',
      redirect_notebook: '请前往笔记本页面',
      analysis: '学习分析',
    }
    return map[action] || action
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 96px)' }}>
      <Title level={3} style={{ marginBottom: 16 }} className="chat-title">🤖 AI学习小助手</Title>

      <Card
        style={{ flex: 1, borderRadius: 16, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
        styles={{ body: { flex: 1, overflow: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 } }}
      >
        {messages.map((msg, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', alignItems: 'flex-start', gap: 8 }}>
            {msg.role === 'bot' && (
              <div className="chat-avatar chat-avatar-bot">
                <RobotOutlined style={{ color: 'white', fontSize: 18 }} />
              </div>
            )}
            <div className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot'}>
              {msg.image && (
                <div style={{ marginBottom: 8 }}>
                  <Image src={msg.image} style={{ maxWidth: 200, maxHeight: 200, borderRadius: 8 }} />
                </div>
              )}
              {msg.content}
              {msg.action && (
                <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
                  ✅ {actionText(msg.action)}
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="chat-avatar chat-avatar-user">
                <UserOutlined style={{ color: '#6366f1', fontSize: 18 }} />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <div className="chat-avatar chat-avatar-bot">
              <RobotOutlined style={{ color: 'white', fontSize: 18 }} />
            </div>
            <Spin size="small" />
          </div>
        )}
        <div ref={bottomRef} />
      </Card>

      {/* 输入区域 */}
      <div className="chat-input-bar">
        {/* 联网搜索开关 */}
        <Tooltip title={webSearch ? '联网搜索已开启' : '联网搜索已关闭'}>
          <Button
            icon={<GlobalOutlined />}
            shape="circle"
            size="large"
            type={webSearch ? 'primary' : 'default'}
            onClick={() => setWebSearch(!webSearch)}
            style={{
              flexShrink: 0,
              ...(webSearch ? {} : { color: '#bfbfbf', borderColor: '#d9d9d9' }),
            }}
            title="联网搜索"
          />
        </Tooltip>

        {/* 拍照按钮 */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          style={{ display: 'none' }}
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleImageSelect(file)
            e.target.value = ''
          }}
        />
        <Button
          icon={<CameraOutlined />}
          shape="circle"
          size="large"
          onClick={() => fileInputRef.current?.click()}
          style={{ flexShrink: 0 }}
          title="拍照识别"
        />

        {/* 相册选择按钮 */}
        <Upload
          accept="image/*"
          showUploadList={false}
          beforeUpload={handleImageSelect}
        >
          <Button
            icon={<PictureOutlined />}
            shape="circle"
            size="large"
            style={{ flexShrink: 0 }}
            title="从相册选择"
          />
        </Upload>

        {/* 语音输入按钮 */}
        <Tooltip title={isListening ? `录音中 ${recordingTime}s，点击停止` : (transcribing ? '正在识别...' : '语音输入（普通话）')}>
          <Button
            icon={<AudioOutlined />}
            shape="circle"
            size="large"
            type={isListening ? 'primary' : 'default'}
            danger={isListening}
            onClick={toggleListening}
            loading={transcribing}
            style={{
              flexShrink: 0,
              ...(isListening ? { animation: 'pulse 1.5s infinite' } : {}),
            }}
          />
        </Tooltip>

        <Input.TextArea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isListening ? `🎤 录音中 ${recordingTime}s...点击麦克风停止` : (transcribing ? '⏳ 语音识别中，请稍候...' : '输入文字、语音或拍照发送...')}
          autoSize={{ minRows: 1, maxRows: 3 }}
          style={{ borderRadius: 12, fontSize: 15 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
          size="large"
          shape="circle"
          style={{ flexShrink: 0 }}
        />
      </div>

      {/* 图片确认弹窗 */}
      <Modal
        title="📸 图片识别"
        open={imageModalOpen}
        onOk={handleImageSave}
        onCancel={() => { setImageModalOpen(false); setPendingImage(null) }}
        okText="确认保存"
        cancelText="取消"
        width={480}
        confirmLoading={loading}
        okButtonProps={{ disabled: uploading || !pendingImage?.filename }}
      >
        {pendingImage && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* 图片预览 */}
            <div style={{ textAlign: 'center', background: '#f5f5f5', borderRadius: 12, padding: 12 }}>
              <img
                src={pendingImage.preview}
                alt="preview"
                style={{ maxWidth: '100%', maxHeight: 250, borderRadius: 8, objectFit: 'contain' }}
              />
            </div>

            {/* OCR 结果 */}
            {uploading ? (
              <div style={{ textAlign: 'center' }}><Spin /> 正在识别中...</div>
            ) : pendingImage.ocrText ? (
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {pendingImage.aiUsed ? '🤖 AI 识别结果：' : '📋 识别结果：'}
                </Text>
                <div style={{
                  background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 8,
                  padding: 12, marginTop: 4, maxHeight: 120, overflow: 'auto',
                  fontSize: 13, lineHeight: 1.6, whiteSpace: 'pre-wrap',
                }}>
                  {pendingImage.ocrText}
                </div>
              </div>
            ) : (
              <Text type="secondary" style={{ fontSize: 12 }}>
                ⚠️ 未能自动识别文字（请先在「大模型设置」中配置并启用AI），你可以手动补充说明
              </Text>
            )}

            {/* 操作选择 */}
            <div style={{ display: 'flex', gap: 12 }}>
              <div style={{ flex: 1 }}>
                <Text style={{ fontSize: 12, color: '#6b7280' }}>保存为：</Text>
                <Select
                  value={imageAction}
                  onChange={setImageAction}
                  options={ACTION_OPTIONS}
                  style={{ width: '100%', marginTop: 4 }}
                />
              </div>
              {imageAction !== 'notebook' && (
                <div style={{ flex: 1 }}>
                  <Text style={{ fontSize: 12, color: '#6b7280' }}>
                    学科：{subjectAutoDetected && <span style={{ color: '#52c41a', marginLeft: 4 }}>🤖 AI已识别</span>}
                  </Text>
                  <Select
                    value={imageSubject}
                    onChange={(v) => { setImageSubject(v); setSubjectAutoDetected(false) }}
                    style={{ width: '100%', marginTop: 4 }}
                  >
                    {subjects.map((s) => (
                      <Select.Option key={s.id} value={s.id}>{s.icon} {s.name}</Select.Option>
                    ))}
                  </Select>
                </div>
              )}
              {imageAction === 'notebook' && (
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', padding: '8px 0' }}>
                  <Text style={{ fontSize: 12, color: '#8b5cf6' }}>📓 AI 将自动识别学科和知识点</Text>
                </div>
              )}
            </div>

            {/* 补充说明 */}
            <div>
              <Text style={{ fontSize: 12, color: '#6b7280' }}>补充说明（可选）：</Text>
              <Input.TextArea
                value={imageNote}
                onChange={(e) => setImageNote(e.target.value)}
                placeholder="比如：这道分数加法做错了，正确答案是3/4"
                rows={2}
                style={{ marginTop: 4 }}
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
