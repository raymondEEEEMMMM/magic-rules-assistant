// pages/search/search.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    keyword: '',
    combinedResults: {
      keywords: [],
      cards: [],
      rules: []
    },
    history: [],
    loading: false,
    searchDone: false,
    searchFocused: true,
    isLightTheme: true,
    // 各个分类的加载状态
    keywordsLoading: false,
    cardsLoading: false,
    rulesLoading: false,
    // 系列筛选
    setCode: '',
    setName: ''
  },

  onLoad(options) {
    this.loadHistory()
    this.setData({ isLightTheme: true })
    // 如果有 setCode 参数，自动加载系列卡牌
    if (options.setCode) {
      this.setData({
        setCode: options.setCode,
        setName: options.setName || ''
      })
      this.loadSetCards()
    }
  },

  onShow() {
    this.setData({ isLightTheme: app.globalData.isLightTheme })
  },

  // 返回
  goBack() {
    console.log('CODEBUDDY_DEBUG search goBack called')
    wx.navigateBack({
      success: () => console.log('CODEBUDDY_DEBUG search goBack success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG search goBack fail err=', err)
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
      loading: true,
      searchDone: false,
      keywordsLoading: true,
      cardsLoading: true,
      rulesLoading: true,
      combinedResults: {
        keywords: [],
        cards: [],
        rules: []
      }
    })

    // 保存到历史
    this.saveToHistory(keyword)

    // 分别查询，不等待全部完成
    this.searchKeywordSync(keyword).then(res => {
      this.setData({
        'combinedResults.keywords': res || [],
        keywordsLoading: false
      })
      this.checkAllLoaded()
    })

    this.searchCardSync(keyword).then(res => {
      this.setData({
        'combinedResults.cards': res || [],
        cardsLoading: false
      })
      this.checkAllLoaded()
    })

    this.searchRulesSync(keyword).then(res => {
      this.setData({
        'combinedResults.rules': res || [],
        rulesLoading: false
      })
      this.checkAllLoaded()
    })
  },

  // 检查是否所有分类都已加载完成
  checkAllLoaded() {
    const { keywordsLoading, cardsLoading, rulesLoading } = this.data
    if (!keywordsLoading && !cardsLoading && !rulesLoading) {
      this.setData({
        loading: false,
        searchDone: true
      })
    }
  },

  // 加载系列卡牌
  loadSetCards() {
    const { setCode } = this.data
    if (!setCode) return
    this.setData({
      cardsLoading: true,
      loading: true
    })
    api.getSetCards(setCode).then(res => {
      this.setData({
        'combinedResults.cards': res.items || [],
        cardsLoading: false,
        loading: false,
        searchDone: true
      })
    }).catch(err => {
      console.error('CODEBUDDY_DEBUG search loadSetCards error', err)
      this.setData({
        cardsLoading: false,
        loading: false,
        searchDone: true
      })
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
    return api.searchCard(keyword, 1, 5).then(res => {
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
      searchDone: false,
      searchFocused: true
    })
  },

  // 查看规则详情
  viewRuleDetail(e) {
    const ruleNumber = e.currentTarget.dataset.rule
    console.log('CODEBUDDY_DEBUG search viewRuleDetail called ruleNumber=', ruleNumber)
    if (!ruleNumber) {
      wx.showToast({ title: '规则编号为空', icon: 'none' })
      return
    }
    const url = `/pages/rule/rule?rule=${encodeURIComponent(ruleNumber)}`
    console.log('CODEBUDDY_DEBUG search viewRuleDetail url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG search viewRuleDetail success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG search viewRuleDetail fail err=', err)
    })
  },

  // 查看关键词详情
  viewKeywordDetail(e) {
    const keyword = e.currentTarget.dataset.keyword
    console.log('CODEBUDDY_DEBUG search viewKeywordDetail called keyword=', keyword)
    const url = `/pages/keyword/keyword?keyword=${encodeURIComponent(keyword)}`
    console.log('CODEBUDDY_DEBUG search viewKeywordDetail url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG search viewKeywordDetail success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG search viewKeywordDetail fail err=', err)
    })
  },

  // 查看卡牌详情
  viewCardDetail(e) {
    const cardId = e.currentTarget.dataset.id
    console.log('CODEBUDDY_DEBUG search viewCardDetail called cardId=', cardId)
    if (!cardId) return
    const url = `/pages/card/card?id=${encodeURIComponent(cardId)}`
    console.log('CODEBUDDY_DEBUG search viewCardDetail url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG search viewCardDetail success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG search viewCardDetail fail err=', err)
    })
  },

  // 查看更多卡牌（跳转卡牌搜索页）
  viewMoreCards(e) {
    const keyword = e.currentTarget.dataset.keyword
    console.log('CODEBUDDY_DEBUG search viewMoreCards keyword=', keyword)
    if (!keyword) return
    const url = `/pages/card/card?id=${encodeURIComponent(keyword)}`
    console.log('CODEBUDDY_DEBUG search viewMoreCards url=', url)
    wx.navigateTo({
      url,
      success: () => console.log('CODEBUDDY_DEBUG search viewMoreCards success'),
      fail: (err) => console.log('CODEBUDDY_DEBUG search viewMoreCards fail err=', err)
    })
  },

  // 去除 HTML 标签
  stripHtml(html) {
    return html.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').trim()
  }
})