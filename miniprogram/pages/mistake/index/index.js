// miniprogram/pages/mistake/index/index.js
const storage = require('../../../utils/mistakeStorage.js')

Page({
  data: {
    records: [],
    filterType: 'all', // all | operation | rule | miss_trigger
    filteredRecords: []
  },

  onLoad() {
    this.loadRecords()
  },

  onShow() {
    this.loadRecords()
  },

  loadRecords() {
    const records = storage.getRecords()
    this.setData({ records }, () => {
      this.applyFilter()
    })
  },

  onFilterTap(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ filterType: type }, () => {
      this.applyFilter()
    })
  },

  applyFilter() {
    const { records, filterType } = this.data
    if (filterType === 'all') {
      this.setData({ filteredRecords: records })
    } else {
      this.setData({ filteredRecords: records.filter(r => r.type === filterType) })
    }
  },

  onRecordTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/mistake/detail/detail?id=${id}` })
  },

  onAddTap() {
    wx.navigateTo({ url: '/pages/mistake/add/add' })
  },

  onDeleteTap(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复',
      success: (res) => {
        if (res.confirm) {
          storage.deleteRecord(id)
          this.loadRecords()
        }
      }
    })
  },

  formatTime(ts) {
    if (!ts) return ''
    const d = new Date(ts)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
  }
})
