// pages/search/search.js
const app = getApp()

Page({
  data: {
    keyword: '',
    currentType: 'all',
    results: [],
    ruleResults: [],
    keywordResults: [],
    cardResults: [],
    history: [],
    loading: false,
    searchDone: false,
    searchFocused: true
  },

  onLoad() {
    this.loadHistory()
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
      searchDone: false 
    })

    // 保存到历史
    this.saveToHistory(keyword)

    // 并行请求所有搜索
    const promises = []
    
    if (this.data.currentType === 'all' || this.data.currentType === 'rule') {
      promises.push(
        app.requestApi('/api/search', { q: keyword })
          .then(res => res.results?.rules || [])
          .catch(() => [])
      )
    }

    if (this.data.currentType === 'all' || this.data.currentType === 'keyword') {
      promises.push(
        app.requestApi('/api/keyword', { k: keyword })
          .then(res => res.result ? [res.result] : [])
          .catch(() => [])
      )
    }

    if (this.data.currentType === 'all' || this.data.currentType === 'card') {
      promises.push(
        app.requestApi('/api/card', { q: keyword, page_size: 10 })
          .then(res => res.items || [])
          .catch(() => [])
      )
    }

    Promise.all(promises)
      .then(([rules, keywords, cards]) => {
        this.setData({
          loading: false,
          searchDone: true,
          ruleResults: rules,
          keywordResults: keywords,
          cardResults: cards,
          results: [...rules, ...keywords, ...cards]
        })
      })
      .catch(() => {
        this.setData({
          loading: false,
          searchDone: true
        })
      })
  },

  // 切换搜索类型
  switchType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ currentType: type })
    
    if (this.data.keyword) {
      this.onSearch()
    }
  },

  // 保存到历史
  saveToHistory(keyword) {
    let history = this.data.history
    history = history.filter(item => item !== keyword)
    history.unshift(keyword)
    history = history.slice(0, 10) // 最多保留10条
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
      results: [],
      searchDone: false,
      searchFocused: true
    })
  },

  // 查看关键词详情
  viewKeywordDetail(e) {
    const keyword = e.currentTarget.dataset.keyword
    wx.navigateTo({
      url: `/pages/keyword/keyword?keyword=${encodeURIComponent(keyword)}`
    })
  }
})
