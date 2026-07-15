// pages/sldcards/sldcards.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    isLightTheme: true,
    loading: false,
    loaded: false,
    // 按日期分组的卡牌
    groups: [],
    // 当前展开的日期
    expandedDates: [],
    // 所有日期（用于展开/收起）
    allDates: []
  },

  onLoad(options) {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
    this.loadSldCards()
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 更新主题（由 app.js 调用）
  updateTheme(isLight) {
    this.setData({ isLightTheme: isLight })
  },

  // 返回
  goBack() {
    wx.navigateBack({ fail: () => wx.redirectTo({ url: '/pages/index/index' }) })
  },

  goToIndex() {
    wx.navigateBack({
      fail: () => wx.switchTab({ url: '/pages/index/index' })
    })
  },

  // 加载 SLD 卡牌（默认12个月）
  loadSldCards() {
    this.setData({ loading: true })

    api.getSecretLairCards(6).then(res => {

      // groups 已经是按日期分组的结构
      const groups = res.groups || []
      const allDates = groups.map(g => g.date)

      // 默认展开所有日期
      this.setData({
        groups,
        allDates,
        expandedDates: allDates,
        loading: false,
        loaded: true
      })
    }).catch(err => {
      this.setData({
        loading: false,
        loaded: true
      })
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    })
  },

  // 展开/收起日期组
  toggleDateGroup(e) {
    const date = e.currentTarget.dataset.date
    const { expandedDates } = this.data

    if (expandedDates.includes(date)) {
      this.setData({
        expandedDates: expandedDates.filter(d => d !== date)
      })
    } else {
      this.setData({
        expandedDates: [...expandedDates, date]
      })
    }
  },

  // 查看卡牌详情
  viewCardDetail(e) {
    const cardId = e.currentTarget.dataset.id
    if (!cardId) return
    const url = `/pages/card/card?id=${encodeURIComponent(cardId)}`
    wx.navigateTo({ url })
  },

  // 新版 WXML 调用
  onCardTap(e) {
    this.viewCardDetail(e)
  }
})
