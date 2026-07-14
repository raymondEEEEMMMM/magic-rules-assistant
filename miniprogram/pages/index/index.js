// pages/index/index.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

// 引入 SVG 图标 helper（用于工具列表图标）
const iconUtil = require('../../utils/icon.js')

Page({
  data: {
    version: '',
    isLightTheme: true,
    showAIJudgeCard: false,
    keyword: '',
    combinedResults: {
      keywords: [],
      cards: [],
      rules: []
    },
    hasMoreCards: false,
    hasMoreRules: false,
    history: [],
    searchDone: false,
    latestSets: [],
    sldGroups: [],
    showSldSection: false,
    hiddenCards: {}
  },

  onLoad() {
    this.setData({
      version: app.version || '1.0.0',
      isLightTheme: app.globalData.isLightTheme,
      showAIJudgeCard: app.globalData.showAIJudgeCard
    })
    this.loadHistory()
    this.fetchLatestSets()
    this.fetchSecretLair()
    this.fetchHomepageCards()
    this.setData({
      toolIcons: {
        token: iconUtil.getDataUrl('card', { color: '#ffffff' }),
        deck: iconUtil.getDataUrl('book', { color: '#ffffff' }),
        heart: iconUtil.getDataUrl('heart', { color: '#ffffff' }),
        dice: iconUtil.getDataUrl('dice', { color: '#ffffff' }),
        chevron: iconUtil.getDataUrl('chevron-right')
      }
    })
  },

  onShow() {
    this.setData({
      isLightTheme: app.globalData.isLightTheme,
      showAIJudgeCard: app.globalData.showAIJudgeCard
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

  // 获取首页卡片配置
  fetchHomepageCards() {
    api.request('/api/homepage/cards', {}).then(res => {
      if (res && res.cards) {
        // 转换为 {aiJudge: true, token: false, ...} 格式
        const hiddenCards = {}
        res.cards.forEach(card => {
          // card_key 格式为 snake_case，转换为 camelCase
          const key = card.card_key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
          hiddenCards[key] = card.hidden
        })
        this.setData({ hiddenCards })
      }
    }).catch(err => {
      console.error('获取首页卡片配置失败:', err)
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
    ]).then(([keywords, cardResult, ruleResult]) => {
      this.setData({
        searchDone: true,
        combinedResults: {
          keywords: keywords || [],
          cards: cardResult?.items || [],
          rules: ruleResult?.rules || []
        },
        hasMoreCards: cardResult?.hasMore || false,
        hasMoreRules: ruleResult?.hasMore || false
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
    return api.searchCard(keyword, 1, 6).then(res => {
      const items = res.results || res.items || []
      const hasMore = res.has_more === true || (res.total_cards > 5 && items.length >= 5)
      return { items: items.slice(0, 5), hasMore }
    }).catch(() => ({ items: [], hasMore: false }))
  },

  // 同步查询规则
  searchRulesSync(keyword) {
    return api.searchRules(keyword).then(res => {
      const rules = (res.results || []).rules || []
      return { rules: rules.slice(0, 5), hasMore: rules.length >= 5 }
    }).catch(() => ({ rules: [], hasMore: false }))
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
      hasMoreCards: false,
      hasMoreRules: false,
      searchDone: false
    })
  },

  // 查看更多结果
  goToMoreResults(e) {
    const type = e.currentTarget.dataset.type
    const keyword = this.data.keyword.trim()
    if (!keyword) return
    if (type === 'cards') {
      wx.navigateTo({ url: `/pages/search/search?keyword=${encodeURIComponent(keyword)}&tab=cards` })
    } else if (type === 'rules') {
      wx.navigateTo({ url: `/pages/search/search?keyword=${encodeURIComponent(keyword)}&tab=rules` })
    } else if (type === 'keywords') {
      wx.navigateTo({ url: `/pages/search/search?keyword=${encodeURIComponent(keyword)}&tab=keywords` })
    }
  },

  // 查看规则详情
  viewRuleDetail(e) {
    const ruleNumber = e.currentTarget.dataset.rule
    if (!ruleNumber) {
      wx.showToast({ title: '规则编号为空', icon: 'none' })
      return
    }
    const url = `/pages/rule/rule?rule=${encodeURIComponent(ruleNumber)}`
    wx.navigateTo({
      url,
    })
  },

  // 查看关键词详情
  viewKeywordDetail(e) {
    const keyword = e.currentTarget.dataset.keyword
    const url = `/pages/keyword/keyword?keyword=${encodeURIComponent(keyword)}`
    wx.navigateTo({
      url,
    })
  },

  // 查看卡牌详情
  viewCardDetail(e) {
    const cardId = e.currentTarget.dataset.id
    if (!cardId) return
    const url = `/pages/card/card?id=${encodeURIComponent(cardId)}`
    wx.navigateTo({
      url,
    })
  },

  // 查看更多卡牌（跳转卡牌搜索页）
  viewMoreCards(e) {
    const keyword = e.currentTarget.dataset.keyword
    console.log('CODEBUDDY_DEBUG index viewMoreCards keyword=', keyword)
    if (!keyword) return
    const url = `/pages/card/card?id=${encodeURIComponent(keyword)}`
    console.log('CODEBUDDY_DEBUG index viewMoreCards url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG index viewMoreCards success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG index viewMoreCards fail err=', err)
    })
  },

  // 查看系列卡牌列表
  viewSetCards(e) {
    const setCode = e.currentTarget.dataset.code
    const setName = e.currentTarget.dataset.name
    if (!setCode) return
    const url = `/pages/setcards/setcards?setCode=${encodeURIComponent(setCode)}&setName=${encodeURIComponent(setName)}`
    wx.navigateTo({
      url,
    })
  },

  // 跳转 AI 裁判页面
  goToAIJudge() {
    wx.navigateTo({
      url: '/pages/agent/agent',
    })
  },

  // 跳转骰子 & 随机页面
  goToDice() {
    wx.navigateTo({
      url: '/pages/dice/dice',
    })
  },

  // 跳转 Token 生成器页面
  goToToken() {
    wx.navigateTo({
      url: '/pages/token/token',
    })
  },

  // 跳转我的套牌页面
  goToDecks() {
    wx.navigateTo({
      url: '/pages/decks/decks',
    })
  },

  // 跳转生命值计数器页面
  goToCounter() {
    wx.navigateTo({
      url: '/pages/counter/counter',
    })
  },

  // 跳转反馈页面
  goToFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback',
    })
  },

  // 跳转开发日志
  goToDevLog() {
    wx.navigateTo({
      url: '/pages/devlog/devlog',
    })
  },

  // 跳转 Promo 卡快讯页面
  goToPromos() {
    wx.navigateTo({
      url: '/pages/promos/promos',
    })
  },

  // 跳转 Secret Lair 专区页面
  goToSldCards() {
    wx.navigateTo({
      url: '/pages/sldcards/sldcards',
    })
  },

  // 跳转 API 测试页面
  goToAPITest() {
    wx.navigateTo({
      url: '/pages/apitest/apitest',
    })
  }
})
