// pages/feedback/feedback.js
const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    isLightTheme: true,
    feedbackTypes: [
      { key: 'suggestion', name: '功能建议' },
      { key: 'bug', name: '问题反馈' },
      { key: 'other', name: '其他' }
    ],
    selectedType: 'suggestion',
    content: '',
    submitting: false,
    openid: ''
  },

  onLoad() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    this.initOpenid()
  },

  // 初始化 openid
  initOpenid() {
    // 尝试从存储获取 openid
    const storedOpenid = wx.getStorageSync('userOpenid')
    if (storedOpenid) {
      this.setData({ openid: storedOpenid })
      return
    }

    // 如果没有存储的 openid，使用设备标识作为临时 openid
    const deviceId = wx.getStorageSync('deviceId')
    if (deviceId) {
      this.setData({ openid: deviceId })
      return
    }

    // 生成临时设备 ID
    const tempId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    wx.setStorageSync('deviceId', tempId)
    this.setData({ openid: tempId })
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 主题切换
  updateTheme(isLight) {
    this.setData({ isLightTheme: isLight })
  },

  // 返回
  goBack() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
  },

  // 选择反馈类型
  onSelectType(e) {
    const key = e.currentTarget.dataset.key
    if (key) {
      this.setData({ selectedType: key })
    }
  },

  // 输入反馈内容
  onContentInput(e) {
    this.setData({ content: e.detail.value })
  },

  // 提交反馈
  submitFeedback() {
    const { content, selectedType, submitting, openid } = this.data

    if (!openid) {
      wx.showToast({ title: '请先登录后再提交反馈', icon: 'none' })
      return
    }

    if (!content || !content.trim()) {
      wx.showToast({ title: '请输入反馈内容', icon: 'none' })
      return
    }

    if (submitting) return

    this.setData({ submitting: true })

    wx.showLoading({ title: '提交中...' })

    api.submitFeedback(content, selectedType, this.data.openid).then(res => {
      wx.hideLoading()
      if (res.success) {
        wx.showToast({ title: '反馈已提交', icon: 'success' })
        // 清空表单
        this.setData({
          content: '',
          selectedType: 'suggestion'
        })
        setTimeout(() => {
          wx.redirectTo({ url: '/pages/index/index' })
        }, 1500)
      } else {
        wx.showToast({ title: res.message || '提交失败', icon: 'none' })
        this.setData({ submitting: false })
      }
    }).catch(err => {
      wx.hideLoading()
      wx.showToast({ title: '提交失败', icon: 'none' })
      this.setData({ submitting: false })
    })
  }
})
