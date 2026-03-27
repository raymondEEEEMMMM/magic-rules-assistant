// pages/keyword/keyword.js
const app = getApp()

// 引入 API 工具
const api = require('../../utils/api')

Page({
  data: {
    keyword: '',
    searching: false,
    searchDone: false,
    keywordResults: [],
    ruleResults: [],
    commonKeywords: [
      'Flying', 'Trample', 'Deathtouch', 'First Strike', 'Lifelink',
      'Haste', 'Vigilance', 'Reach', 'Hexproof', 'Indestructible',
      'Menace', 'Double Strike', 'Flash', 'Ward', 'Protection'
    ],
    showDetail: false,
    currentKeyword: '',
    keywordDetail: null,
    relatedRules: [],
    isLightTheme: true
  },

  onLoad(options) {
    console.log('CODEBUDDY_DEBUG keyword onLoad options=', options)
    this.setData({ isLightTheme: true })
    if (options.keyword) {
      console.log('CODEBUDDY_DEBUG keyword onLoad keyword found, searching')
      this.setData({
        keyword: decodeURIComponent(options.keyword)
      })
      this.onSearch()
    } else {
      console.log('CODEBUDDY_DEBUG keyword onLoad no keyword parameter')
    }
    console.log('CODEBUDDY_DEBUG keyword onLoad completed')
  },

  onShow() {
    this.setData({ isLightTheme: true })
  },

  // 返回
  goBack() {
    wx.redirectTo({
      url: '/pages/index/index'
    })
  },

  onInput(e) {
    this.setData({
      keyword: e.detail.value
    })
  },

  clearSearch() {
    this.setData({
      keyword: '',
      keywordResults: [],
      ruleResults: [],
      searchDone: false
    })
  },

  onSearch() {
    const keyword = this.data.keyword.trim()
    if (!keyword) return

    this.setData({
      searching: true,
      searchDone: false
    })

    api.searchRules(keyword).then(res => {
      if (res && res.results) {
        const results = res.results
        this.setData({
          searching: false,
          searchDone: true,
          keywordResults: results.keyword_abilities || [],
          ruleResults: results.rules || []
        })
      } else {
        this.setData({
          searching: false,
          searchDone: true,
          keywordResults: [],
          ruleResults: []
        })
      }
    }).catch(err => {
      console.error('搜索失败:', err)
      this.setData({
        searching: false,
        searchDone: true
      })
      wx.showToast({
        title: '搜索失败',
        icon: 'none'
      })
    })
  },

  // 点击热门关键词
  searchKeyword(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
    this.onSearch()
  },

  // 查看关键词详情
  viewKeywordDetail(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({
      currentKeyword: keyword,
      showDetail: true,
      keywordDetail: null,
      relatedRules: []
    })

    // 获取关键词详情
    this.fetchKeywordDetail(keyword)
  },

  // 获取关键词详情
  fetchKeywordDetail(keyword) {
    wx.showLoading({ title: '加载中...' })

    api.getKeyword(keyword).then(res => {
      wx.hideLoading()

      if (res && res.result) {
        const result = res.result
        this.setData({
          keywordDetail: result
        })

        // 获取相关规则
        this.fetchRelatedRules(keyword)
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('获取关键词详情失败:', err)
    })
  },

  // 获取相关规则
  fetchRelatedRules(keyword) {
    api.searchRules(keyword).then(res => {
      if (res && res.results) {
        const rules = res.results.rules || []
        // 取前5条相关规则
        this.setData({
          relatedRules: rules.slice(0, 5)
        })
      }
    }).catch(err => {
      console.error('获取相关规则失败:', err)
    })
  },

  closeDetail() {
    this.setData({
      showDetail: false
    })
  },

  preventClose() {
    // 阻止关闭
  }
})
