// pages/sldcards/sldcards.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    isLightTheme: true,
    loading: false,
    loaded: false,
    viewMode: 'image', // 'image' or 'text'
    // 按日期分组的卡牌
    groups: [],
    // 当前展开的日期
    expandedDates: [],
    // 所有日期（用于展开/收起）
    allDates: [],
    // 搜索
    searchCode: '',
    searchResult: null,
    searchNotFound: false,
    // 筛选月份（搜索后用于只显示对应月份）
    filteredMonth: ''
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

  // 搜索输入
  onSearchInput(e) {
    this.setData({
      searchCode: e.detail.value,
      searchResult: null,
      searchNotFound: false
    })
  },

  // 执行搜索
  onSearch() {
    const code = this.data.searchCode.trim()
    if (!code) return

    this.setData({ loading: true })

    api.searchSecretLair(code).then(res => {
      this.setData({ loading: false })

      if (res.found && res.card) {
        // 找到卡牌，展开对应月份并筛选显示
        const yearMonth = res.card.year_month
        const { groups, expandedDates } = this.data

        // 确保搜索结果对应的月份被展开
        if (!expandedDates.includes(yearMonth)) {
          this.setData({
            expandedDates: [...expandedDates, yearMonth]
          })
        }

        // 显示搜索结果摘要，并筛选只显示该月份
        this.setData({
          searchResult: {
            year_month: yearMonth,
            name: res.card.name,
            image_url: res.card.image_url,
            collector_number: res.card.collector_number,
            total: groups.find(g => g.date === yearMonth)?.cards.length || 1
          },
          searchNotFound: false,
          filteredMonth: yearMonth  // 筛选：只显示该月份
        })
      } else {
        this.setData({
          searchResult: null,
          searchNotFound: true,
          filteredMonth: ''  // 清除筛选
        })
      }
    }).catch(err => {
      this.setData({ loading: false })
      wx.showToast({
        title: '搜索失败',
        icon: 'none'
      })
    })
  },

  // 清除搜索
  clearSearch() {
    this.setData({
      searchCode: '',
      searchResult: null,
      searchNotFound: false,
      filteredMonth: ''
    })
  },

  // 切换视图模式
  toggleView() {
    this.setData({
      viewMode: this.data.viewMode === 'image' ? 'text' : 'image'
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
