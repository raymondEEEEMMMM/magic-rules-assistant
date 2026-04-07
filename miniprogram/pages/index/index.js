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
    searchDone: false,
    latestSets: [],
    sldGroups: [],
    showSldSection: false
  },

  onLoad() {
    console.log('CODEBUDDY_DEBUG index onLoad started')
    this.setData({
      version: app.version || '1.0.0',
      isLightTheme: app.globalData.isLightTheme
    })
    console.log('CODEBUDDY_DEBUG index setData version=', this.data.version, 'isLightTheme=', this.data.isLightTheme)
    this.loadHistory()
    this.fetchLatestSets()
    this.fetchSecretLair()
  },

  onShow() {
    console.log('CODEBUDDY_DEBUG index onShow isLightTheme=', app.globalData.isLightTheme)
    this.setData({
      isLightTheme: app.globalData.isLightTheme
    })
    console.log('CODEBUDDY_DEBUG index onShow completed')
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
    console.log('CODEBUDDY_DEBUG index loadHistory historyLength=', history.length, 'history=', history)
    this.setData({ history })
    console.log('CODEBUDDY_DEBUG index loadHistory setData completed')
  },

  // 获取最新系列资讯
  fetchLatestSets() {
    api.request('/api/mtgch/sets', {}).then(sets => {
      if (!sets || !Array.isArray(sets)) return
      // 过滤 token 系列，按发行日期降序排列
      const latest = sets
        .filter(s => s.set_type !== 'token')
        .sort((a, b) => new Date(b.released_at) - new Date(a.released_at))
        .slice(0, 10)
        .map(s => ({
          name: s.translated_name || s.name,
          code: s.code,
          iconUrl: s.icon_svg_uri,
          releasedAt: s.released_at
        }))
      this.setData({ latestSets: latest })
    }).catch(err => {
      console.error('获取最新系列失败:', err)
    })
  },

  // 获取 Secret Lair 资讯
  fetchSecretLair() {
    api.getSecretLairCards(3).then(res => {
      if (res && res.groups) {
        const recentGroups = res.groups.slice(0, 6)
        this.setData({ sldGroups: recentGroups, showSldSection: recentGroups.length > 0 })
      }
    }).catch(err => {
      console.error('获取Secret Lair失败:', err)
    })
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
    console.log('CODEBUDDY_DEBUG index viewRuleDetail called ruleNumber=', ruleNumber)
    if (!ruleNumber) {
      wx.showToast({ title: '规则编号为空', icon: 'none' })
      return
    }
    const url = `/pages/rule/rule?rule=${encodeURIComponent(ruleNumber)}`
    console.log('CODEBUDDY_DEBUG index viewRuleDetail url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG index viewRuleDetail success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index viewRuleDetail fail err=', err)
    })
  },

  // 查看关键词详情
  viewKeywordDetail(e) {
    const keyword = e.currentTarget.dataset.keyword
    console.log('CODEBUDDY_DEBUG index viewKeywordDetail called keyword=', keyword)
    const url = `/pages/keyword/keyword?keyword=${encodeURIComponent(keyword)}`
    console.log('CODEBUDDY_DEBUG index viewKeywordDetail url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG index viewKeywordDetail success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index viewKeywordDetail fail err=', err)
    })
  },

  // 查看卡牌详情
  viewCardDetail(e) {
    const cardId = e.currentTarget.dataset.id
    console.log('CODEBUDDY_DEBUG index viewCardDetail called cardId=', cardId)
    if (!cardId) return
    const url = `/pages/card/card?id=${encodeURIComponent(cardId)}`
    console.log('CODEBUDDY_DEBUG index viewCardDetail url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG index viewCardDetail success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index viewCardDetail fail err=', err)
    })
  },

  // 查看系列卡牌列表
  viewSetCards(e) {
    const setCode = e.currentTarget.dataset.code
    const setName = e.currentTarget.dataset.name
    console.log('CODEBUDDY_DEBUG index viewSetCards called setCode=', setCode, 'setName=', setName)
    if (!setCode) return
    const url = `/pages/setcards/setcards?setCode=${encodeURIComponent(setCode)}&setName=${encodeURIComponent(setName)}`
    console.log('CODEBUDDY_DEBUG index viewSetCards url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG index viewSetCards success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index viewSetCards fail err=', err)
    })
  },

  // 跳转 AI 裁判页面
  goToAIJudge() {
    console.log('CODEBUDDY_DEBUG index goToAIJudge called url=/pages/agent/agent')
    wx.navigateTo({
      url: '/pages/agent/agent',
      success: () => console.log('CODEBUDDY_DEBUG index goToAIJudge success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index goToAIJudge fail err=', err)
    })
  },

  // 跳转生命值计数器页面
  goToCounter() {
    console.log('CODEBUDDY_DEBUG index goToCounter called url=/pages/counter/counter')
    wx.navigateTo({
      url: '/pages/counter/counter',
      success: () => console.log('CODEBUDDY_DEBUG index goToCounter success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index goToCounter fail err=', err)
    })
  },

  // 跳转反馈页面
  goToFeedback() {
    console.log('CODEBUDDY_DEBUG index goToFeedback called url=/pages/feedback/feedback')
    wx.navigateTo({
      url: '/pages/feedback/feedback',
      success: () => console.log('CODEBUDDY_DEBUG index goToFeedback success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index goToFeedback fail err=', err)
    })
  },

  // 跳转 Secret Lair 专区页面
  goToSldCards() {
    console.log('CODEBUDDY_DEBUG index goToSldCards called url=/pages/sldcards/sldcards')
    wx.navigateTo({
      url: '/pages/sldcards/sldcards',
      success: () => console.log('CODEBUDDY_DEBUG index goToSldCards success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index goToSldCards fail err=', err)
    })
  },

  // 跳转 API 测试页面
  goToAPITest() {
    console.log('CODEBUDDY_DEBUG index goToAPITest called url=/pages/apitest/apitest')
    wx.navigateTo({
      url: '/pages/apitest/apitest',
      success: () => console.log('CODEBUDDY_DEBUG index goToAPITest success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index goToAPITest fail err=', err)
    })
  }
})
