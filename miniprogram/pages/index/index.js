// pages/index/index.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    version: '',
    isLightTheme: true,
    keyword: '',
    combinedResults: {
      keywords: [],
      cards: [],
      rules: []
    },
    history: [],
    searchDone: false
  },

  onLoad() {
    this.setData({
      version: app.version || '1.0.0',
      isLightTheme: app.globalData.isLightTheme
    })
    this.loadHistory()
  },

  onShow() {
    this.setData({
      isLightTheme: app.globalData.isLightTheme
    })
  },

  // 更新主题（由 app.js 调用）
  updateTheme(isLight) {
    this.setData({
      isLightTheme: isLight
    })
  },

  // 切换主题
  toggleTheme() {
    const newTheme = app.toggleTheme()
    this.setData({
      isLightTheme: newTheme
    })
  },

  // 加载搜索历史
  loadHistory() {
    const history = wx.getStorageSync('searchHistory') || []
    this.setData({ history })
  },

  // 输入监听
  onInput(e) {
    this.setData({
      keyword: e.detail.value,
      searchDone: false
    })
  },

  // 执行搜索
  onSearch() {
    const keyword = this.data.keyword.trim()
    if (!keyword) return

    this.setData({
      searchDone: false
    })

    // 保存到历史
    this.saveToHistory(keyword)

    // 组合查询：同时查询所有分类
    Promise.all([
      this.searchKeywordSync(keyword),
      this.searchCardSync(keyword),
      this.searchRulesSync(keyword)
    ]).then(([keywords, cards, rules]) => {
      this.setData({
        searchDone: true,
        combinedResults: {
          keywords: keywords || [],
          cards: cards || [],
          rules: rules || []
        }
      })
    }).catch(err => {
      console.error('组合查询失败:', err)
      this.setData({ searchDone: true })
    })
  },

  // 同步查询关键词
  searchKeywordSync(keyword) {
    const enKeyword = api.getCnKeyword(keyword)
    return api.getKeyword(enKeyword).then(res => {
      return res.result ? [res.result] : []
    }).catch(() => [])
  },

  // 同步查询卡牌
  searchCardSync(keyword) {
    return api.searchCard(keyword, 1, 3).then(res => {
      return res.results || res.items || []
    }).catch(() => [])
  },

  // 同步查询规则
  searchRulesSync(keyword) {
    return api.searchRules(keyword).then(res => {
      return (res.results || []).rules || []
    }).catch(() => [])
  },

  // 保存到历史
  saveToHistory(keyword) {
    let history = this.data.history
    history = history.filter(item => item !== keyword)
    history.unshift(keyword)
    history = history.slice(0, 10)
    wx.setStorageSync('searchHistory', history)
    this.setData({ history })
  },

  // 使用历史记录
  useHistory(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
    this.onSearch()
  },

  // 清空历史
  clearHistory() {
    wx.removeStorageSync('searchHistory')
    this.setData({ history: [] })
  },

  // 清空搜索
  clearSearch() {
    this.setData({
      keyword: '',
      combinedResults: { keywords: [], cards: [], rules: [] },
      searchDone: false
    })
  },

  // 查看规则详情
  viewRuleDetail(e) {
    const ruleNumber = e.currentTarget.dataset.rule
    if (!ruleNumber) {
      wx.showToast({ title: '规则编号为空', icon: 'none' })
      return
    }
    wx.navigateTo({
      url: `/pages/rule/rule?rule=${encodeURIComponent(ruleNumber)}`
    })
  },

  // 查看关键词详情
  viewKeywordDetail(e) {
    const keyword = e.currentTarget.dataset.keyword
    wx.navigateTo({
      url: `/pages/keyword/keyword?keyword=${encodeURIComponent(keyword)}`
    })
  },

  // 查看卡牌详情
  viewCardDetail(e) {
    const cardId = e.currentTarget.dataset.id
    if (!cardId) return
    wx.navigateTo({
      url: `/pages/card/card?id=${encodeURIComponent(cardId)}`
    })
  },

  // 跳转 AI 裁判页面
  goToAIJudge() {
    wx.navigateTo({
      url: '/pages/agent/agent'
    })
  },

  // 跳转 API 测试页面
  goToAPITest() {
    wx.navigateTo({
      url: '/pages/apitest/apitest'
    })
  }
})
