// pages/search/search.js
const app = getApp()

// API 配置
const API_BASE = 'https://magic-rules-assistant-0a1904c329.service.tcloudbase.com'

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

    // 调用后端API搜索
    this.performSearch(keyword)
  },

  // 调用后端API搜索
  performSearch(keyword) {
    wx.request({
      url: `${API_BASE}/wechat/api/search`,
      data: { q: keyword },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          const results = res.data.results || {}
          this.setData({
            loading: false,
            searchDone: true,
            ruleResults: results.rules || [],
            keywordResults: results.keyword_abilities || [],
            cardResults: results.cards || [],
            results: res.data.results
          })
        } else {
          this.setData({
            loading: false,
            searchDone: true
          })
        }
      },
      fail: (err) => {
        console.error('搜索失败:', err)
        this.setData({
          loading: false,
          searchDone: true
        })
        wx.showToast({
          title: '搜索失败',
          icon: 'none'
        })
      }
    })
  },

  // 切换搜索类型
  switchType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ currentType: type })
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
