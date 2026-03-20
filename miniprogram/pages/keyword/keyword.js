// pages/keyword/keyword.js
const API_BASE = 'https://magic-rules-assistant-0a1904c329.tcb.qcloud.la'

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
    relatedRules: []
  },

  onLoad(options) {
    if (options.keyword) {
      this.setData({
        keyword: decodeURIComponent(options.keyword)
      })
      this.onSearch()
    }
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

    wx.request({
      url: `${API_BASE}/wechat/api/search`,
      data: { q: keyword },
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.results) {
          const results = res.data.results
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
      },
      fail: (err) => {
        console.error('搜索失败:', err)
        this.setData({
          searching: false,
          searchDone: true
        })
        wx.showToast({
          title: '搜索失败',
          icon: 'none'
        })
      }
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

    wx.request({
      url: `${API_BASE}/wechat/api/keyword`,
      data: { k: keyword },
      method: 'GET',
      success: (res) => {
        wx.hideLoading()

        if (res.statusCode === 200 && res.data && res.data.result) {
          const result = res.data.result
          this.setData({
            keywordDetail: result
          })

          // 获取相关规则
          this.fetchRelatedRules(keyword)
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('获取关键词详情失败:', err)
      }
    })
  },

  // 获取相关规则
  fetchRelatedRules(keyword) {
    wx.request({
      url: `${API_BASE}/wechat/api/search`,
      data: { q: keyword },
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.results) {
          const rules = res.data.results.rules || []
          // 取前5条相关规则
          this.setData({
            relatedRules: rules.slice(0, 5)
          })
        }
      },
      fail: (err) => {
        console.error('获取相关规则失败:', err)
      }
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
