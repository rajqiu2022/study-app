import axios from 'axios'

// 部署时使用相对路径（nginx代理），本地开发用 localhost:8000
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
})

// 动态获取当前登录用户ID
export const getCurrentUserId = () => {
  const user = localStorage.getItem('study_user')
  if (user) {
    try { return JSON.parse(user).id } catch { return null }
  }
  return null
}

export const getCurrentUser = () => {
  const user = localStorage.getItem('study_user')
  if (user) {
    try { return JSON.parse(user) } catch { return null }
  }
  return null
}

export const setCurrentUser = (user) => {
  localStorage.setItem('study_user', JSON.stringify(user))
}

export const clearCurrentUser = () => {
  localStorage.removeItem('study_user')
}

const uid = () => getCurrentUserId()

// ---- 用户认证 ----
export const register = (data) => api.post('/users/register', data)
export const login = (data) => api.post('/users/login', data)
export const updateUser = (userId, data) => api.put(`/users/${userId}`, data)
export const getUser = (userId) => api.get(`/users/${userId}`)

// ---- 仪表盘 ----
export const getDashboard = () => api.get('/dashboard/', { params: { user_id: uid() } })

// ---- 学科 ----
export const getSubjects = () => api.get('/subjects/')

// ---- 学习记录 ----
export const getRecords = (subjectId) =>
  api.get('/records/', { params: { user_id: uid(), subject_id: subjectId || undefined } })
export const createRecord = (data) => api.post('/records/', { ...data, user_id: uid() })
export const updateRecord = (id, data) => api.put(`/records/${id}`, data)
export const deleteRecord = (id) => api.delete(`/records/${id}`)

// ---- 错题本 ----
export const getWrongQuestions = (params = {}) =>
  api.get('/wrong-questions/', { params: { user_id: uid(), ...params } })
export const createWrongQuestion = (data) => api.post('/wrong-questions/', { ...data, user_id: uid() })
export const updateWrongQuestion = (id, data) => api.put(`/wrong-questions/${id}`, data)
export const reviewWrongQuestion = (id) => api.post(`/wrong-questions/${id}/review`)
export const deleteWrongQuestion = (id) => api.delete(`/wrong-questions/${id}`)

// ---- 智能练习 ----
export const generatePractice = (data) => api.post('/practice/generate', { ...data, user_id: uid() }, { timeout: 120000 })
export const submitPractice = (sessionId, answers) => api.post(`/practice/${sessionId}/submit`, { answers })
export const abandonPractice = (sessionId) => api.post(`/practice/${sessionId}/abandon`)
export const getPracticeSession = (sessionId) => api.get(`/practice/${sessionId}`)
export const getPracticeSessions = () => api.get('/practice/', { params: { user_id: uid() } })

// ---- AI对话 ----
export const sendChat = (message, webSearch = false) => api.post('/chat/', { user_id: uid(), message, web_search: webSearch }, { timeout: 60000 })

// ---- 系统设置 ----
export const getLLMConfig = () => api.get('/settings/llm', { params: { user_id: uid() } })
export const saveLLMConfig = (data) => api.post('/settings/llm', data, { params: { user_id: uid() } })
export const testLLMConnection = (data) => api.post('/settings/llm/test', data, { timeout: 30000 })

// ---- 图片识别 ----
export const uploadImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('user_id', uid() || '')
  return api.post('/ocr/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 60000 })
}

export const recognizeAndSave = ({ action, subject_id, content, image_filename, ocr_text }) => {
  const formData = new FormData()
  formData.append('user_id', uid())
  formData.append('action', action)
  formData.append('subject_id', subject_id || 'math')
  formData.append('content', content || '')
  formData.append('image_filename', image_filename || '')
  formData.append('ocr_text', ocr_text || '')
  return api.post('/ocr/recognize-and-save', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 120000 })
}

export const getImageUrl = (filename) => {
  const base = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'
    : '/api'
  return `${base}/ocr/image/${filename}`
}

// ---- 知识图谱 ----
export const getKnowledgeGraph = (subjectId) =>
  api.get('/knowledge-graph/', { params: { user_id: uid(), subject_id: subjectId || undefined }, timeout: 120000 })

export default api
