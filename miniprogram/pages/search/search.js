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
    searchFocused: true,
    useRealApi: false  // 是否使用真实API
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

    // 根据配置选择使用真实API或本地模拟
    if (this.data.useRealApi) {
      this.performRealSearch(keyword)
    } else {
      this.performLocalSearch(keyword)
    }
  },

  // 真实API搜索 - 使用云调用
  performRealSearch(keyword) {
    if (app.globalData.useCloudCall) {
      // 使用 wx.cloud.callFunction 调用云函数
      wx.cloud.callFunction({
        name: 'mtgAsk',
        data: {
          httpMethod: 'GET',
          path: '/api/search',
          queryString: `q=${encodeURIComponent(keyword)}`
        },
        success: (res) => {
          if (res.result && res.result.body) {
            const data = typeof res.result.body === 'string'
              ? JSON.parse(res.result.body)
              : res.result
            const results = data.results || {}
            this.setData({
              loading: false,
              searchDone: true,
              ruleResults: results.rules || [],
              keywordResults: results.keyword_abilities || [],
              cardResults: results.cards || [],
              results: [
                ...(results.rules || []),
                ...(results.keyword_abilities || []),
                ...(results.cards || [])
              ]
            })
          } else {
            this.setData({ loading: false, searchDone: true })
          }
        },
        fail: (err) => {
          this.setData({ loading: false, searchDone: true })
          wx.showToast({ title: '调用失败', icon: 'none' })
        }
      })
    } else {
      // 使用 HTTP 请求
      const apiBase = app.globalData.apiBase
      wx.request({
        url: `${apiBase}/api/search`,
        data: { q: keyword },
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200 && res.data) {
            const results = res.data.results || {}
            this.setData({
              loading: false,
              searchDone: true,
              ruleResults: results.rules || [],
              keywordResults: results.keyword_abilities || [],
              cardResults: results.cards || [],
              results: [
                ...(results.rules || []),
                ...(results.keyword_abilities || []),
                ...(results.cards || [])
              ]
            })
          } else {
            this.setData({ loading: false, searchDone: true })
            wx.showToast({ title: '搜索失败', icon: 'none' })
          }
        },
        fail: () => {
          this.setData({ loading: false, searchDone: true })
          wx.showToast({ title: '网络请求失败', icon: 'none' })
        }
      })
    }
  },

  // 本地搜索实现
  performLocalSearch(keyword) {
    setTimeout(() => {
      const results = this.getMockResults(keyword)

      this.setData({
        loading: false,
        searchDone: true,
        ruleResults: results.rules,
        keywordResults: results.keywords,
        cardResults: results.cards,
        results: [...results.rules, ...results.keywords, ...results.cards]
      })
    }, 300)
  },

  // 获取模拟结果
  getMockResults(keyword) {
    const mockRules = [
      {
        title: '优先权',
        content: '优先权是玩家获得施放咒语或启动异能的机会。当玩家获得优先权时，他们可以选择施放咒语、启动异能或让过优先权。',
        category: '基础规则'
      },
      {
        title: '战斗阶段',
        content: '战斗阶段包括开始战斗步骤、宣告攻击者步骤、宣告阻挡者步骤、战斗伤害步骤和结束战斗步骤。',
        category: '回合结构'
      },
      {
        title: '瞬间时机',
        content: '瞬间可以在你获得优先权的几乎任何时候施放，包括在对手的回合中。',
        category: '优先权'
      }
    ]

    const mockKeywords = [
      {
        name: '飞行',
        description: '具有飞行的生物只能被其他具有飞行或延势的生物阻挡。'
      },
      {
        name: '死触',
        description: '具有死触的任何生物只要对另一个生物造成大于0的伤害，就会造成等量的伤害。'
      },
      {
        name: '警戒',
        description: '警戒可以让生物在攻击时不会横置，并且在攻击者步骤后仍能阻挡。'
      }
    ]

    const mockCards = [
      {
        name: '黑绿霸主',
        manaCost: '{2}{B}{G}',
        type: '生物 — 霸主',
        text: '当黑绿霸主进入战场时，你可以从你的牌库中寻找一张沼泽牌或森林牌，将其横置放进战场，然后将你的牌库洗牌。',
        power: '4',
        toughness: '4'
      },
      {
        name: '红蓝法师',
        manaCost: '{U}{R}',
        type: '生物 — 人类 法师',
        text: '飞行\n每当红蓝法师成为咒语或异能的目标时，你可以掷硬币。如果是正面，反击该咒语或异能。',
        power: '2',
        toughness: '2'
      }
    ]

    // 根据关键词过滤
    const filterResults = (array, key) => {
      return array.filter(item => 
        (item.name || item.title || '').toLowerCase().includes(keyword.toLowerCase()) ||
        (item.description || item.content || '').toLowerCase().includes(keyword.toLowerCase())
      )
    }

    return {
      rules: filterResults(mockRules, keyword),
      keywords: filterResults(mockKeywords, keyword),
      cards: filterResults(mockCards, keyword)
    }
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
