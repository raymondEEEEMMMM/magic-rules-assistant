// miniprogram/pages/mistake/detail/detail.js
const storage = require('../../../utils/mistakeStorage.js')

Page({
  data: {
    record: null
  },

  onLoad(options) {
    const id = options.id
    const record = storage.getRecordById(id)
    if (record) {
      this.setData({ record })
    } else {
      wx.showToast({ title: '记录不存在', icon: 'none' })
      setTimeout(() => wx.navigateBack(), 1500)
    }
  },

  onReview() {
    const { record } = this.data
    const updated = storage.updateRecord(record.id, {
      reviewed_at: Date.now(),
      review_count: (record.review_count || 0) + 1
    })
    this.setData({ record: updated })
    wx.showToast({ title: '已标记复习', icon: 'success' })
  },

  onDelete() {
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复',
      success: (res) => {
        if (res.confirm) {
          storage.deleteRecord(this.data.record.id)
          wx.navigateBack()
        }
      }
    })
  },

  formatTime(ts) {
    if (!ts) return ''
    const d = new Date(ts)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  }
})
