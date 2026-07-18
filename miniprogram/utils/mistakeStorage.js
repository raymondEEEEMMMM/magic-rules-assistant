// miniprogram/utils/mistakeStorage.js
const STORAGE_KEY = 'mistake_records'

function generateId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

function getRecords() {
  try {
    const data = wx.getStorageSync(STORAGE_KEY)
    return data ? JSON.parse(data) : []
  } catch (e) {
    console.error('读取错题记录失败', e)
    return []
  }
}

function saveRecord(record) {
  const records = getRecords()
  const newRecord = {
    id: generateId(),
    type: record.type,
    cards: record.cards || [],
    title: record.title || '',
    content: record.content || '',
    created_at: Date.now(),
    reviewed_at: null,
    review_count: 0
  }
  records.unshift(newRecord)
  wx.setStorageSync(STORAGE_KEY, JSON.stringify(records))
  return newRecord
}

function updateRecord(id, updates) {
  const records = getRecords()
  const index = records.findIndex(r => r.id === id)
  if (index === -1) return null
  records[index] = { ...records[index], ...updates }
  wx.setStorageSync(STORAGE_KEY, JSON.stringify(records))
  return records[index]
}

function deleteRecord(id) {
  const records = getRecords()
  const filtered = records.filter(r => r.id !== id)
  wx.setStorageSync(STORAGE_KEY, JSON.stringify(filtered))
}

function getRecordById(id) {
  const records = getRecords()
  return records.find(r => r.id === id) || null
}

module.exports = {
  getRecords,
  getRecordById,
  saveRecord,
  updateRecord,
  deleteRecord
}
